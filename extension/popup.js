const api = typeof browser !== 'undefined' ? browser : chrome;

const btn     = document.getElementById('btn-export');
const btnDiag = document.getElementById('btn-diag');
const status  = document.getElementById('status');
const diagOut = document.getElementById('diag-output');

function setStatus(type, text) {
  status.className = `status ${type}`;
  status.textContent = text;
}

async function getTab() {
  const [tab] = await api.tabs.query({ active: true, currentWindow: true });
  return tab;
}

// Detect the frame that has the process table.
// Tries #fPP:processosTable first, then falls back to any table
// containing a process number pattern — handles any frame/ID variant.
const DETECTION_FUNC = () => {
  const PADRAO = /\d{7}-\d{2}\.\d{4}\.6\.\d{2,4}\.\d{4}/;
  if (document.querySelector('#fPP\\:processosTable')) return 'specific';
  if (document.querySelector('[id*="processosTable"]'))  return 'id-partial';
  const tables = [...document.querySelectorAll('table')];
  if (tables.some(t => PADRAO.test(t.innerText || '') && t.rows.length > 1)) return 'content';
  return null;
};

// Poll all frames until table appears (max timeoutMs).
async function encontrarFrame(tabId, timeoutMs = 20000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeoutMs) {
    const frames = await api.scripting.executeScript({
      target: { tabId, allFrames: true },
      func: DETECTION_FUNC,
    }).catch(() => []);

    const target = frames?.find(f => f.result !== null && f.result !== undefined);
    if (target) return target;

    await new Promise(r => setTimeout(r, 1000));
  }
  return null;
}

// ── Export ────────────────────────────────────────────────────────────────────

btn.addEventListener('click', async () => {
  btn.disabled = true;
  diagOut.style.display = 'none';
  setStatus('loading', 'Procurando tabela de processos...');

  try {
    const tab = await getTab();
    if (!tab?.id) { setStatus('error', 'Não foi possível identificar a aba ativa.'); return; }

    // Inject in all frames first
    await api.scripting.executeScript({
      target: { tabId: tab.id, allFrames: true },
      files: ['content.js'],
    }).catch(() => {});

    const targetFrame = await encontrarFrame(tab.id, 20000);
    if (!targetFrame) {
      setStatus('error', 'Tabela não encontrada. Execute a consulta no PJe e aguarde os resultados aparecerem antes de exportar.');
      return;
    }

    setStatus('loading', 'Extraindo processos de todas as páginas… acompanhe na página do PJe.');

    const response = await api.tabs.sendMessage(
      tab.id,
      { action: 'exportCSV' },
      { frameId: targetFrame.frameId }
    );

    if (response?.ok) {
      setStatus('success',
        `✓ ${response.rows} processo${response.rows !== 1 ? 's' : ''} exportado${response.rows !== 1 ? 's' : ''} em ${response.paginas} página${response.paginas !== 1 ? 's' : ''}.`
      );
    } else {
      setStatus('error', response?.error || 'Erro desconhecido.');
    }

  } catch (err) {
    const msg = err?.message || String(err);
    setStatus('error', msg.includes('Cannot establish connection') ? 'Abra o PJe TRE-CE antes de exportar.' : msg);
  } finally {
    btn.disabled = false;
  }
});

// ── Diagnostic ────────────────────────────────────────────────────────────────

btnDiag.addEventListener('click', async () => {
  btnDiag.disabled = true;
  diagOut.style.display = 'none';
  setStatus('loading', 'Coletando informações...');

  try {
    const tab = await getTab();
    if (!tab?.id) { setStatus('error', 'Aba não identificada.'); return; }

    const results = await api.scripting.executeScript({
      target: { tabId: tab.id, allFrames: true },
      func: () => {
        const PADRAO = /\d{7}-\d{2}\.\d{4}\.6\.\d{2,4}\.\d{4}/;
        const norm = s => (s || '').replace(/\s+/g, ' ').trim().slice(0, 60);
        const tables = [...document.querySelectorAll('table')].map(t => ({
          id: t.id || '(sem id)',
          rows: t.rows.length,
          temProcesso: PADRAO.test(t.innerText || ''),
          headers: [...(t.querySelector('thead tr, tr') || t)
            .querySelectorAll('th,td')].map(c => norm(c.innerText)).filter(Boolean).slice(0, 5),
        }));
        const iframes = [...document.querySelectorAll('iframe')].map(f => ({
          id: f.id || '(sem id)',
          src: (f.src || f.getAttribute('src') || '').slice(0, 100),
        }));

        // JSF/RichFaces paginator diagnostic
        const pag = document.getElementById('fPP:processosTable:scTabela_table');
        const pagBotoes = pag
          ? [...pag.querySelectorAll('td.rich-datascr-button')].map(td => ({
              txt: (td.innerText || td.textContent || '').trim(),
              cls: (td.className || '').slice(0, 80),
            }))
          : null;

        // Nó atual buttons diagnostic (first row only)
        const primeiraLinha = document.querySelector('#fPP\\:processosTable\\:tb tr, [id*="processosTable"] tbody tr');
        const btnNo = primeiraLinha ? primeiraLinha.querySelector('[id^="btnMostrarNos"]') : null;

        // Angular Material paginator diagnostic
        const matPag = document.querySelector('.mat-paginator, .mat-mdc-paginator');
        const genPag = document.querySelector('[class*="paginator"], [id*="paginator"], [class*="paginat"]');
        const matNextEl = document.querySelector(
          '.mat-paginator-navigation-next, .mat-mdc-paginator-navigation-next, ' +
          '[aria-label="Next page"], [aria-label="Próxima página"], [aria-label="Próxima"], ' +
          '[aria-label="Próxima pagina"]'
        );
        // All buttons — key info for debugging Angular paginators
        const todosOsBotoes = [...document.querySelectorAll('button')].map(b => ({
          txt: ((b.innerText || b.textContent || '').replace(/\s+/g,' ').trim()).slice(0, 25),
          aria: (b.getAttribute('aria-label') || '').slice(0, 50),
          cls: (b.className || '').slice(0, 60),
          dis: b.disabled || b.getAttribute('aria-disabled') === 'true',
        })).filter(b => b.txt || b.aria).slice(0, 25);

        return {
          url: location.href.slice(0, 100),
          hasPjeTable: !!document.querySelector('#fPP\\:processosTable'),
          temProcessoEmTabela: tables.some(t => t.temProcesso),
          tables: tables.slice(0, 15),
          iframes: iframes.slice(0, 10),
          paginador: pag ? { id: pag.id, botoes: pagBotoes } : null,
          btnMostrarNos: btnNo ? { id: btnNo.id, onclick: (btnNo.getAttribute('onclick') || '').slice(0, 100) } : null,
          matPaginador: matPag ? matPag.className.slice(0, 80) : (genPag ? `(generic) ${(genPag.className||genPag.id||'').slice(0,60)}` : null),
          matNext: matNextEl ? { aria: matNextEl.getAttribute('aria-label'), cls: matNextEl.className.slice(0,60), dis: matNextEl.disabled } : null,
          botoes: todosOsBotoes,
        };
      },
    });

    const lines = [];
    (results || []).forEach((r, i) => {
      if (!r?.result) return;
      const d = r.result;
      lines.push(`--- Frame ${i} (frameId: ${r.frameId}) ---`);
      lines.push(`URL: ${d.url}`);
      lines.push(`#fPP:processosTable: ${d.hasPjeTable} | tem nº processo em tabela: ${d.temProcessoEmTabela}`);
      if (d.paginador) {
        lines.push(`paginador JSF: id="${d.paginador.id}" | ${d.paginador.botoes?.length ?? 0} botão(ões) rich-datascr-button`);
        (d.paginador.botoes || []).forEach((b, j) => lines.push(`  [${j}] txt="${b.txt}" cls="${b.cls}"`));
      } else {
        lines.push('paginador JSF: NÃO ENCONTRADO');
      }
      if (d.matPaginador) {
        lines.push(`paginador Angular: ${d.matPaginador}`);
        if (d.matNext) {
          lines.push(`  next btn: aria="${d.matNext.aria}" cls="${d.matNext.cls}" disabled=${d.matNext.dis}`);
        } else {
          lines.push('  next btn: NÃO ENCONTRADO (mat-paginator-navigation-next / aria-label)');
        }
      } else {
        lines.push('paginador Angular: NÃO ENCONTRADO (.mat-paginator / [class*=paginator])');
      }
      if (d.btnMostrarNos) {
        lines.push(`btnMostrarNos: id="${d.btnMostrarNos.id}" | onclick="${d.btnMostrarNos.onclick}"`);
      } else {
        lines.push('btnMostrarNos: NÃO ENCONTRADO na primeira linha');
      }
      if (d.botoes?.length) {
        lines.push(`botões (${d.botoes.length}):`);
        d.botoes.forEach(b => lines.push(`  txt="${b.txt}" aria="${b.aria}" dis=${b.dis} | ${b.cls}`));
      }
      if (d.iframes.length) {
        lines.push('iframes:');
        d.iframes.forEach(f => lines.push(`  id="${f.id}" src="${f.src}"`));
      }
      if (d.tables.length) {
        lines.push('tabelas:');
        d.tables.forEach(t => lines.push(
          `  id="${t.id}" rows=${t.rows} proc=${t.temProcesso} | ${t.headers.join(' | ')}`
        ));
      } else {
        lines.push('(nenhuma tabela)');
      }
    });

    const output = lines.join('\n') || 'Nenhum frame acessível.';
    diagOut.textContent = output;
    diagOut.style.display = 'block';
    setStatus('idle', 'Copie o resultado abaixo e compartilhe para análise.');

  } catch (err) {
    setStatus('error', err?.message || String(err));
  } finally {
    btnDiag.disabled = false;
  }
});

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

// ── Export ────────────────────────────────────────────────────────────────────

btn.addEventListener('click', async () => {
  btn.disabled = true;
  diagOut.style.display = 'none';
  setStatus('loading', 'Aguardando...');

  try {
    const tab = await getTab();
    if (!tab?.id) { setStatus('error', 'Não foi possível identificar a aba ativa.'); return; }

    // Find which frame contains the PJe table
    const frames = await api.scripting.executeScript({
      target: { tabId: tab.id, allFrames: true },
      func: () => !!document.querySelector('#fPP\\:processosTable'),
    });

    const targetFrame = frames?.find(f => f.result === true);
    if (!targetFrame) {
      setStatus('error', 'Tabela não encontrada. Use o botão 🔍 Diagnóstico e compartilhe o resultado.');
      return;
    }

    await api.scripting.executeScript({
      target: { tabId: tab.id, frameIds: [targetFrame.frameId] },
      files: ['content.js'],
    }).catch(() => {});

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
        const tables = [...document.querySelectorAll('table')].map(t => ({
          id: t.id || '(sem id)',
          rows: t.rows.length,
          cls: (t.className || '').slice(0, 40),
        }));
        const iframes = [...document.querySelectorAll('iframe')].map(f => ({
          id: f.id || '(sem id)',
          src: (f.src || f.getAttribute('src') || '').slice(0, 80),
        }));
        return {
          url: location.href.slice(0, 80),
          tables: tables.slice(0, 15),
          iframes: iframes.slice(0, 10),
          hasPjeTable: !!document.querySelector('#fPP\\:processosTable'),
        };
      },
    });

    const lines = [];
    (results || []).forEach((r, i) => {
      if (!r?.result) return;
      const d = r.result;
      lines.push(`--- Frame ${i} (frameId: ${r.frameId}) ---`);
      lines.push(`URL: ${d.url}`);
      lines.push(`#fPP:processosTable: ${d.hasPjeTable}`);
      if (d.iframes.length) lines.push(`iframes: ${JSON.stringify(d.iframes)}`);
      if (d.tables.length) {
        lines.push('tabelas:');
        d.tables.forEach(t => lines.push(`  id="${t.id}" rows=${t.rows} class="${t.cls}"`));
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

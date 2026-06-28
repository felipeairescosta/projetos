(() => {
  if (window.__pjeExtratorLoaded) return;
  window.__pjeExtratorLoaded = true;
  const PADRAO_PROCESSO = /\d{7}-\d{2}\.\d{4}\.6\.\d{2,4}\.\d{4}/;

  const HEADER_KEYWORDS = {
    processo:            ['processo', 'número', 'numero'],
    caracteristicas:     ['caracteristic'],
    orgao_julgador:      ['órgão', 'orgao', 'orgão'],
    relator:             ['relator'],
    autuado_em:          ['autuad'],
    classe_judicial:     ['classe'],
    polo_ativo:          ['polo ativo', 'ativo'],
    polo_passivo:        ['polo passivo', 'passivo'],
    tarefas_atuais:      ['tarefa', 'nó atual', 'no atual', 'node'],
    ultima_movimentacao: ['ultima', 'última', 'movimenta'],
  };

  const INDICE_FALLBACK = {
    processo:            0,
    caracteristicas:     1,
    orgao_julgador:      2,
    relator:             3,
    autuado_em:          4,
    classe_judicial:     5,
    polo_ativo:          6,
    polo_passivo:        7,
    ultima_movimentacao: -1,
  };

  const COLUNAS_CSV = [
    'processo', 'caracteristicas', 'orgao_julgador', 'relator',
    'autuado_em', 'classe_judicial', 'polo_ativo', 'polo_passivo',
    'tarefas_atuais', 'ultima_movimentacao',
  ];

  // ── helpers ───────────────────────────────────────────────────────────────

  function limpar(texto) {
    if (!texto) return '';
    return String(texto).replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  }

  function semAcento(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  const aguardar = ms => new Promise(r => setTimeout(r, ms));

  // Execute JS in the PAGE's main world (content scripts are isolated;
  // mostrarNosAtuaisN lives in the page's window, not here).
  function executarNaPagina(codigo) {
    const s = document.createElement('script');
    s.textContent = `(()=>{ try{ ${codigo} }catch(e){} })();`;
    (document.head || document.documentElement).appendChild(s);
    s.remove();
  }

  // ── column auto-detection ─────────────────────────────────────────────────

  function mapearColunas(tabela) {
    const ths = [...tabela.querySelectorAll('thead th, thead td')];
    if (ths.length === 0) return null;
    const mapa = {};
    ths.forEach((th, i) => {
      const txt = semAcento(limpar(th.innerText || th.textContent || ''));
      for (const [campo, palavras] of Object.entries(HEADER_KEYWORDS)) {
        if (palavras.some(p => txt.includes(semAcento(p)))) { mapa[campo] = i; break; }
      }
    });
    return ('processo' in mapa) ? mapa : null;
  }

  // ── table detection ───────────────────────────────────────────────────────

  function encontrarTabela() {
    const s1 = document.querySelector('#fPP\\:processosTable');
    if (s1) return s1;
    const s2 = document.querySelector('[id*="processosTable"]');
    if (s2) return s2.tagName === 'TABLE' ? s2 : (s2.querySelector('table') || s2);
    const todas = [...document.querySelectorAll('table')];
    const comProcesso = todas.filter(t => PADRAO_PROCESSO.test(t.innerText || '') && t.rows.length > 1);
    if (comProcesso.length > 0) return comProcesso.reduce((a, b) => a.rows.length > b.rows.length ? a : b);
    return null;
  }

  // ── signatures & wait ─────────────────────────────────────────────────────

  function assinatura(tabela) { return limpar(tabela?.innerText || ''); }

  async function aguardarEstavel(tabela, timeoutMs = 15000) {
    const t0 = Date.now();
    let prev = null, streak = 0;
    while (Date.now() - t0 < timeoutMs) {
      const cur = assinatura(tabela);
      streak = (cur && cur === prev) ? streak + 1 : 0;
      prev = cur;
      if (cur && streak >= 2) return;
      await aguardar(500);
    }
  }

  // ── frame diagnostic (shown in overlay at start) ──────────────────────────

  function diagnosticarFrame(tabela) {
    const norm = s => (s || '').slice(0, 50);

    const pag =
      document.getElementById('fPP:processosTable:scTabela_table') ||
      document.querySelector('[id*="scTabela_table"]') ||
      document.querySelector('.rich-datascr') ||
      document.querySelector('.mat-paginator') ||
      document.querySelector('[class*="paginator"]');

    const pagId    = pag ? norm(pag.id || 'sem id') : 'NÃO ENCONTRADO';
    const matNext  = !!document.querySelector('.mat-paginator-navigation-next, [aria-label="Next page"]');

    // Column headers detected
    const ths = [...tabela.querySelectorAll('thead th, thead td')];
    const headers = ths.map(th => norm(limpar(th.innerText || th.textContent || ''))).filter(Boolean);

    // First row: button IDs and cell count
    let btnNoId = 'NÃO ENCONTRADO', celulas = 0;
    const primeiraLinha = tabela.querySelector('tbody tr, tr');
    if (primeiraLinha) {
      const btn = primeiraLinha.querySelector('[id^="btnMostrarNos"]');
      if (btn) btnNoId = norm(btn.id);
      celulas = primeiraLinha.querySelectorAll('td').length;
      // Any other buttons
      const outrosBtns = [...primeiraLinha.querySelectorAll('button, a')]
        .map(b => norm(b.id || b.getAttribute('aria-label') || b.title || b.className))
        .filter(Boolean).slice(0, 3);
      if (outrosBtns.length) btnNoId += ' | outros: ' + outrosBtns.join(', ');
    }

    return (
      `Tabela: ${norm(tabela.id || 'sem id')} (${celulas} colunas)\n` +
      `Headers: ${headers.length ? headers.join(' | ') : 'nenhum'}\n` +
      `Paginador: ${pagId} | mat-next:${matNext}\n` +
      `BtnTarefas: ${btnNoId}`
    );
  }

  // ── nó atual via Ajax (JSF/RichFaces) ────────────────────────────────────

  async function extrairNoAtual(tr) {
    const btn = tr.querySelector('[id^="btnMostrarNos"]');
    if (!btn) return '';

    const m = btn.id.match(/btnMostrarNos(\d+)/);
    if (!m) return '';

    const n = m[1];
    const elementId = `fPP:processosTable:${n}:nosAtuais`;

    // Must run in page's main world — content script window is isolated.
    executarNaPagina(
      `if(typeof mostrarNosAtuais${n}==='function') mostrarNosAtuais${n}('${n}');`
    );

    const t0 = Date.now();
    while (Date.now() - t0 < 5000) {
      const el = document.getElementById(elementId) ||
                 document.querySelector(`[id*=":${n}:nosAtuais"]`);
      const txt = limpar(el?.innerText || el?.textContent || '');
      if (txt) return txt;
      await aguardar(200);
    }
    return '';
  }

  // ── tarefas via "Visualizar" click (Angular) ──────────────────────────────

  async function extrairTarefasViaClick(tr) {
    const btnVis = [...tr.querySelectorAll('button, a, [role="button"]')].find(el => {
      const txt = semAcento((el.innerText || el.textContent || el.getAttribute('aria-label') || '').toLowerCase());
      return txt.includes('visualizar');
    });
    if (!btnVis) return '';

    const targetCell = btnVis.closest('td');
    const snapCell = limpar(targetCell?.innerText || '');

    // Snapshot every CDK overlay pane and its current text
    const cdkContainer = document.querySelector('.cdk-overlay-container');
    const panesAntes = [...document.querySelectorAll('.cdk-overlay-container .cdk-overlay-pane')];
    const textosPanesAntes = panesAntes.map(p => limpar(p.innerText || ''));
    const snapCdkTotal = limpar(cdkContainer?.innerText || '');

    clicarElemento(btnVis);

    const fecharOverlay = () => {
      document.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'Escape', code: 'Escape', bubbles: true, cancelable: true,
      }));
      const bd = document.querySelector('.cdk-overlay-backdrop');
      if (bd) bd.click();
    };

    const t0 = Date.now();
    while (Date.now() - t0 < 8000) {
      await aguardar(400);

      // A: cell content changed (Angular replaced button with lazy-loaded text)
      if (targetCell) {
        const txt = limpar(targetCell.innerText || '');
        if (txt && txt !== snapCell && !/^visualizar$/i.test(txt.trim())) return txt;
      }

      // B: any CDK pane's content changed (catches dialogs, menus, popovers)
      const panesAgora = [...document.querySelectorAll('.cdk-overlay-container .cdk-overlay-pane')];
      for (let i = 0; i < panesAgora.length; i++) {
        const txt = limpar(panesAgora[i].innerText || '');
        if (!txt || txt.length < 5) continue;
        const txtAntes = textosPanesAntes[i] ?? '';
        if (txt !== txtAntes) {
          fecharOverlay();
          await aguardar(600);
          return txt;
        }
      }

      // C: CDK container text changed but pane scan missed it
      const cdkNow = limpar(cdkContainer?.innerText || '');
      if (cdkNow !== snapCdkTotal && cdkNow.length > 5) {
        fecharOverlay();
        await aguardar(600);
        return (cdkNow.length > snapCdkTotal.length
          ? cdkNow.slice(snapCdkTotal.length).trim()
          : cdkNow);
      }

      // D: Angular detail row appeared as next sibling (expandable rows)
      const next = tr.nextElementSibling;
      if (next && next.tagName === 'TR' && !PADRAO_PROCESSO.test(next.innerText || '')) {
        const txt = limpar(next.innerText || '');
        if (txt && txt.length > 5) {
          clicarElemento(btnVis);
          await aguardar(400);
          return txt;
        }
      }
    }

    return '';
  }

  // ── page extraction ───────────────────────────────────────────────────────

  function lerCelula(tds, idx, total) {
    const real = idx >= 0 ? idx : total + idx;
    return (real >= 0 && real < total) ? limpar(tds[real]?.innerText) : '';
  }

  async function extrairPagina(tabela, mapa, numeroPagina) {
    await aguardarEstavel(tabela);
    const tbody = tabela.querySelector('tbody') || tabela;
    const linhas = tbody.querySelectorAll('tr');
    const dados = [];

    for (const tr of linhas) {
      const textoLinha = limpar(tr.innerText || '');
      const matchProc = PADRAO_PROCESSO.exec(textoLinha);
      if (!matchProc) continue;

      const tds = tr.querySelectorAll('td');
      const qtd = tds.length;
      const reg = { pagina: numeroPagina };

      for (const campo of COLUNAS_CSV.filter(c => c !== 'tarefas_atuais')) {
        const idx = mapa[campo];
        if (idx === undefined) { reg[campo] = ''; continue; }
        reg[campo] = lerCelula(tds, idx, qtd);
      }

      if (!PADRAO_PROCESSO.test(reg.processo)) reg.processo = matchProc[0];

      // 1) Try reading from table cell if header was detected AND cell has real content
      //    (ignore "Visualizar" — that's the button label, not actual task data)
      const idxTarefa = mapa['tarefas_atuais'];
      if (idxTarefa !== undefined) {
        const txt = lerCelula(tds, idxTarefa, qtd);
        if (txt && !/^visualizar$/i.test(txt.trim())) {
          reg.tarefas_atuais = txt;
        }
      }
      // 2) Fallback: JSF/RichFaces Ajax button (Python script approach)
      if (!reg.tarefas_atuais) {
        reg.tarefas_atuais = await extrairNoAtual(tr);
      }
      // 3) Fallback: Angular "Visualizar" button click
      if (!reg.tarefas_atuais) {
        reg.tarefas_atuais = await extrairTarefasViaClick(tr);
      }

      if (!reg.autuado_em) {
        for (const c of ['caracteristicas', 'autuado_em', 'classe_judicial',
                         'polo_ativo', 'polo_passivo', 'ultima_movimentacao']) {
          if (!reg[c]) reg[c] = 'SIGILO';
        }
      }

      dados.push(reg);
    }
    return dados;
  }

  // ── pagination ────────────────────────────────────────────────────────────

  function encontrarBotaoProxima() {
    // Strategy 1: RichFaces JSF paginator (confirmed in Python script)
    const richPag =
      document.getElementById('fPP:processosTable:scTabela_table') ||
      document.querySelector('[id*="scTabela_table"]') ||
      document.querySelector('[id*="scrollerTable"]') ||
      document.querySelector('.rich-datascr');

    if (richPag) {
      const cells = [...richPag.querySelectorAll('td.rich-datascr-button')];
      let alvo = cells.find(td => {
        const txt = (td.innerText || td.textContent || '').trim();
        return txt === '»' && !(td.className || '').includes('dsbld');
      });
      if (!alvo && cells.length >= 2) {
        const c = cells[cells.length - 2];
        if (!(c.className || '').includes('dsbld')) alvo = c;
      }
      if (alvo) return { el: alvo, via: `richfaces:${richPag.id || 'sem id'}` };
    }

    // Strategy 2: Angular Material paginator (classic and MDC/v15+)
    const matNext = document.querySelector(
      '.mat-paginator-navigation-next:not([disabled]), ' +
      '.mat-mdc-paginator-navigation-next:not([disabled]), ' +
      '[aria-label="Next page"]:not([disabled]), ' +
      '[aria-label="Próxima página"]:not([disabled]), ' +
      '[aria-label="Próxima"]:not([disabled]), ' +
      '[aria-label="Próxima pagina"]:not([disabled]), ' +
      '[aria-label="Página seguinte"]:not([disabled]), ' +
      '[aria-label="Avançar"]:not([disabled])'
    );
    if (matNext) return { el: matNext, via: 'angular-material' };

    // Strategy 2b: case-insensitive aria-label substring match for "next" / "próxima"
    const ariaNext = [...document.querySelectorAll('button')].find(btn => {
      if (btn.disabled || btn.getAttribute('aria-disabled') === 'true') return false;
      const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
      return aria.includes('next') || aria.includes('próxima') || aria.includes('proxima') ||
             aria.includes('seguinte') || aria.includes('avanç');
    });
    if (ariaNext) return { el: ariaNext, via: `aria-label:${ariaNext.getAttribute('aria-label')}` };

    // Strategy 3: any id/class containing "paginador" or "paginator"
    const genPag = document.querySelector('[id*="paginador"], [id*="paginator"], [class*="paginador"], [class*="paginator"]');
    if (genPag) {
      const btns = [...genPag.querySelectorAll('button, a, td, li, span')];
      const next = btns.find(el => {
        const txt = (el.innerText || el.textContent || '').trim();
        const dis = el.disabled || el.getAttribute('aria-disabled') === 'true' ||
                    (el.className || '').includes('disabled') ||
                    (el.className || '').includes('dsbld');
        return !dis && (txt === '»' || txt === '›' || txt === '>' || txt === 'Próxima');
      });
      if (next) return { el: next, via: `generic:${genPag.id || genPag.className.slice(0, 30)}` };
    }

    // Strategy 4: last resort — any visible » or › anywhere in document
    const any = [...document.querySelectorAll('button, td, a, li')].find(el => {
      const txt = (el.innerText || el.textContent || '').trim();
      const dis = el.disabled || el.getAttribute('aria-disabled') === 'true' ||
                  (el.className || '').includes('disabled') ||
                  (el.className || '').includes('dsbld');
      return !dis && (txt === '»' || txt === '›');
    });
    if (any) return { el: any, via: `fallback:${any.tagName}` };

    return null;
  }

  function clicarElemento(el) {
    // Set attribute on the shared DOM; MutationObserver in content_main.js (MAIN world)
    // detects this and fires the click where Angular zone.js is listening.
    el.setAttribute('data-pje-click', Date.now().toString());
    // Fallback: if main world doesn't handle it within 300 ms, click from isolated world.
    setTimeout(() => {
      if (el.hasAttribute('data-pje-click')) {
        el.removeAttribute('data-pje-click');
        el.focus?.();
        el.click?.();
      }
    }, 300);
  }

  // Returns the new table element on success, null on failure.
  // Re-finds the table dynamically so Angular re-renders don't break us.
  async function proximaPagina(tabela) {
    await aguardarEstavel(tabela);
    const antes = assinatura(tabela);

    const resultado = encontrarBotaoProxima();
    if (!resultado) return null;

    // Up to 3 click attempts
    for (let tentativa = 0; tentativa < 3; tentativa++) {
      const r = tentativa === 0 ? resultado : encontrarBotaoProxima();
      if (!r) break;

      clicarElemento(r.el);

      const t0 = Date.now();
      while (Date.now() - t0 < 10000) {
        await aguardar(400);
        // Re-find table each poll — Angular may have re-created the element
        const tabelaAtual = encontrarTabela() || tabela;
        const sig = assinatura(tabelaAtual);
        if (sig && sig !== antes) {
          await aguardarEstavel(tabelaAtual);
          return tabelaAtual; // return new reference
        }
      }

      await aguardar(1000);
    }

    return null;
  }

  // ── CSV + download ────────────────────────────────────────────────────────

  function toCSV(dados) {
    const esc  = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const head = COLUNAS_CSV.map(esc).join(',');
    const rows = dados.map(r => COLUNAS_CSV.map(c => esc(r[c])).join(','));
    return [head, ...rows].join('\r\n');
  }

  function download(csv) {
    const data = new Date().toISOString().slice(0, 10);
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement('a'), {
      href: url, download: `pje_trece_${data}.csv`, style: 'display:none',
    });
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
  }

  // ── progress overlay ──────────────────────────────────────────────────────

  let overlay = null;

  function mostrarOverlay(txt) {
    if (!overlay) {
      overlay = Object.assign(document.createElement('div'), {
        style: [
          'position:fixed', 'top:16px', 'right:16px', 'z-index:2147483647',
          'background:#003366', 'color:#fff', 'padding:12px 16px',
          'border-radius:8px', 'font:12px/1.6 monospace',
          'box-shadow:0 4px 12px rgba(0,0,0,.4)', 'max-width:380px',
          'white-space:pre-wrap', 'word-break:break-all',
        ].join(';'),
      });
      document.body.appendChild(overlay);
    }
    overlay.textContent = txt;
  }

  function removerOverlay() { overlay?.remove(); overlay = null; }

  // ── main ──────────────────────────────────────────────────────────────────

  async function exportarTudo(sendResponse) {
    const tabelaInicial = encontrarTabela();
    if (!tabelaInicial) {
      sendResponse({ ok: false, error: 'Tabela não encontrada neste frame.' });
      return;
    }

    // Brief diagnostic (1s) then start immediately
    mostrarOverlay(`⏳ Iniciando extração…\n${diagnosticarFrame(tabelaInicial)}`);
    await aguardar(1000);

    // Use let so Angular re-renders can update the reference
    let tabela = tabelaInicial;
    let mapa = mapearColunas(tabela) || INDICE_FALLBACK;
    const todos = [];
    let pagina = 1;
    const visitadas = new Set();

    while (true) {
      const sig = assinatura(tabela);
      if (sig && visitadas.has(sig)) break;
      visitadas.add(sig);

      mostrarOverlay(`⏳ Extraindo página ${pagina}…\n${todos.length} processo(s) coletados`);

      const dados = await extrairPagina(tabela, mapa, pagina);
      todos.push(...dados);

      const proximoRes = encontrarBotaoProxima();
      const paginacaoInfo = proximoRes
        ? `próxima: ${proximoRes.via}`
        : 'próxima: NÃO ENCONTRADA';

      mostrarOverlay(`✔ Página ${pagina} — ${dados.length} processos\nTotal: ${todos.length}\n${paginacaoInfo}`);

      await aguardar(800); // let Angular settle after Visualizar clicks before paginating

      // proximaPagina returns the new table reference (Angular may recreate it)
      const novaTabela = await proximaPagina(tabela);
      if (!novaTabela) break;
      tabela = novaTabela; // update reference for next iteration
      pagina++;
      if (pagina > 500) break;
    }

    removerOverlay();

    if (todos.length === 0) {
      sendResponse({ ok: false, error: 'Nenhum processo encontrado na consulta.' });
      return;
    }

    download(toCSV(todos));
    sendResponse({ ok: true, rows: todos.length, paginas: pagina });
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.action !== 'exportCSV') return;
    if (!encontrarTabela()) {
      sendResponse({ ok: false, error: 'Tabela não encontrada neste frame.' });
      return;
    }
    exportarTudo(sendResponse);
    return true;
  });
})();

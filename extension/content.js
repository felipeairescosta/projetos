if (window.__pjeExtratorLoaded) { /* already registered */ }
window.__pjeExtratorLoaded = true;

(() => {
  const PADRAO_PROCESSO = /\d{7}-\d{2}\.\d{4}\.6\.06\.\d{4}/;

  const INDICE_TD = {
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
    'no_atual', 'ultima_movimentacao',
  ];

  // ── helpers ───────────────────────────────────────────────────────────────

  function limpar(texto) {
    if (!texto) return '';
    return String(texto).replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  }

  const aguardar = ms => new Promise(r => setTimeout(r, ms));

  // ── table detection ───────────────────────────────────────────────────────
  // Strategy 1: exact PJe/RichFaces ID.
  // Strategy 2: any element whose ID contains "processosTable", take inner table.
  // Strategy 3: largest table whose text contains a process number pattern.

  function encontrarTabela() {
    const s1 = document.querySelector('#fPP\\:processosTable');
    if (s1) return s1;

    const s2 = document.querySelector('[id*="processosTable"]');
    if (s2) return s2.tagName === 'TABLE' ? s2 : (s2.querySelector('table') || s2);

    const todas = [...document.querySelectorAll('table')];
    const comProcesso = todas.filter(t =>
      PADRAO_PROCESSO.test(t.innerText || '') && t.rows.length > 1
    );
    if (comProcesso.length > 0) {
      return comProcesso.reduce((a, b) => a.rows.length > b.rows.length ? a : b);
    }

    return null;
  }

  // ── signatures & wait ─────────────────────────────────────────────────────

  function assinatura(tabela) {
    return limpar(tabela?.innerText || '');
  }

  async function aguardarEstavel(tabela, timeoutMs = 30000) {
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

  // ── nó atual via Ajax ─────────────────────────────────────────────────────

  async function extrairNoAtual(tr) {
    const btn = tr.querySelector('[id^="btnMostrarNos"]');
    if (!btn) return '';

    const m = btn.id.match(/btnMostrarNos(\d+)/);
    if (!m) return '';

    const n = m[1];
    const elementId = `fPP:processosTable:${n}:nosAtuais`;

    try {
      const fn = window[`mostrarNosAtuais${n}`];
      if (typeof fn === 'function') fn(n);
    } catch (_) { return ''; }

    const t0 = Date.now();
    while (Date.now() - t0 < 8000) {
      const el = document.getElementById(elementId);
      const txt = limpar(el?.innerText || el?.textContent || '');
      if (txt) return txt;
      await aguardar(200);
    }
    return '';
  }

  // ── page extraction ───────────────────────────────────────────────────────

  async function extrairPagina(tabela, numeroPagina) {
    await aguardarEstavel(tabela);

    // Prefer tbody rows; fall back to all tr in the table.
    const tbody = tabela.querySelector('tbody') || tabela.querySelector('[id$="\\:tb"]') || tabela;
    const linhas = tbody.querySelectorAll('tr');
    const dados  = [];

    for (const tr of linhas) {
      const textoLinha = limpar(tr.innerText || '');
      const matchProc  = PADRAO_PROCESSO.exec(textoLinha);
      if (!matchProc) continue;

      const tds = tr.querySelectorAll('td');
      const qtd = tds.length;
      const reg = { pagina: numeroPagina };

      for (const [col, idx] of Object.entries(INDICE_TD)) {
        const real = idx >= 0 ? idx : qtd + idx;
        reg[col] = (real >= 0 && real < qtd) ? limpar(tds[real]?.innerText) : '';
      }

      if (!PADRAO_PROCESSO.test(reg.processo)) reg.processo = matchProc[0];

      reg.no_atual = await extrairNoAtual(tr);

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

  async function proximaPagina(tabela) {
    await aguardarEstavel(tabela);
    const antes = assinatura(tabela);

    // Look for paginator near the table (parent or sibling).
    const root = tabela.closest('form') || tabela.parentElement || document;
    const table = root.querySelector('[id*="scTabela_table"], [id*="scrollerTable"]')
                  || document.querySelector('[id*="scTabela_table"], [id*="scrollerTable"]');

    if (!table) return false;

    const cells = [...table.querySelectorAll('td.rich-datascr-button, td[class*="datascr-button"]')];

    let alvo = cells.find(td => {
      const txt = limpar(td.innerText || td.textContent || '');
      return txt === '»' && !(td.className || '').includes('dsbld');
    });

    if (!alvo && cells.length >= 2) {
      const c = cells[cells.length - 2];
      if (!(c.className || '').includes('dsbld')) alvo = c;
    }

    if (!alvo) return false;

    for (const tipo of ['mousedown', 'mouseup', 'click']) {
      alvo.dispatchEvent(new MouseEvent(tipo, { bubbles: true, cancelable: true }));
    }

    const t0 = Date.now();
    while (Date.now() - t0 < 20000) {
      await aguardar(500);
      if (assinatura(tabela) !== antes) {
        await aguardarEstavel(tabela);
        return true;
      }
    }
    return false;
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
          'position:fixed', 'bottom:20px', 'right:20px', 'z-index:2147483647',
          'background:#003366', 'color:#fff', 'padding:12px 16px',
          'border-radius:8px', 'font:13px/1.5 sans-serif',
          'box-shadow:0 4px 12px rgba(0,0,0,.35)', 'max-width:320px',
          'white-space:pre-wrap',
        ].join(';'),
      });
      document.body.appendChild(overlay);
    }
    overlay.textContent = txt;
  }

  function removerOverlay() { overlay?.remove(); overlay = null; }

  // ── main ──────────────────────────────────────────────────────────────────

  async function exportarTudo(sendResponse) {
    const tabela = encontrarTabela();
    if (!tabela) {
      sendResponse({ ok: false, error: 'Tabela não encontrada neste frame.' });
      return;
    }

    const todos = [];
    let pagina = 1;
    const visitadas = new Set();

    while (true) {
      const sig = assinatura(tabela);
      if (sig && visitadas.has(sig)) break;
      visitadas.add(sig);

      mostrarOverlay(`⏳ Extraindo página ${pagina}…\n${todos.length} processo(s) coletados`);

      const dados = await extrairPagina(tabela, pagina);
      todos.push(...dados);

      mostrarOverlay(`✔ Página ${pagina} — ${dados.length} processos\nTotal: ${todos.length}`);

      if (!await proximaPagina(tabela)) break;
      pagina++;
    }

    removerOverlay();

    if (todos.length === 0) {
      sendResponse({ ok: false, error: 'Nenhum processo encontrado na consulta.' });
      return;
    }

    download(toCSV(todos));
    sendResponse({ ok: true, rows: todos.length, paginas: pagina });
  }

  // Only respond if this frame has the table.
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

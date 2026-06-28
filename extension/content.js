// Guard against multiple injections
if (window.__pjeExtratorLoaded) {
  // already loaded — just re-register listener is safe since we clear below
}
window.__pjeExtratorLoaded = true;

(() => {
  const PADRAO_PROCESSO = /\d{7}-\d{2}\.\d{4}\.6\.06\.\d{4}/;

  // td index for each column (-1 = last td). Mirrors extrair_pje_v17.py.
  const INDICE_TD = {
    processo:            0,
    caracteristicas:     1,
    orgao_julgador:      2,
    relator:             3,
    autuado_em:          4,
    classe_judicial:     5,
    polo_ativo:          6,
    polo_passivo:        7,
    ultima_movimentacao: -1,   // no_atual comes from Ajax, not a td index
  };

  const COLUNAS_CSV = [
    'processo', 'caracteristicas', 'orgao_julgador', 'relator',
    'autuado_em', 'classe_judicial', 'polo_ativo', 'polo_passivo',
    'no_atual', 'ultima_movimentacao',
  ];

  // ── helpers ──────────────────────────────────────────────────────────────

  function limpar(texto) {
    if (!texto) return '';
    return String(texto).replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  }

  function aguardar(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  // Snapshot of the visible table body — used to detect page changes.
  function assinatura() {
    const tb = document.querySelector('#fPP\\:processosTable\\:tb');
    return limpar(tb?.innerText || '');
  }

  async function aguardarEstavel(timeoutMs = 30000) {
    const t0 = Date.now();
    let prev = null, streak = 0;
    while (Date.now() - t0 < timeoutMs) {
      const cur = assinatura();
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
    } catch (_) {
      return '';
    }

    // Poll until the Ajax response populates the element (max 8 s)
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

  async function extrairPagina(numeroPagina) {
    await aguardarEstavel();

    const linhas = document.querySelectorAll('#fPP\\:processosTable\\:tb tr');
    const dados = [];

    for (const tr of linhas) {
      const textoLinha = limpar(tr.innerText || '');
      const matchProc = PADRAO_PROCESSO.exec(textoLinha);
      if (!matchProc) continue;

      const tds = tr.querySelectorAll('td');
      const qtd = tds.length;
      const reg = { pagina: numeroPagina };

      for (const [col, idx] of Object.entries(INDICE_TD)) {
        const real = idx >= 0 ? idx : qtd + idx;
        reg[col] = (real >= 0 && real < qtd) ? limpar(tds[real]?.innerText) : '';
      }

      // Fallback: ensure processo has the number
      if (!PADRAO_PROCESSO.test(reg.processo)) reg.processo = matchProc[0];

      reg.no_atual = await extrairNoAtual(tr);

      // Sigiloso: autuado_em vazio mas processo preenchido
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

  async function proximaPagina() {
    await aguardarEstavel();
    const antes = assinatura();

    const table = document.getElementById('fPP:processosTable:scTabela_table');
    if (!table) return false;

    const cells = [...table.querySelectorAll('td.rich-datascr-button')];

    let alvo = cells.find(td => {
      const txt = limpar(td.innerText || td.textContent || '');
      return txt === '»' && !(td.className || '').includes('dsbld');
    });

    // Fallback: second-to-last button if no explicit '»'
    if (!alvo && cells.length >= 2) {
      const c = cells[cells.length - 2];
      if (!(c.className || '').includes('dsbld')) alvo = c;
    }

    if (!alvo) return false;

    for (const tipo of ['mousedown', 'mouseup', 'click']) {
      alvo.dispatchEvent(new MouseEvent(tipo, { bubbles: true, cancelable: true }));
    }

    // Wait up to 20 s for the table to change
    const t0 = Date.now();
    while (Date.now() - t0 < 20000) {
      await aguardar(500);
      const depois = assinatura();
      if (depois && depois !== antes) {
        await aguardarEstavel();
        return true;
      }
    }
    return false;
  }

  // ── CSV generation ────────────────────────────────────────────────────────

  function toCSV(dados) {
    const esc = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const linhas = [COLUNAS_CSV.map(esc).join(',')];
    for (const row of dados) linhas.push(COLUNAS_CSV.map(c => esc(row[c])).join(','));
    return linhas.join('\r\n');
  }

  function download(csv) {
    const data = new Date().toISOString().slice(0, 10);
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement('a'), {
      href: url,
      download: `pje_trece_${data}.csv`,
      style: 'display:none',
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

  function removerOverlay() {
    overlay?.remove();
    overlay = null;
  }

  // ── main ──────────────────────────────────────────────────────────────────

  async function exportarTudo(sendResponse) {
    const tableEl = document.querySelector('#fPP\\:processosTable');
    if (!tableEl) {
      sendResponse({ ok: false, error: 'Tabela do PJe não encontrada. Execute uma consulta primeiro.' });
      return;
    }

    const todos = [];
    let pagina = 1;
    const visitadas = new Set();

    while (true) {
      const sig = assinatura();
      if (sig && visitadas.has(sig)) break;
      visitadas.add(sig);

      mostrarOverlay(`⏳ Extraindo página ${pagina}…\n${todos.length} processo(s) coletados`);

      const dados = await extrairPagina(pagina);
      todos.push(...dados);

      mostrarOverlay(`✔ Página ${pagina} — ${dados.length} processos\nTotal: ${todos.length}`);

      const temProxima = await proximaPagina();
      if (!temProxima) break;
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

  // Replace any previous listener by re-registering (guard at top prevents
  // duplicate listeners since the module scope is fresh per injection).
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.action !== 'exportCSV') return;
    exportarTudo(sendResponse);
    return true; // keep async channel open
  });
})();

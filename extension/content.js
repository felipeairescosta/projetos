if (window.__pjeExtratorLoaded) { /* already registered */ }
window.__pjeExtratorLoaded = true;

(() => {
  const PADRAO_PROCESSO = /\d{7}-\d{2}\.\d{4}\.6\.06\.\d{4}/;

  // Canonical field names → keywords that appear in <th> text (lowercase, no accents)
  const HEADER_KEYWORDS = {
    processo:            ['processo', 'número', 'numero'],
    caracteristicas:     ['caracteristic'],
    orgao_julgador:      ['órgão', 'orgao', 'orgão'],
    relator:             ['relator'],
    autuado_em:          ['autuad'],
    classe_judicial:     ['classe'],
    polo_ativo:          ['polo ativo', 'ativo'],
    polo_passivo:        ['polo passivo', 'passivo'],
    ultima_movimentacao: ['ultima', 'última', 'movimenta'],
  };

  // Fallback fixed indices if table has no readable headers (from extrair_pje_v17.py)
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
    'no_atual', 'ultima_movimentacao',
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

  // ── column auto-detection from <th> headers ───────────────────────────────

  function mapearColunas(tabela) {
    const ths = [...tabela.querySelectorAll('thead th, thead td')];
    if (ths.length === 0) return null; // no headers found

    const mapa = {};
    ths.forEach((th, i) => {
      const txt = semAcento(limpar(th.innerText || th.textContent || ''));
      for (const [campo, palavras] of Object.entries(HEADER_KEYWORDS)) {
        if (palavras.some(p => txt.includes(semAcento(p)))) {
          mapa[campo] = i;
          break;
        }
      }
    });

    // Must have at least "processo" mapped to be valid
    return ('processo' in mapa) ? mapa : null;
  }

  // ── table detection ───────────────────────────────────────────────────────

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

      for (const campo of COLUNAS_CSV.filter(c => c !== 'no_atual')) {
        const idx = mapa[campo];
        if (idx === undefined) { reg[campo] = ''; continue; }
        reg[campo] = lerCelula(tds, idx, qtd);
      }

      // Sanity check: if "processo" cell doesn't have the number, use regex match
      if (!PADRAO_PROCESSO.test(reg.processo)) reg.processo = matchProc[0];

      reg.no_atual = await extrairNoAtual(tr);

      // Processos sigilosos
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

    // Look anywhere in the document for paginator (different PJe views use different IDs)
    const paginatorTable =
      document.querySelector('[id*="scTabela_table"]') ||
      document.querySelector('[id*="scrollerTable"]') ||
      document.querySelector('[id*="paginador"]') ||
      document.querySelector('[id*="paginator"]');

    if (!paginatorTable) return false;

    const cells = [...paginatorTable.querySelectorAll(
      'td.rich-datascr-button, td[class*="datascr-button"], td[class*="paginator"]'
    )];

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

    // Auto-detect column order from headers; fall back to fixed indices
    const mapa = mapearColunas(tabela) || INDICE_FALLBACK;

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

(() => {
  // Selectors ordered by specificity for PJe (PrimeFaces / Angular / JSF)
  const TABLE_SELECTORS = [
    '.ui-datatable table',
    'table.ui-datatable-data',
    '[id*="lista"] table',
    '[id*="resultado"] table',
    '[id*="processos"] table',
    'table[role="grid"]',
  ];

  function findBestTable() {
    for (const sel of TABLE_SELECTORS) {
      const tables = document.querySelectorAll(sel);
      if (tables.length > 0) {
        // prefer the table with the most rows
        return [...tables].reduce((best, t) =>
          t.rows.length > best.rows.length ? t : best
        );
      }
    }
    // fallback: largest table on the page
    const all = [...document.querySelectorAll('table')];
    if (all.length === 0) return null;
    return all.reduce((best, t) => t.rows.length > best.rows.length ? t : best);
  }

  function cellText(cell) {
    return cell.innerText.replace(/\s+/g, ' ').trim();
  }

  function extractTable(table) {
    const headers = [];
    const rows = [];

    // header: <thead> or first <tr> with <th>
    const thead = table.querySelector('thead');
    const headerRow = thead
      ? thead.querySelector('tr')
      : [...table.querySelectorAll('tr')].find(r => r.querySelector('th'));

    if (headerRow) {
      for (const th of headerRow.querySelectorAll('th, td')) {
        headers.push(cellText(th));
      }
    }

    // body rows
    const tbody = table.querySelector('tbody') || table;
    for (const tr of tbody.querySelectorAll('tr')) {
      if (tr.querySelector('th')) continue; // skip sub-headers
      const cells = tr.querySelectorAll('td');
      if (cells.length === 0) continue;
      rows.push([...cells].map(cellText));
    }

    return { headers, rows };
  }

  function toCSV({ headers, rows }) {
    const escape = v => `"${v.replace(/"/g, '""')}"`;
    const lines = [];
    if (headers.length > 0) lines.push(headers.map(escape).join(','));
    for (const row of rows) lines.push(row.map(escape).join(','));
    return lines.join('\r\n');
  }

  function download(csv, filename) {
    // BOM UTF-8 for Excel compatibility
    const bom = '﻿';
    const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 1000);
  }

  function buildFilename() {
    const date = new Date().toISOString().slice(0, 10);
    const page = document.title.replace(/[^a-zA-Z0-9]/g, '_').slice(0, 40) || 'pje';
    return `${page}_${date}.csv`;
  }

  // Message listener called from popup
  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.action !== 'exportCSV') return;

    const table = findBestTable();
    if (!table) {
      sendResponse({ ok: false, error: 'Nenhuma tabela encontrada na página.' });
      return;
    }

    const data = extractTable(table);
    if (data.rows.length === 0) {
      sendResponse({ ok: false, error: 'A tabela não contém linhas de dados.' });
      return;
    }

    const csv = toCSV(data);
    download(csv, buildFilename());
    sendResponse({ ok: true, rows: data.rows.length, cols: data.headers.length });
  });
})();

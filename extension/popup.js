// Chrome/Firefox API compatibility
const api = typeof browser !== 'undefined' ? browser : chrome;

const btn    = document.getElementById('btn-export');
const status = document.getElementById('status');

function setStatus(type, text) {
  status.className = `status ${type}`;
  status.textContent = text;
}

btn.addEventListener('click', async () => {
  btn.disabled = true;
  setStatus('loading', 'Aguardando...');

  try {
    const [tab] = await api.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.id) {
      setStatus('error', 'Não foi possível identificar a aba ativa.');
      return;
    }

    // Inject content script on demand (handles cases where page reloaded)
    await api.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['content.js'],
    }).catch(() => {}); // ignore if already injected

    setStatus('loading', 'Extraindo processos de todas as páginas… acompanhe na página do PJe.');

    const response = await api.tabs.sendMessage(tab.id, { action: 'exportCSV' });

    if (response.ok) {
      setStatus('success',
        `✓ ${response.rows} processo${response.rows !== 1 ? 's' : ''} exportado${response.rows !== 1 ? 's' : ''} em ${response.paginas} página${response.paginas !== 1 ? 's' : ''}.`
      );
    } else {
      setStatus('error', response.error || 'Erro desconhecido.');
    }
  } catch (err) {
    const msg = err?.message || String(err);
    if (msg.includes('Cannot establish connection') || msg.includes('No tab')) {
      setStatus('error', 'Abra o PJe TRE-CE antes de exportar.');
    } else {
      setStatus('error', msg);
    }
  } finally {
    btn.disabled = false;
  }
});

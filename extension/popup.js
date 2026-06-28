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
    if (!tab?.id) {
      setStatus('error', 'Não foi possível identificar a aba ativa.');
      return;
    }

    // Step 1: scan all frames to find which one contains the PJe table
    const frames = await api.scripting.executeScript({
      target: { tabId: tab.id, allFrames: true },
      func: () => !!document.querySelector('#fPP\\:processosTable'),
    });

    const targetFrame = frames?.find(f => f.result === true);
    if (!targetFrame) {
      setStatus('error', 'Tabela do PJe não encontrada. Execute uma consulta e aguarde os resultados carregarem.');
      return;
    }

    // Step 2: inject content script specifically in that frame
    await api.scripting.executeScript({
      target: { tabId: tab.id, frameIds: [targetFrame.frameId] },
      files: ['content.js'],
    }).catch(() => {});

    setStatus('loading', 'Extraindo processos de todas as páginas… acompanhe na página do PJe.');

    // Step 3: send message directly to the frame that has the table
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
    if (msg.includes('Cannot establish connection') || msg.includes('No tab')) {
      setStatus('error', 'Abra o PJe TRE-CE antes de exportar.');
    } else {
      setStatus('error', msg);
    }
  } finally {
    btn.disabled = false;
  }
});

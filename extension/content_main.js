// Runs in the page's MAIN world — receives click requests from the isolated
// content script via postMessage and fires them where Angular's zone.js listens.
(() => {
  if (window.__pjeMainLoaded) return;
  window.__pjeMainLoaded = true;

  window.addEventListener('message', e => {
    if (e.source !== window || e.data?.__pje__ !== 'click') return;
    const el = document.querySelector(`[data-pje-click="${e.data.id}"]`);
    if (!el) return;
    el.focus?.();
    ['mousedown', 'mouseup', 'click'].forEach(ev =>
      el.dispatchEvent(new MouseEvent(ev, { bubbles: true, cancelable: true }))
    );
    el.click?.();
  });
})();

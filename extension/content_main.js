// Runs in the page's MAIN world — receives click requests from the isolated
// content script via a shared-DOM CustomEvent and fires them where Angular's
// zone.js listens. DOM CustomEvents dispatched by content scripts propagate
// to main-world listeners because the DOM is shared between worlds.
(() => {
  if (window.__pjeMainLoaded) return;
  window.__pjeMainLoaded = true;

  document.addEventListener('__pje_click__', e => {
    const el = document.querySelector(`[data-pje-click="${e.detail.id}"]`);
    if (!el) return;
    el.focus?.();
    ['mousedown', 'mouseup', 'click'].forEach(ev =>
      el.dispatchEvent(new MouseEvent(ev, { bubbles: true, cancelable: true }))
    );
    el.click?.();
  });
})();

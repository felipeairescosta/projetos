// Runs in the page's MAIN world. Uses MutationObserver on the shared DOM to
// detect click requests from the isolated content script (content.js).
// When content.js sets data-pje-click on an element, this observer fires in
// the main world and dispatches the click where Angular zone.js is listening.
// MutationObserver on shared DOM attributes is the most reliable cross-world
// communication channel in Chrome MV3 — no serialisation, no timing issues.
(() => {
  if (window.__pjeMainLoaded) return;
  window.__pjeMainLoaded = true;

  new MutationObserver(mutations => {
    for (const m of mutations) {
      if (m.type !== 'attributes' || m.attributeName !== 'data-pje-click') continue;
      const el = m.target;
      if (!el.hasAttribute('data-pje-click')) continue;
      el.removeAttribute('data-pje-click');
      el.focus?.();
      // Dispatch exactly ONE click (plus the gesture events before it).
      // Adding el.click() after dispatchEvent fires two click events, which
      // causes the Angular Material paginator to advance two pages per step
      // (producing 104/194 records instead of all 194).
      // Visualizar bypasses this relay entirely (direct btnVis.click() from
      // the isolated world), so only paginator clicks come through here.
      ['mousedown', 'mouseup', 'click'].forEach(ev =>
        el.dispatchEvent(new MouseEvent(ev, {
          bubbles: true, cancelable: true, composed: true, view: window,
        }))
      );
    }
  }).observe(document.documentElement, {
    subtree: true,
    attributes: true,
    attributeFilter: ['data-pje-click'],
  });
})();

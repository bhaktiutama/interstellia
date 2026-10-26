/* UI bersama Copper, Gargantua, Millar (docs/app/rencana-ui-seragam.md UI2). Skrip biasa, jalan dari file://.
   window.UIKIT:
   - get(key, def) / set(key, v): localStorage dengan try/catch
   - flash(el, content, s, html): tampilkan el (hidden = false, opasitas 1) lalu pudar setelah s detik; dipakai toast dan petunjuk tombol
   - keys(el, html, s): petunjuk tombol tengah bawah (D6), bawaan 8 s
   - panel(el, key, onChange): panel kontrol ciut / buka, status diingat di localStorage key (bawaan ciut, D7); kembali fungsi toggle(force)
   - tokens(): warna token CSS untuk gambar kanvas ({ ink, muted, accent, accentRGB, panel, line, warn, mono })
   - lite(on): tanpa blur (preset Hemat) */
(function () {
  'use strict';
  const T = new WeakMap();
  function get(key, def) { try { const v = localStorage.getItem(key); return v === null ? def : v; } catch (e) { return def; } }
  function set(key, v) { try { localStorage.setItem(key, String(v)); } catch (e) { /* abaikan */ } }
  function flash(el, content, s, html) {
    if (!el) return;
    if (content !== undefined && content !== null) { if (html) el.innerHTML = content; else el.textContent = content; }
    const old = T.get(el); if (old) { clearTimeout(old[0]); clearTimeout(old[1]); }
    el.hidden = false; el.style.opacity = 1;
    const a = setTimeout(() => { el.style.opacity = 0; }, Math.max(0.5, s || 4) * 1000);
    const b = setTimeout(() => { el.hidden = true; T.delete(el); }, Math.max(0.5, s || 4) * 1000 + 800);
    T.set(el, [a, b]);
  }
  function keys(el, html, s) { flash(el, html, s || 8, true); }
  function panel(el, key, onChange) {
    const toggle = (force) => {
      const open = force !== undefined ? !!force : el.classList.contains('collapsed');
      el.classList.toggle('collapsed', !open);
      if (key) set(key, open ? '1' : '0');
      if (onChange) onChange(open);
      return open;
    };
    el.classList.toggle('collapsed', (key ? get(key, '0') : '0') !== '1');
    if (onChange) onChange(!el.classList.contains('collapsed'));
    return toggle;
  }
  let TOK = null;
  function tokens() {
    if (TOK) return TOK;
    const cs = getComputedStyle(document.documentElement), v = (n, d) => (cs.getPropertyValue(n) || '').trim() || d;
    TOK = { ink: v('--ui-ink', '#d9dde3'), muted: v('--ui-muted', '#8b929c'), accent: v('--ui-accent', '#e8b765'),
      accentRGB: v('--ui-accent-rgb', '232, 183, 101'), panel: v('--ui-panel', 'rgba(12, 14, 18, 0.72)'), line: v('--ui-line', 'rgba(255, 255, 255, 0.10)'),
      warn: v('--ui-warn', '#e7806b'), mono: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace' };
    return TOK;
  }
  function lite(on) { document.body.classList.toggle('ui-lite', !!on); }
  window.UIKIT = { get, set, flash, keys, panel, tokens, lite };
})();

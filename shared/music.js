// Lagu tema bersama Interstellia (Copper, Millar, Gargantua): mp3 karya pemilik proyek di shared/musik/tema*.data.js
// (base64 agar jalan dari file://), dimuat saat pertama dibutuhkan, diputar acak bergiliran lewat satu elemen <audio>.
// Blob URL = asal sama, jadi createMediaElementSource tetap bersuara walau halaman dibuka dari file://.
// Pemakaian: el = SONGKIT.element('../../shared/musik/') lalu sambungkan ke WebAudio; SONGKIT.play() / SONGKIT.pause().
window.SONGKIT = (() => {
  const LIST = ['tema1', 'tema2'];
  const K = { el: null, base: '', cur: -1, want: false, urls: {} };
  function load(i) {
    if (K.urls[i]) return Promise.resolve(K.urls[i]);
    return new Promise((ok, no) => {
      const s = document.createElement('script'); s.src = K.base + LIST[i] + '.data.js';
      s.onload = () => {
        s.remove();
        try {
          const S = window.__SONGS || {}, bin = atob(S[LIST[i]]), u8 = new Uint8Array(bin.length);
          for (let j = 0; j < bin.length; j++) u8[j] = bin.charCodeAt(j);
          delete S[LIST[i]];
          K.urls[i] = URL.createObjectURL(new Blob([u8], { type: 'audio/mpeg' })); ok(K.urls[i]);
        } catch (e) { no(e); }
      };
      s.onerror = () => { s.remove(); no(new Error('Lagu tema tidak ditemukan: ' + s.src)); };
      document.head.appendChild(s);
    });
  }
  function pick() {                                             // acak, tidak mengulang lagu yang baru selesai
    if (LIST.length < 2) return 0;
    let i; do i = Math.floor(Math.random() * LIST.length); while (i === K.cur);
    return i;
  }
  function next() {
    const i = pick(); K.cur = i;
    load(i).then((url) => { K.el.src = url; if (K.want) K.el.play().catch(() => {}); }).catch((e) => console.warn(e));
  }
  return {
    LIST,
    element(base) {
      if (!K.el) { K.base = base; K.el = new Audio(); K.el.preload = 'auto'; K.el.addEventListener('ended', next); next(); }
      return K.el;
    },
    play() { K.want = true; if (K.el && K.el.src) K.el.play().catch(() => {}); },
    pause() { K.want = false; if (K.el) K.el.pause(); },
    get current() { return K.cur >= 0 ? LIST[K.cur] : ''; },
  };
})();

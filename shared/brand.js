/* shared/brand.js: atlas merek fiktif bersama (Rencana tahap 27, docs/cooper-station/rencana-tahap-27-cooper-station.md).
   Skrip biasa (bukan modul) agar jalan dari file://, mengisi window.BRANDKIT. Tanpa three.js, tanpa aset luar.
   Semua merek fiktif buatan sendiri (bukan merek dunia nyata, bukan dari film). Logo digambar dari bentuk primitif kanvas.
   Isi:
     BRANDS                 tabel merek: id, name, sub { id, en } slogan, cjk (teks Jepang / Mandarin opsional), use (toko,
                            kantor, reklame, suburban, neon, lcd), warna bg / fg / ac / neon, logo, font
     KINDS                  tata letak atlas per jenis sel: plang 256 x 128 (siang), neon 256 x 128 (latar gelap, huruf menyala),
                            tegak 128 x 256 (papan vertikal / blade), logo 128 x 128 (atap, pilon, puncak menara)
     draw(canvas, lang)     menggambar atlas SIZE x SIZE ke kanvas (dibuat bila kosong), mengembalikan { canvas, avg }:
                            avg = Float32Array warna rata-rata sRGB 0..1 per sel (indeks cellIndex), untuk pudar jarak jauh
     cell(b, kind)          { x, y, w, h, u0, v0, u1, v1 } (uv konvensi WebGL flipY: v = 0 di bawah)
     cellIndex(b, kind)     indeks sel global (urutan KINDS lalu merek)
     pick(u, use)           merek deterministik dari bilangan 0..1 di antara merek dengan pemakaian `use`
   Sel bisa dihitung di shader: asal sel = (b % cols) * w, y0 + floor(b / cols) * h. Baris y 1536-2048 dicadangkan (LCD 27e). */
(function () {
  'use strict';
  const SIZE = 2048, TAU = Math.PI * 2;
  const KINDS = {
    plang: { y0: 0, w: 256, h: 128, cols: 8 },
    neon: { y0: 384, w: 256, h: 128, cols: 8 },
    tegak: { y0: 768, w: 128, h: 256, cols: 16 },
    logo: { y0: 1280, w: 128, h: 128, cols: 16 },
  };
  const FONTS = {
    sans: '"Helvetica Neue", Arial, "Liberation Sans", sans-serif',
    cond: '"Arial Narrow", "Roboto Condensed", "Liberation Sans Narrow", "Helvetica Neue", Arial, sans-serif',
    serif: 'Georgia, "Times New Roman", "Liberation Serif", serif',
    round: '"Trebuchet MS", Verdana, "DejaVu Sans", sans-serif',
    mono: '"Courier New", "Liberation Mono", monospace',
    cjk: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", Meiryo, "Microsoft YaHei", "PingFang SC", "Noto Sans CJK JP", "Noto Sans CJK SC", IPAGothic, sans-serif',
  };
  // bg latar plang siang, fg huruf, ac aksen logo, neon warna menyala malam
  const BRANDS = [
    { id: 'heliofarm', name: 'HELIOFARM', sub: { id: 'Sayur segar dari sunline', en: 'Fresh greens from the sunline' }, use: ['toko', 'reklame'], bg: '#1f6b3a', fg: '#f4f1e4', ac: '#b8e05a', neon: '#7dff6a', logo: 'leaf', font: 'sans' },
    { id: 'kopilingkar', name: 'KOPI LINGKAR', sub: { id: 'Diseduh searah putaran', en: 'Brewed with the spin' }, use: ['toko'], bg: '#3b2418', fg: '#f1dfc0', ac: '#d08a3c', neon: '#ffb45a', logo: 'cup', font: 'serif' },
    { id: 'bankcincin', name: 'BANK CINCIN', sub: { id: 'Tabungan di orbit stabil', en: 'Savings in a stable orbit' }, use: ['kantor', 'toko'], bg: '#14244a', fg: '#f3e2a4', ac: '#e0b84a', neon: '#ffd86a', logo: 'ring', font: 'serif' },
    { id: 'perisai', name: 'PERISAI', sub: { id: 'Asuransi radiasi & meteor', en: 'Radiation & meteor cover' }, use: ['kantor', 'reklame'], bg: '#0f5c63', fg: '#ffffff', ac: '#7fe3e0', neon: '#5ff4ff', logo: 'hex', font: 'cond' },
    { id: 'buihtitan', name: 'BUIH TITAN', sub: { id: 'Soda dingin dari es Titan', en: 'Cold soda from Titan ice' }, cjk: '泡', use: ['reklame', 'toko', 'neon'], bg: '#c4161c', fg: '#ffffff', ac: '#ffd23f', neon: '#ff3b4a', logo: 'bubbles', font: 'round' },
    { id: 'rotihub', name: 'ROTI HUB', sub: { id: 'Roti hangat tiap pagi', en: 'Warm bread every morning' }, use: ['toko'], bg: '#f2e3c6', fg: '#7a3b12', ac: '#d9822b', neon: '#ffa040', logo: 'wheat', font: 'serif' },
    { id: 'gowesspin', name: 'GOWES SPIN', sub: { id: 'Sepeda untuk 1 g', en: 'Bikes made for 1 g' }, use: ['toko'], bg: '#ffd200', fg: '#111111', ac: '#111111', neon: '#ffe600', logo: 'wheel', font: 'cond' },
    { id: 'cucikoriolis', name: 'CUCI KORIOLIS', sub: { id: 'Laundry kiloan berputar', en: 'Spin-cycle laundry' }, use: ['toko', 'suburban'], bg: '#dff1fb', fg: '#0d4f80', ac: '#2a9bd8', neon: '#52c8ff', logo: 'swirl', font: 'round' },
    { id: 'sehat1g', name: 'KLINIK SEHAT 1G', sub: { id: 'Buka 24 jam', en: 'Open 24 hours' }, use: ['toko', 'suburban'], bg: '#ffffff', fg: '#0b6b3a', ac: '#18a058', neon: '#3dff8a', logo: 'cross', font: 'sans' },
    { id: 'enceladus', name: 'ENCELADUS', sub: { id: 'Air murni dari bulan es', en: 'Pure water from an ice moon' }, use: ['reklame', 'toko'], bg: '#e8f6fb', fg: '#0a3d62', ac: '#3fb6dc', neon: '#7fe8ff', logo: 'drop', font: 'sans' },
    { id: 'miesaturnus', name: 'MIE SATURNUS', sub: { id: 'Mie kuah panas', en: 'Hot noodle soup' }, cjk: '土星拉麺', use: ['toko', 'neon'], bg: '#b3121b', fg: '#ffe9a8', ac: '#ffcc33', neon: '#ff5a2a', logo: 'bowl', font: 'cond' },
    { id: 'dok7', name: 'DOK 7 LOGISTIK', sub: { id: 'Kirim antar dek', en: 'Deck-to-deck delivery' }, use: ['kantor', 'reklame'], bg: '#1d1f22', fg: '#ff8a1e', ac: '#ff8a1e', neon: '#ff8a1e', logo: 'box', font: 'cond' },
    { id: 'jagungemas', name: 'JAGUNG EMAS', sub: { id: 'Camilan dari ladang Copper', en: 'Snacks from Copper fields' }, use: ['reklame', 'toko'], bg: '#f5b819', fg: '#4a2a05', ac: '#2f7a2a', neon: '#ffd23a', logo: 'corn', font: 'round' },
    { id: 'apoteksumbu', name: 'APOTEK SUMBU', sub: { id: 'Obat & vitamin', en: 'Medicine & vitamins' }, use: ['toko', 'suburban'], bg: '#0f7a5a', fg: '#ffffff', ac: '#ffffff', neon: '#4dffb8', logo: 'pill', font: 'sans' },
    { id: 'bukubintang', name: 'BUKU BINTANG', sub: { id: 'Buku & peta bintang', en: 'Books & star charts' }, use: ['toko'], bg: '#3a1f5c', fg: '#f6e7ff', ac: '#f2c94c', neon: '#c78bff', logo: 'book', font: 'serif' },
    { id: 'miniorbit', name: 'MINI ORBIT 24', sub: { id: 'Selalu buka', en: 'Always open' }, use: ['toko', 'suburban'], bg: '#ffffff', fg: '#d0202a', ac: '#1b8a3a', neon: '#ff3040', logo: 'bag', font: 'sans' },
    { id: 'soraramen', name: 'SORA RAMEN', sub: { id: 'Ramen gaya Jepang', en: 'Japanese-style ramen' }, cjk: '空ラーメン', use: ['toko', 'neon'], bg: '#111111', fg: '#f5efe2', ac: '#d6282e', neon: '#ff2e4d', logo: 'bowl', font: 'cjk' },
    { id: 'neondo', name: 'NEON-DO', sub: { id: 'Elektronik & suku cadang', en: 'Electronics & parts' }, cjk: 'ネオン堂', use: ['reklame', 'toko', 'neon', 'lcd'], bg: '#160b2e', fg: '#ff4fd8', ac: '#35f2ff', neon: '#ff4fd8', logo: 'bolt', font: 'cjk' },
    { id: 'huanxing', name: 'HUANXING', sub: { id: 'Peralatan rumah', en: 'Home appliances' }, cjk: '环星电器', use: ['kantor', 'reklame', 'neon'], bg: '#a8121a', fg: '#ffd56a', ac: '#ffd56a', neon: '#ff3a2e', logo: 'ringstar', font: 'cjk' },
    { id: 'tuxingcha', name: 'TUXING CHA', sub: { id: 'Teh susu & teh hijau', en: 'Milk tea & green tea' }, cjk: '土星茶', use: ['toko', 'neon'], bg: '#1e5e4e', fg: '#f1f6e8', ac: '#a9d98b', neon: '#6dffb0', logo: 'leaf', font: 'cjk' },
    { id: 'lumen9', name: 'LUMEN-9', sub: { id: 'Layar setipis cahaya', en: 'Screens thin as light' }, use: ['kantor', 'reklame', 'lcd'], bg: '#05080d', fg: '#4ff0ff', ac: '#4ff0ff', neon: '#4ff0ff', logo: 'grid', font: 'mono' },
    { id: 'kestrelwisata', name: 'KESTREL WISATA', sub: { id: 'Tur cincin Saturnus', en: 'Saturn ring tours' }, use: ['reklame', 'lcd'], bg: '#0d1f4a', fg: '#ffffff', ac: '#ff9a2e', neon: '#ffae4a', logo: 'planet', font: 'cond' },
    { id: 'kainsumbu', name: 'KAIN SUMBU', sub: { id: 'Busana kota silinder', en: 'Cylinder-city fashion' }, use: ['toko'], bg: '#f4f1ea', fg: '#141414', ac: '#141414', neon: '#ffffff', logo: 'tag', font: 'serif' },
    { id: 'nullg', name: 'NULL-G GYM', sub: { id: 'Latihan di 1 g penuh', en: 'Train at full 1 g' }, use: ['toko', 'suburban'], bg: '#1a1a1a', fg: '#c6ff1a', ac: '#c6ff1a', neon: '#c6ff1a', logo: 'dumbbell', font: 'cond' },
  ];

  // ---------- logo primitif (pusat cx, cy, jari-jari r) ----------
  function logo(g, kind, cx, cy, r, fg, ac) {
    g.save(); g.translate(cx, cy); g.lineJoin = 'round'; g.lineCap = 'round';
    const L = r * 0.13;                                              // tebal garis
    const circ = (x, y, rr, fill) => { g.beginPath(); g.arc(x, y, rr, 0, TAU); fill ? g.fill() : g.stroke(); };
    g.fillStyle = ac; g.strokeStyle = ac; g.lineWidth = L;
    switch (kind) {
      case 'leaf':
        g.beginPath(); g.moveTo(-r * 0.7, r * 0.7); g.bezierCurveTo(-r * 0.8, -r * 0.4, r * 0.1, -r * 0.9, r * 0.75, -r * 0.75);
        g.bezierCurveTo(r * 0.8, r * 0.1, r * 0.2, r * 0.8, -r * 0.7, r * 0.7); g.fill();
        g.strokeStyle = fg; g.lineWidth = L * 0.6; g.beginPath(); g.moveTo(-r * 0.7, r * 0.7); g.quadraticCurveTo(0, 0, r * 0.6, -r * 0.6); g.stroke(); break;
      case 'cup':
        g.beginPath(); g.moveTo(-r * 0.6, -r * 0.2); g.lineTo(r * 0.45, -r * 0.2); g.lineTo(r * 0.35, r * 0.6); g.lineTo(-r * 0.5, r * 0.6); g.closePath(); g.fill();
        g.lineWidth = L; circ(r * 0.55, r * 0.15, r * 0.22, false);
        g.strokeStyle = fg; g.lineWidth = L * 0.6;
        for (const x of [-0.3, 0, 0.3]) { g.beginPath(); g.moveTo(x * r - r * 0.1, -r * 0.4); g.quadraticCurveTo(x * r + r * 0.12, -r * 0.6, x * r - r * 0.05, -r * 0.85); g.stroke(); } break;
      case 'ring':
        g.lineWidth = L * 1.6; circ(0, 0, r * 0.62, false); g.lineWidth = L * 0.7; g.beginPath(); g.ellipse(0, 0, r * 0.95, r * 0.28, -0.35, 0, TAU); g.stroke(); break;
      case 'hex':
        g.beginPath(); for (let i = 0; i < 6; i++) { const a = i * TAU / 6 + Math.PI / 6; g.lineTo(Math.cos(a) * r * 0.85, Math.sin(a) * r * 0.85); } g.closePath(); g.fill();
        g.fillStyle = fg; g.beginPath(); g.moveTo(0, -r * 0.5); g.lineTo(r * 0.38, -r * 0.3); g.lineTo(r * 0.3, r * 0.2); g.lineTo(0, r * 0.52); g.lineTo(-r * 0.3, r * 0.2); g.lineTo(-r * 0.38, -r * 0.3); g.closePath(); g.fill(); break;
      case 'bubbles':
        circ(-r * 0.3, r * 0.25, r * 0.42, true); g.fillStyle = fg; circ(r * 0.35, -r * 0.3, r * 0.3, true); g.fillStyle = ac; circ(r * 0.45, r * 0.45, r * 0.18, true); circ(-r * 0.45, -r * 0.55, r * 0.14, true); break;
      case 'wheat':
        g.lineWidth = L * 0.7; g.beginPath(); g.moveTo(0, r * 0.9); g.lineTo(0, -r * 0.8); g.stroke();
        for (let k = 0; k < 4; k++) for (const s of [-1, 1]) { g.save(); g.translate(0, -r * 0.55 + k * r * 0.35); g.rotate(s * 0.6); g.beginPath(); g.ellipse(s * r * 0.2, 0, r * 0.26, r * 0.11, 0, 0, TAU); g.fill(); g.restore(); } break;
      case 'wheel':
        g.lineWidth = L * 1.3; circ(0, 0, r * 0.8, false); g.lineWidth = L * 0.45;
        for (let i = 0; i < 12; i++) { const a = i * TAU / 12; g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * r * 0.78, Math.sin(a) * r * 0.78); g.stroke(); } circ(0, 0, r * 0.14, true); break;
      case 'swirl':
        g.lineWidth = L; g.beginPath(); for (let t = 0; t < 1; t += 0.01) { const a = t * TAU * 2.2, rr = r * (0.1 + 0.75 * t); g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); } g.stroke(); break;
      case 'cross':
        g.fillRect(-r * 0.22, -r * 0.75, r * 0.44, r * 1.5); g.fillRect(-r * 0.75, -r * 0.22, r * 1.5, r * 0.44); break;
      case 'drop':
        g.beginPath(); g.moveTo(0, -r * 0.9); g.bezierCurveTo(r * 0.3, -r * 0.4, r * 0.65, 0, r * 0.62, r * 0.3); g.arc(0, r * 0.3, r * 0.62, 0, Math.PI);
        g.bezierCurveTo(-r * 0.65, 0, -r * 0.3, -r * 0.4, 0, -r * 0.9); g.fill(); g.fillStyle = fg; g.beginPath(); g.ellipse(-r * 0.22, r * 0.25, r * 0.1, r * 0.2, 0.3, 0, TAU); g.fill(); break;
      case 'bowl':
        g.beginPath(); g.moveTo(-r * 0.85, -r * 0.05); g.lineTo(r * 0.85, -r * 0.05); g.arc(0, -r * 0.05, r * 0.85, 0, Math.PI); g.fill();
        g.fillRect(-r * 0.3, r * 0.72, r * 0.6, r * 0.12);
        g.strokeStyle = fg; g.lineWidth = L * 0.6; g.beginPath(); g.moveTo(r * 0.2, -r * 0.9); g.lineTo(-r * 0.15, -r * 0.05); g.moveTo(r * 0.5, -r * 0.85); g.lineTo(r * 0.1, -r * 0.05); g.stroke(); break;
      case 'box':
        g.beginPath(); g.moveTo(0, -r * 0.8); g.lineTo(r * 0.75, -r * 0.4); g.lineTo(r * 0.75, r * 0.45); g.lineTo(0, r * 0.85); g.lineTo(-r * 0.75, r * 0.45); g.lineTo(-r * 0.75, -r * 0.4); g.closePath(); g.fill();
        g.strokeStyle = fg; g.lineWidth = L * 0.5; g.beginPath(); g.moveTo(-r * 0.75, -r * 0.4); g.lineTo(0, 0); g.lineTo(r * 0.75, -r * 0.4); g.moveTo(0, 0); g.lineTo(0, r * 0.85); g.stroke(); break;
      case 'corn':
        g.fillStyle = ac; g.beginPath(); g.moveTo(0, r * 0.9); g.quadraticCurveTo(-r * 0.9, r * 0.2, -r * 0.35, -r * 0.3); g.lineTo(0, r * 0.5); g.closePath(); g.fill();
        g.beginPath(); g.moveTo(0, r * 0.9); g.quadraticCurveTo(r * 0.9, r * 0.2, r * 0.35, -r * 0.3); g.lineTo(0, r * 0.5); g.closePath(); g.fill();
        g.fillStyle = fg; g.beginPath(); g.ellipse(0, -r * 0.15, r * 0.3, r * 0.7, 0, 0, TAU); g.fill(); break;
      case 'pill':
        g.save(); g.rotate(-0.7); g.beginPath(); g.arc(-r * 0.35, 0, r * 0.32, Math.PI / 2, Math.PI * 1.5); g.lineTo(r * 0.35, -r * 0.32); g.arc(r * 0.35, 0, r * 0.32, -Math.PI / 2, Math.PI / 2); g.closePath();
        g.lineWidth = L * 0.8; g.stroke(); g.beginPath(); g.arc(-r * 0.35, 0, r * 0.32, Math.PI / 2, Math.PI * 1.5); g.lineTo(0, -r * 0.32); g.lineTo(0, r * 0.32); g.closePath(); g.fill(); g.restore(); break;
      case 'book':
        g.beginPath(); g.moveTo(0, -r * 0.45); g.lineTo(-r * 0.85, -r * 0.65); g.lineTo(-r * 0.85, r * 0.55); g.lineTo(0, r * 0.75); g.lineTo(r * 0.85, r * 0.55); g.lineTo(r * 0.85, -r * 0.65); g.closePath(); g.fill();
        g.strokeStyle = fg; g.lineWidth = L * 0.4; g.beginPath(); g.moveTo(0, -r * 0.45); g.lineTo(0, r * 0.75); g.stroke();
        g.fillStyle = fg; star(g, r * 0.42, -r * 0.05, r * 0.22); break;
      case 'bag':
        g.fillRect(-r * 0.65, -r * 0.3, r * 1.3, r * 1.1); g.lineWidth = L * 0.8; g.beginPath(); g.arc(0, -r * 0.3, r * 0.35, Math.PI, 0); g.stroke();
        g.fillStyle = '#ffffff'; g.font = `bold ${Math.round(r * 0.6)}px ${FONTS.sans}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('24', 0, r * 0.28); break;
      case 'bolt':
        g.beginPath(); g.moveTo(r * 0.2, -r * 0.9); g.lineTo(-r * 0.5, r * 0.1); g.lineTo(-r * 0.02, r * 0.1); g.lineTo(-r * 0.25, r * 0.9); g.lineTo(r * 0.55, -r * 0.15); g.lineTo(r * 0.05, -r * 0.15); g.closePath(); g.fill(); break;
      case 'ringstar':
        g.lineWidth = L; circ(0, 0, r * 0.78, false); star(g, 0, 0, r * 0.48); break;
      case 'grid':
        for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) { g.globalAlpha = (i + j) % 2 ? 0.55 : 1; g.fillRect(-r * 0.75 + i * r * 0.52, -r * 0.75 + j * r * 0.52, r * 0.42, r * 0.42); } g.globalAlpha = 1; break;
      case 'planet':
        circ(0, 0, r * 0.5, true); g.strokeStyle = fg; g.lineWidth = L * 0.7; g.beginPath(); g.ellipse(0, 0, r * 0.95, r * 0.26, -0.4, 0.15, Math.PI - 0.15, true); g.stroke(); break;
      case 'tag':
        g.beginPath(); g.moveTo(-r * 0.75, -r * 0.35); g.lineTo(r * 0.35, -r * 0.35); g.lineTo(r * 0.8, 0); g.lineTo(r * 0.35, r * 0.35); g.lineTo(-r * 0.75, r * 0.35); g.closePath(); g.lineWidth = L * 0.7; g.stroke(); circ(r * 0.35, 0, r * 0.09, true); break;
      case 'dumbbell':
        g.fillRect(-r * 0.55, -r * 0.08, r * 1.1, r * 0.16); for (const s of [-1, 1]) { g.fillRect(s * r * 0.55 - r * 0.12, -r * 0.45, r * 0.24, r * 0.9); g.fillRect(s * r * 0.8 - r * 0.08, -r * 0.3, r * 0.16, r * 0.6); } break;
      default: circ(0, 0, r * 0.7, true);
    }
    g.restore();
  }
  function star(g, x, y, r) {
    g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.42 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill();
  }

  // teks dipersempit agar muat lebar maxW (tidak pernah diperbesar)
  function fitText(g, txt, x, y, maxW, size, font, weight = 'bold') {
    g.font = `${weight} ${size}px ${font}`;
    const w = g.measureText(txt).width;
    if (w > maxW) { g.save(); g.translate(x, y); g.scale(maxW / w, 1); g.fillText(txt, 0, 0); g.restore(); } else g.fillText(txt, x, y);
  }
  const hasCJK = (s) => /[぀-ヿ㐀-鿿]/.test(s);

  // ---------- sel ----------
  function cell(b, kind) {
    const K = KINDS[kind], x = (b % K.cols) * K.w, y = K.y0 + Math.floor(b / K.cols) * K.h;
    return { x, y, w: K.w, h: K.h, u0: x / SIZE, u1: (x + K.w) / SIZE, v0: 1 - (y + K.h) / SIZE, v1: 1 - y / SIZE };
  }
  const KIND_LIST = Object.keys(KINDS);
  const cellIndex = (b, kind) => KIND_LIST.indexOf(kind) * BRANDS.length + b;

  function drawPlang(g, B, c, lang) {                                // siang: latar warna merek, logo kiri, nama + slogan
    g.fillStyle = B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    g.strokeStyle = B.fg; g.globalAlpha = 0.35; g.lineWidth = 3; g.strokeRect(c.x + 5, c.y + 5, c.w - 10, c.h - 10); g.globalAlpha = 1;
    logo(g, B.logo, c.x + 52, c.y + 64, 38, B.fg, B.ac);
    g.fillStyle = B.fg; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    const font = FONTS[B.font] || FONTS.sans;
    fitText(g, B.name, c.x + 100, c.y + 66, c.w - 112, 36, font);
    g.globalAlpha = 0.85; fitText(g, B.sub[lang] || B.sub.id, c.x + 101, c.y + 94, c.w - 112, 17, FONTS.sans, '600'); g.globalAlpha = 1;
  }
  function drawNeon(g, B, c) {                                       // malam: latar hampir hitam, huruf tabung neon (CJK bila ada)
    g.fillStyle = '#07070a'; g.fillRect(c.x, c.y, c.w, c.h);
    const txt = B.cjk ? B.cjk : B.name, font = B.cjk ? FONTS.cjk : (FONTS[B.font] || FONTS.sans);
    g.save(); g.beginPath(); g.rect(c.x, c.y, c.w, c.h); g.clip();
    g.textAlign = 'center'; g.textBaseline = 'middle';
    for (const [blur, col, a] of [[22, B.neon, 0.9], [8, B.neon, 1], [0, '#ffffff', 0.85]]) {
      g.shadowColor = col; g.shadowBlur = blur; g.fillStyle = blur ? B.neon : col; g.globalAlpha = a;
      if (B.cjk) fitText(g, txt, c.x + c.w / 2, c.y + 58, c.w - 36, 62, font);
      else fitText(g, txt, c.x + c.w / 2, c.y + 64, c.w - 36, 46, font);
    }
    g.shadowBlur = 0; g.globalAlpha = 1;
    if (B.cjk) { g.fillStyle = B.neon; g.globalAlpha = 0.8; fitText(g, B.name, c.x + c.w / 2, c.y + 106, c.w - 60, 16, FONTS.sans); g.globalAlpha = 1; }
    g.restore();
  }
  function drawTegak(g, B, c) {                                      // papan vertikal: logo atas, huruf ditumpuk (CJK) atau diputar 90 derajat
    const dark = !!B.cjk;
    g.fillStyle = dark ? '#0b0b10' : B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    g.strokeStyle = dark ? B.neon : B.fg; g.globalAlpha = 0.5; g.lineWidth = 3; g.strokeRect(c.x + 5, c.y + 5, c.w - 10, c.h - 10); g.globalAlpha = 1;
    logo(g, B.logo, c.x + 64, c.y + 40, 26, dark ? B.neon : B.fg, dark ? B.neon : B.ac);
    g.fillStyle = dark ? B.neon : B.fg; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (B.cjk) {
      const ch = [...B.cjk], step = Math.min(44, 172 / ch.length);   // 78-250 px: muat di sel
      if (dark) { g.shadowColor = B.neon; g.shadowBlur = 10; }
      ch.forEach((k, i) => {
        const y = c.y + 78 + step * (i + 0.5), sz = Math.round(step * 0.9);
        if (k === 'ー') { g.save(); g.translate(c.x + 64, y); g.rotate(Math.PI / 2); fitText(g, k, 0, 0, 100, sz, FONTS.cjk); g.restore(); }   // tanda panjang tegak di tulisan vertikal
        else fitText(g, k, c.x + 64, y, 100, sz, FONTS.cjk);
      });
      g.shadowBlur = 0;
    } else {
      g.save(); g.translate(c.x + 64, c.y + 160); g.rotate(-Math.PI / 2);
      fitText(g, B.name, 0, 0, 170, 40, FONTS[B.font] || FONTS.sans); g.restore();
    }
  }
  function drawLogo(g, B, c) {                                       // kotak: logo besar di lingkaran warna merek
    g.fillStyle = B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    logo(g, B.logo, c.x + 64, c.y + 64, 50, B.fg, B.ac);
  }

  function draw(canvas, lang = 'id') {
    if (!canvas) canvas = document.createElement('canvas');
    canvas.width = SIZE; canvas.height = SIZE;
    const g = canvas.getContext('2d', { willReadFrequently: true });
    g.clearRect(0, 0, SIZE, SIZE); g.fillStyle = '#000'; g.fillRect(0, 0, SIZE, SIZE);
    const clip = (fn, B, c) => { g.save(); g.beginPath(); g.rect(c.x, c.y, c.w, c.h); g.clip(); fn(g, B, c, lang); g.restore(); };   // tiap sel tidak bocor ke tetangga
    BRANDS.forEach((B, b) => {
      clip(drawPlang, B, cell(b, 'plang')); clip(drawNeon, B, cell(b, 'neon'));
      clip(drawTegak, B, cell(b, 'tegak')); clip(drawLogo, B, cell(b, 'logo'));
    });
    // warna rata-rata per sel (sRGB 0..1), sampel tiap 4 piksel; dibaca dari kanvas 2D di CPU (bukan GPU)
    const avg = new Float32Array(KIND_LIST.length * BRANDS.length * 3);
    KIND_LIST.forEach((kind) => BRANDS.forEach((B, b) => {
      const c = cell(b, kind), d = g.getImageData(c.x, c.y, c.w, c.h).data; let r = 0, gg = 0, bb = 0, n = 0;
      for (let y = 2; y < c.h; y += 4) for (let x = 2; x < c.w; x += 4) { const i = (y * c.w + x) * 4; r += d[i]; gg += d[i + 1]; bb += d[i + 2]; n++; }
      const k = cellIndex(b, kind) * 3; avg[k] = r / n / 255; avg[k + 1] = gg / n / 255; avg[k + 2] = bb / n / 255;
    }));
    return { canvas, avg };
  }

  // merek deterministik dari u (0..1) di antara merek dengan pemakaian `use`
  const BY_USE = {};
  for (const B of BRANDS) for (const u of B.use) (BY_USE[u] = BY_USE[u] || []).push(BRANDS.indexOf(B));
  function pick(u, use = 'toko') {
    const L = BY_USE[use] || BRANDS.map((_, i) => i);
    return L[Math.min(L.length - 1, Math.floor(Math.max(0, u) * L.length))];
  }

  window.BRANDKIT = { SIZE, KINDS, FONTS, BRANDS, BY_USE, draw, cell, cellIndex, pick, logo, hasCJK };
})();

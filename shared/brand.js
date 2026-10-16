/* shared/brand.js: atlas merek fiktif bersama (Rencana tahap 27, docs/cooper-station/rencana-tahap-27-cooper-station.md).
   Skrip biasa (bukan modul) agar jalan dari file://, mengisi window.BRANDKIT. Tanpa three.js, tanpa aset luar.
   Semua merek fiktif buatan sendiri (bukan merek dunia nyata, bukan dari film). Logo digambar dari bentuk primitif kanvas.
   Plang di dunia game memakai bahasa distrik, tidak ikut bahasa UI dan tidak dalam bahasa Indonesia (permintaan Bhakti):
   merek global berbahasa English, merek lokal berbahasa distriknya (DISTRICT_LANG).
   Isi:
     BRANDS                 tabel merek: id, name (Latin / alih aksara), local (teks aksara asli bila bukan Latin), sub (slogan dalam
                            bahasa merek), lang ('en' global, 'ja', 'zh', 'ar', 'hi', 'ru', 'uk', 'de', 'it', 'pl', 'el', 'es', 'vi',
                            'uz'), use (toko, kantor, reklame, suburban, neon, lcd), warna bg / fg / ac / neon, logo, font
     DISTRICT_LANG          nama distrik Copper -> bahasa plang lokal (distrik lain / di luar distrik = 'en')
     KINDS                  tata letak atlas per jenis sel: plang 256 x 128 (siang), neon 256 x 128 (latar gelap, huruf menyala),
                            tegak 128 x 256 (papan vertikal / blade), logo 128 x 128 (atap, pilon, puncak menara)
     draw(canvas)           menggambar atlas W x H (2048 x 4096) ke kanvas (dibuat bila kosong), mengembalikan { canvas, avg }:
                            avg = Float32Array warna rata-rata sRGB 0..1 per sel (indeks cellIndex), untuk pudar jarak jauh
     cell(b, kind)          { x, y, w, h, u0, v0, u1, v1 } (uv konvensi WebGL flipY: v = 0 di bawah)
     cellIndex(b, kind)     indeks sel global (urutan KINDS lalu merek)
     pick(u, use, district) merek deterministik dari u (0..1): di distrik berbahasa X sekitar 60% merek lokal X + 40% merek global,
                            distrik berbahasa English hanya merek global
   Sel bisa dihitung di shader: asal sel = (b % cols) * w, y0 + floor(b / cols) * h. Baris y 2688-4096 dicadangkan (LCD 27e). */
(function () {
  'use strict';
  const W = 2048, H = 4096, SIZE = W, TAU = Math.PI * 2;
  const KINDS = {
    plang: { y0: 0, w: 256, h: 128, cols: 8 },
    neon: { y0: 768, w: 256, h: 128, cols: 8 },
    tegak: { y0: 1536, w: 128, h: 256, cols: 16 },
    logo: { y0: 2304, w: 128, h: 128, cols: 16 },
  };
  const FONTS = {
    sans: '"Helvetica Neue", Arial, "Liberation Sans", sans-serif',
    cond: '"Arial Narrow", "Roboto Condensed", "Liberation Sans Narrow", "Helvetica Neue", Arial, sans-serif',
    serif: 'Georgia, "Times New Roman", "Liberation Serif", serif',
    round: '"Trebuchet MS", Verdana, "DejaVu Sans", sans-serif',
    mono: '"Courier New", "Liberation Mono", monospace',
    cjk: '"Hiragino Sans", "Hiragino Kaku Gothic ProN", "Yu Gothic", Meiryo, "Microsoft YaHei", "PingFang SC", "Noto Sans CJK JP", "Noto Sans CJK SC", IPAGothic, sans-serif',
    ar: '"Geeza Pro", "Segoe UI", Tahoma, Arial, "Noto Naskh Arabic", "Noto Sans Arabic", FreeSerif, sans-serif',
    hi: '"Nirmala UI", Mangal, "Kohinoor Devanagari", "Devanagari Sangam MN", "Noto Sans Devanagari", FreeSerif, sans-serif',
  };
  const DISTRICT_LANG = {
    'New York': 'en', Sagan: 'en', Chandrasekhar: 'en', Iowa: 'en', Tokyo: 'ja', Shanghai: 'zh',
    Kairo: 'ar', 'Al-Battani': 'ar', 'Taman Nil': 'ar', Delhi: 'hi', Punjab: 'hi', Tsiolkovsky: 'ru', Ukraina: 'uk',
    Kepler: 'de', Galileo: 'it', Copernicus: 'pl', Hypatia: 'el', Pampas: 'es', 'Taman Mekong': 'vi', 'Ulugh Beg': 'uz',
  };
  const b = (id, name, lang, sub, use, bg, fg, ac, neon, logo, font, local) => ({ id, name, lang, sub, use, bg, fg, ac, neon, logo, font, local });
  // bg latar plang siang, fg huruf, ac aksen logo, neon warna menyala malam
  const BRANDS = [
    // merek global (English), dipakai di semua distrik
    b('heliofarm', 'HELIOFARM', 'en', 'Greens grown on the sunline', ['toko', 'reklame'], '#1f6b3a', '#f4f1e4', '#b8e05a', '#7dff6a', 'leaf', 'sans'),
    b('ringroast', 'RING ROAST COFFEE', 'en', 'Brewed with the spin', ['toko'], '#3b2418', '#f1dfc0', '#d08a3c', '#ffb45a', 'cup', 'serif'),
    b('ringbank', 'RINGBANK', 'en', 'Savings in a stable orbit', ['kantor', 'toko'], '#14244a', '#f3e2a4', '#e0b84a', '#ffd86a', 'ring', 'serif'),
    b('shieldline', 'SHIELDLINE', 'en', 'Radiation & meteor cover', ['kantor', 'reklame'], '#0f5c63', '#ffffff', '#7fe3e0', '#5ff4ff', 'hex', 'cond'),
    b('titanfizz', 'TITAN FIZZ', 'en', 'Cold soda from Titan ice', ['reklame', 'toko', 'neon'], '#c4161c', '#ffffff', '#ffd23f', '#ff3b4a', 'bubbles', 'round'),
    b('hubbakery', 'HUB BAKERY', 'en', 'Fresh bread every morning', ['toko', 'suburban'], '#f2e3c6', '#7a3b12', '#d9822b', '#ffa040', 'wheat', 'serif'),
    b('spincycles', 'SPIN CYCLES', 'en', 'Bikes built for 1 g', ['toko'], '#ffd200', '#111111', '#111111', '#ffe600', 'wheel', 'cond'),
    b('coriolis', 'CORIOLIS LAUNDRY', 'en', 'Spin-cycle laundry', ['toko', 'suburban'], '#dff1fb', '#0d4f80', '#2a9bd8', '#52c8ff', 'swirl', 'round'),
    b('clinic1g', '1G CLINIC', 'en', 'Open 24 hours', ['toko', 'suburban'], '#ffffff', '#0b6b3a', '#18a058', '#3dff8a', 'cross', 'sans'),
    b('enceladus', 'ENCELADUS', 'en', 'Pure water from an ice moon', ['reklame', 'toko'], '#e8f6fb', '#0a3d62', '#3fb6dc', '#7fe8ff', 'drop', 'sans'),
    b('dock7', 'DOCK 7 LOGISTICS', 'en', 'Deck-to-deck delivery', ['kantor', 'reklame'], '#1d1f22', '#ff8a1e', '#ff8a1e', '#ff8a1e', 'box', 'cond'),
    b('goldencorn', 'GOLDEN CORN', 'en', 'Snacks from Copper fields', ['reklame', 'toko'], '#f5b819', '#4a2a05', '#2f7a2a', '#ffd23a', 'corn', 'round'),
    b('axispharm', 'AXIS PHARMACY', 'en', 'Medicine & vitamins', ['toko', 'suburban'], '#0f7a5a', '#ffffff', '#ffffff', '#4dffb8', 'pill', 'sans'),
    b('starlight', 'STARLIGHT BOOKS', 'en', 'Books & star charts', ['toko'], '#3a1f5c', '#f6e7ff', '#f2c94c', '#c78bff', 'book', 'serif'),
    b('orbitmart', 'ORBIT MART 24', 'en', 'Always open', ['toko', 'suburban'], '#ffffff', '#d0202a', '#1b8a3a', '#ff3040', 'bag', 'sans'),
    b('lumen9', 'LUMEN-9', 'en', 'Screens thin as light', ['kantor', 'reklame', 'lcd'], '#05080d', '#4ff0ff', '#4ff0ff', '#4ff0ff', 'grid', 'mono'),
    b('kestrel', 'KESTREL TOURS', 'en', 'Saturn ring tours', ['reklame', 'lcd'], '#0d1f4a', '#ffffff', '#ff9a2e', '#ffae4a', 'planet', 'cond'),
    b('axisatelier', 'AXIS ATELIER', 'en', 'Cylinder-city fashion', ['toko'], '#f4f1ea', '#141414', '#141414', '#ffffff', 'tag', 'serif'),
    b('nullg', 'NULL-G GYM', 'en', 'Train at full 1 g', ['toko', 'suburban'], '#1a1a1a', '#c6ff1a', '#c6ff1a', '#c6ff1a', 'dumbbell', 'cond'),
    // Jepang (Tokyo)
    b('soraramen', 'SORA RAMEN', 'ja', '本格醤油ラーメン', ['toko', 'neon'], '#111111', '#f5efe2', '#d6282e', '#ff2e4d', 'bowl', 'cjk', '空ラーメン'),
    b('neondo', 'NEON-DO', 'ja', '電子部品・修理', ['reklame', 'toko', 'neon', 'lcd'], '#160b2e', '#ff4fd8', '#35f2ff', '#ff4fd8', 'bolt', 'cjk', 'ネオン堂'),
    b('hoshikissa', 'HOSHI KISSA', 'ja', '珈琲と甘味', ['toko', 'neon'], '#2b1a12', '#f6e2b8', '#e3a94b', '#ffc46a', 'cup', 'cjk', '星喫茶'),
    // Mandarin (Shanghai)
    b('huanxing', 'HUANXING', 'zh', '家用电器', ['kantor', 'reklame', 'neon'], '#a8121a', '#ffd56a', '#ffd56a', '#ff3a2e', 'ringstar', 'cjk', '环星电器'),
    b('tuxingcha', 'TUXING CHA', 'zh', '奶茶 · 绿茶', ['toko', 'neon'], '#1e5e4e', '#f1f6e8', '#a9d98b', '#6dffb0', 'leaf', 'cjk', '土星茶'),
    b('tuxingmian', 'TUXING MIANGUAN', 'zh', '手工拉面', ['toko', 'neon'], '#b3121b', '#ffe9a8', '#ffcc33', '#ff5a2a', 'bowl', 'cjk', '土星面馆'),
    // Arab (Kairo, Al-Battani, Taman Nil)
    b('halqa', 'MAQHA AL-HALQA', 'ar', 'قهوة وشاي', ['toko', 'neon'], '#123a3a', '#f3e6c4', '#d8a64a', '#ffcf6a', 'cup', 'ar', 'مقهى الحلقة'),
    b('mihwar', 'SAYDALIYAT AL-MIHWAR', 'ar', 'مفتوح ٢٤ ساعة', ['toko', 'suburban'], '#ffffff', '#0d6b4a', '#18a06a', '#3dffa0', 'cross', 'ar', 'صيدلية المحور'),
    b('makhbaznil', 'MAKHBAZ AN-NIL', 'ar', 'خبز طازج كل صباح', ['toko', 'suburban'], '#e9d7b0', '#5a2e10', '#c47a2c', '#ffa448', 'wheat', 'ar', 'مخبز النيل'),
    // Hindi (Delhi, Punjab)
    b('chakrachai', 'CHAKRA CHAI', 'hi', 'मसाला चाय', ['toko', 'neon'], '#7a1f12', '#ffe6b0', '#f2a33a', '#ff9a3a', 'cup', 'hi', 'चक्र चाय'),
    b('taramithai', 'TARA MITHAI', 'hi', 'मिठाई और नमकीन', ['toko', 'suburban'], '#f7c531', '#6a1a3a', '#c2185b', '#ffd23a', 'ringstar', 'hi', 'तारा मिठाई'),
    // Rusia (Tsiolkovsky)
    b('orbitakhleb', 'ORBITA KHLEB', 'ru', 'Свежий хлеб', ['toko', 'suburban'], '#f0e2c0', '#6b2b0c', '#c4762a', '#ffa040', 'wheat', 'sans', 'ОРБИТА ХЛЕБ'),
    b('aptekaos', 'APTEKA OS', 'ru', 'Круглосуточно', ['toko', 'suburban'], '#0f5f8a', '#ffffff', '#7fd4ff', '#52c8ff', 'cross', 'sans', 'АПТЕКА ОСЬ'),
    // Ukraina (Ukraina)
    b('zoryana', 'ZORYANA KAVA', 'uk', 'Кава та випічка', ['toko'], '#16326b', '#ffd84a', '#ffd84a', '#ffe060', 'cup', 'serif', 'ЗОРЯНА КАВА'),
    b('poleagro', 'POLE AGRO', 'uk', 'Насіння та добрива', ['toko', 'suburban'], '#2f6b1f', '#fff3c4', '#f2c230', '#b8ff5a', 'leaf', 'cond', 'ПОЛЕ АГРО'),
    // Jerman (Kepler)
    b('keplerapo', 'KEPLER APOTHEKE', 'de', 'Tag und Nacht', ['toko', 'suburban'], '#ffffff', '#c8102e', '#c8102e', '#ff3a4a', 'pill', 'sans'),
    b('baeckerei', 'BÄCKEREI ORBIT', 'de', 'Frisch gebacken', ['toko'], '#3a2a1a', '#f3dfb5', '#d9a04a', '#ffc060', 'wheat', 'serif'),
    // Italia (Galileo)
    b('caffeanello', 'CAFFÈ ANELLO', 'it', 'Espresso al banco', ['toko', 'neon'], '#0f3d2e', '#f4ead2', '#c9a14a', '#ffd07a', 'cup', 'serif'),
    b('trattoria', 'TRATTORIA ORBITA', 'it', 'Cucina di casa', ['toko'], '#8a1c1c', '#fbeedd', '#f2c94c', '#ff6a4a', 'bowl', 'serif'),
    // Polandia (Copernicus)
    b('piekarnia', 'PIEKARNIA ORBITA', 'pl', 'Świeże pieczywo', ['toko', 'suburban'], '#f4e6c8', '#7a2e12', '#c97a2a', '#ffa448', 'wheat', 'serif'),
    b('gwiazda', 'KWIACIARNIA GWIAZDA', 'pl', 'Kwiaty i rośliny', ['toko'], '#f6d6e2', '#7a1f4a', '#2f7a3a', '#ff7ab8', 'leaf', 'round'),
    // Yunani (Hypatia)
    b('fournos', 'FOURNOS TROCHIA', 'el', 'Φρέσκο ψωμί', ['toko', 'suburban'], '#1d4f91', '#ffffff', '#ffffff', '#6ab8ff', 'wheat', 'sans', 'ΦΟΥΡΝΟΣ ΤΡΟΧΙΑ'),
    b('kafeneio', 'KAFENEIO DAKTYLIOS', 'el', 'Ελληνικός καφές', ['toko'], '#f4efe4', '#1d4f91', '#1d4f91', '#6ab8ff', 'cup', 'serif', 'ΚΑΦΕΝΕΙΟ ΔΑΚΤΥΛΙΟΣ'),
    // Spanyol (Pampas)
    b('panaderia', 'PANADERÍA LA ÓRBITA', 'es', 'Pan del día', ['toko', 'suburban'], '#f2dfb4', '#7a3410', '#d4822b', '#ffa448', 'wheat', 'serif'),
    b('parrilla', 'PARRILLA EL ANILLO', 'es', 'Carnes a la brasa', ['toko'], '#2a1410', '#ffcf8a', '#e2552a', '#ff6a3a', 'ring', 'cond'),
    // Vietnam (Taman Mekong)
    b('phovanhdai', 'PHỞ VÀNH ĐAI', 'vi', 'Phở bò truyền thống', ['toko', 'neon'], '#c8102e', '#fff3c4', '#ffd23a', '#ff4a3a', 'bowl', 'sans'),
    b('caphesao', 'CÀ PHÊ SAO', 'vi', 'Cà phê sữa đá', ['toko'], '#2b1a12', '#f6e2b8', '#e3a94b', '#ffc46a', 'cup', 'round'),
    // Uzbek (Ulugh Beg)
    b('nonuyi', 'NON UYI', 'uz', 'Issiq non', ['toko', 'suburban'], '#1f5aa6', '#ffffff', '#f2c230', '#6ab8ff', 'wheat', 'round'),
    b('choyxona', 'CHOYXONA YULDUZ', 'uz', 'Choy va palov', ['toko'], '#0f6b6b', '#f7e9c4', '#e2a73a', '#ffcf6a', 'ringstar', 'serif'),
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
  function cell(i, kind) {
    const K = KINDS[kind], x = (i % K.cols) * K.w, y = K.y0 + Math.floor(i / K.cols) * K.h;
    return { x, y, w: K.w, h: K.h, u0: x / W, u1: (x + K.w) / W, v0: 1 - (y + K.h) / H, v1: 1 - y / H };
  }
  const KIND_LIST = Object.keys(KINDS);
  const cellIndex = (i, kind) => KIND_LIST.indexOf(kind) * BRANDS.length + i;
  const text = (B) => B.local || B.name;                             // teks utama plang (aksara asli bila ada)
  const fontOf = (B) => B.lang === 'ja' || B.lang === 'zh' ? FONTS.cjk : B.lang === 'ar' ? FONTS.ar : B.lang === 'hi' ? FONTS.hi : (FONTS[B.font] || FONTS.sans);
  const subFont = (B) => B.lang === 'ja' || B.lang === 'zh' ? FONTS.cjk : B.lang === 'ar' ? FONTS.ar : B.lang === 'hi' ? FONTS.hi : FONTS.sans;
  const dirOf = (g, B) => { g.direction = B.lang === 'ar' ? 'rtl' : 'ltr'; };

  function drawPlang(g, B, c) {                                      // siang: latar warna merek, logo kiri, nama + slogan
    g.fillStyle = B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    g.strokeStyle = B.fg; g.globalAlpha = 0.35; g.lineWidth = 3; g.strokeRect(c.x + 5, c.y + 5, c.w - 10, c.h - 10); g.globalAlpha = 1;
    logo(g, B.logo, c.x + 52, c.y + 64, 38, B.fg, B.ac);
    dirOf(g, B); g.fillStyle = B.fg; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    fitText(g, text(B), c.x + 100, c.y + 66, c.w - 112, 36, fontOf(B));
    g.globalAlpha = 0.85; fitText(g, B.sub, c.x + 101, c.y + 94, c.w - 112, 17, subFont(B), '600'); g.globalAlpha = 1;
    g.direction = 'ltr';
  }
  function drawNeon(g, B, c) {                                       // malam: latar hampir hitam, huruf tabung neon
    g.fillStyle = '#07070a'; g.fillRect(c.x, c.y, c.w, c.h);
    const big = B.lang === 'ja' || B.lang === 'zh';
    dirOf(g, B); g.textAlign = 'center'; g.textBaseline = 'middle';
    for (const [blur, col, a] of [[22, B.neon, 0.9], [8, B.neon, 1], [0, '#ffffff', 0.85]]) {
      g.shadowColor = col; g.shadowBlur = blur; g.fillStyle = blur ? B.neon : col; g.globalAlpha = a;
      fitText(g, text(B), c.x + c.w / 2, c.y + (B.local ? 58 : 64), c.w - 36, big ? 62 : 46, fontOf(B));
    }
    g.shadowBlur = 0; g.globalAlpha = 1; g.direction = 'ltr';
    if (B.local) { g.fillStyle = B.neon; g.globalAlpha = 0.8; fitText(g, B.name, c.x + c.w / 2, c.y + 106, c.w - 60, 16, FONTS.sans); g.globalAlpha = 1; }   // alih aksara kecil
  }
  function drawTegak(g, B, c) {                                      // papan vertikal: logo atas, huruf ditumpuk (CJK) atau diputar 90 derajat
    const cjk = B.lang === 'ja' || B.lang === 'zh', dark = cjk;
    g.fillStyle = dark ? '#0b0b10' : B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    g.strokeStyle = dark ? B.neon : B.fg; g.globalAlpha = 0.5; g.lineWidth = 3; g.strokeRect(c.x + 5, c.y + 5, c.w - 10, c.h - 10); g.globalAlpha = 1;
    logo(g, B.logo, c.x + 64, c.y + 40, 26, dark ? B.neon : B.fg, dark ? B.neon : B.ac);
    g.fillStyle = dark ? B.neon : B.fg; g.textAlign = 'center'; g.textBaseline = 'middle';
    if (cjk) {
      const ch = [...B.local], step = Math.min(44, 172 / ch.length);   // 78-250 px: muat di sel
      g.shadowColor = B.neon; g.shadowBlur = 10;
      ch.forEach((k, i) => {
        const y = c.y + 78 + step * (i + 0.5), sz = Math.round(step * 0.9);
        if (k === 'ー') { g.save(); g.translate(c.x + 64, y); g.rotate(Math.PI / 2); fitText(g, k, 0, 0, 100, sz, FONTS.cjk); g.restore(); }   // tanda panjang tegak di tulisan vertikal
        else fitText(g, k, c.x + 64, y, 100, sz, FONTS.cjk);
      });
      g.shadowBlur = 0;
    } else {
      dirOf(g, B); g.save(); g.translate(c.x + 64, c.y + 160); g.rotate(-Math.PI / 2);
      fitText(g, text(B), 0, 0, 170, 40, fontOf(B)); g.restore(); g.direction = 'ltr';
    }
  }
  function drawLogo(g, B, c) {                                       // kotak: logo besar di warna merek
    g.fillStyle = B.bg; g.fillRect(c.x, c.y, c.w, c.h);
    logo(g, B.logo, c.x + 64, c.y + 64, 50, B.fg, B.ac);
  }

  function draw(canvas) {
    if (!canvas) canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const g = canvas.getContext('2d', { willReadFrequently: true });
    g.clearRect(0, 0, W, H); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
    const clip = (fn, B, c) => { g.save(); g.beginPath(); g.rect(c.x, c.y, c.w, c.h); g.clip(); fn(g, B, c); g.restore(); };   // tiap sel tidak bocor ke tetangga
    BRANDS.forEach((B, i) => {
      clip(drawPlang, B, cell(i, 'plang')); clip(drawNeon, B, cell(i, 'neon'));
      clip(drawTegak, B, cell(i, 'tegak')); clip(drawLogo, B, cell(i, 'logo'));
    });
    // warna rata-rata per sel (sRGB 0..1), sampel tiap 4 piksel; dibaca dari kanvas 2D di CPU (bukan GPU)
    const avg = new Float32Array(KIND_LIST.length * BRANDS.length * 3);
    KIND_LIST.forEach((kind) => BRANDS.forEach((B, i) => {
      const c = cell(i, kind), d = g.getImageData(c.x, c.y, c.w, c.h).data; let r = 0, gg = 0, bb = 0, n = 0;
      for (let y = 2; y < c.h; y += 4) for (let x = 2; x < c.w; x += 4) { const k = (y * c.w + x) * 4; r += d[k]; gg += d[k + 1]; bb += d[k + 2]; n++; }
      const k = cellIndex(i, kind) * 3; avg[k] = r / n / 255; avg[k + 1] = gg / n / 255; avg[k + 2] = bb / n / 255;
    }));
    return { canvas, avg };
  }

  // daftar indeks merek per (bahasa, pemakaian)
  const POOL = {};
  BRANDS.forEach((B, i) => { for (const u of B.use) { const k = B.lang + ':' + u; (POOL[k] = POOL[k] || []).push(i); } });
  const BY_USE = {};
  BRANDS.forEach((B, i) => { for (const u of B.use) (BY_USE[u] = BY_USE[u] || []).push(i); });
  const at = (L, u) => L[Math.min(L.length - 1, Math.floor(Math.max(0, u) * L.length))];
  // merek deterministik dari u (0..1); district = nama distrik Copper atau null
  function pick(u, use = 'toko', district = null) {
    const lang = DISTRICT_LANG[district] || 'en', glob = POOL['en:' + use] || BY_USE[use] || BRANDS.map((_, i) => i), loc = POOL[lang + ':' + use];
    if (lang === 'en' || !loc) return at(glob, u);
    return u < 0.6 ? at(loc, u / 0.6) : at(glob, (u - 0.6) / 0.4);
  }

  window.BRANDKIT = { W, H, SIZE, KINDS, FONTS, BRANDS, DISTRICT_LANG, BY_USE, POOL, draw, cell, cellIndex, pick, logo, hasCJK };
})();

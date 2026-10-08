"""Uji 18b (Copper Corn Station): dek pandang menara ikon, E naik/turun, lempar dan jatuhkan bola dari 175 m, plus revisi bangunan.
- 18b-2: dek = teras keliling di atap tingkat 4 (175 m) di sekitar tingkat puncak; g lokal = 1 - h/R; pemain tidak bisa
  keluar pagar atau masuk badan tingkat puncak.
- Aksi E di lobi -> langsung di dek (tanpa lift); E di mana saja di dek -> langsung ke lobi.
- Bola dijatuhkan dari luar pagar: titik jatuh dibandingkan hitungan analitik kerangka inersia (bola bergerak lurus
  dengan kecepatan tepi omega x r0), selisih di bawah 5%; belokan jauh lebih besar daripada jatuh dari 20 m di tanah.
- Gereja: menara punya pintu (depan -za). Pasar besar: atap lengkung menempel dinding (dasar 6,2 m, jari-jari 12 m).
- Rumah Cooper: jendela kaca bening (transparan) di lubang dinding sungguhan.
Pakai: python tools/uji_menara.py   (butuh: pip install playwright && playwright install chromium)"""
import asyncio, pathlib
from playwright.async_api import async_playwright

UJI = r"""
(async () => {
  const S = window.__station, out = {}, wait = (ms) => new Promise((r) => setTimeout(r, ms)), D = S.DECK, R = S.R, P = S.player;
  const OM = S.OMEGA, wrap = (x) => { const C = 2 * Math.PI * R; return ((x % C) + C * 1.5) % C - C / 2; };
  out[`dek pandang di ${D.h.toFixed(1)} m (s ${D.s.toFixed(0)}, za ${D.za.toFixed(0)})`] = D.h > 170 && D.h < 180 && D.half > D.inner;
  // E dari lobi
  S.teleport('nyc'); await wait(300);
  P.theta = D.s / R; P.za = D.za - D.podD / 2 - 1.5; P.h = 0; P.state = 'ground'; P.deck = false;
  const a = S.availableAction();
  out[`aksi di lobi: ${a ? a.key : 'tidak ada'}`] = !!a && a.key === 'tower';
  S.doAction();
  out[`tiba di dek: state ${P.state}, dek ${P.deck}, h ${P.h.toFixed(1)} m, g lokal ${S.localG().toFixed(4)} (1 - h/R = ${(1 - P.h / R).toFixed(4)})`] =
    P.state === 'ground' && P.deck === true && Math.abs(P.h - D.h) < 0.01 && Math.abs(S.localG() - (1 - P.h / R)) < 0.002;
  // berjalan maju terus: tetap di dalam pagar, tidak masuk badan tingkat puncak
  S.input.auto = true;
  for (const hd of [Math.PI, 0.3, 1.9, -1.2]) { P.heading = hd; for (let i = 0; i < 120; i++) S.physicsStep(0.1); }
  S.input.auto = false;
  const K = (R - D.h) / R;                                          // 23j: busur lantai -> meter sebenarnya di ketinggian dek
  const ds = wrap(P.theta * R - D.s) * K, dz = P.za - D.za;
  out[`jalan 48 s di dek: posisi (${ds.toFixed(1)}, ${dz.toFixed(1)}) m dari pusat, h ${P.h.toFixed(1)}`] =
    Math.abs(ds) <= D.half - 0.49 && Math.abs(dz) <= D.half - 0.49 && Math.max(Math.abs(ds), Math.abs(dz)) >= D.inner + 0.34 && Math.abs(P.h - D.h) < 0.01;
  // 23j: sisi yang menghadap lengkungan (+-s) bisa mepet pagar seperti sisi end cap (+-za)
  const reach = [];
  for (const [hd, ax] of [[Math.PI / 2, 's'], [-Math.PI / 2, 's'], [0, 'z'], [Math.PI, 'z']]) {
    S.goDeck(); P.za = D.za + (hd === 0 ? 1 : -1) * (D.half + D.inner) / 2; P.theta = D.s / R; for (let i = 0; i < 5; i++) S.physicsStep(0.1);
    P.heading = hd; S.input.auto = true; for (let i = 0; i < 60; i++) S.physicsStep(0.1); S.input.auto = false;
    reach.push(D.half - (ax === 's' ? Math.abs(wrap(P.theta * R - D.s) * K) : Math.abs(P.za - D.za)));
  }
  out[`jarak ke pagar di 4 sisi (+s, -s, +za, -za): ${reach.map((x) => x.toFixed(2)).join(', ')} m`] = reach.every((x) => x > 0.45 && x < 0.6);
  // jatuhkan bola ke luar pagar, melawan arah putaran (melenceng menjauhi menara)
  S.goDeck(); P.za = D.za - (D.half + D.inner) / 2; await wait(100);
  P.heading = -Math.PI / 2;
  S.dropBall(); const b = S.getLastBall(), p0 = b.pos.clone();
  for (let i = 0; i < 400 && !b.done; i++) S.physicsStep(0.05);   // langkah fisika langsung (sandbox lambat)
  out[`titik lepas ${S.LAB.dropOut.toFixed(1)} m di luar pagar, bola tidak menabrak menara`] = S.LAB.dropOut > 10 && !b.hitTower;
  const r0 = Math.hypot(p0.x, p0.y), h0 = R - r0, th0 = Math.atan2(p0.y, p0.x), th1 = Math.atan2(b.pos.y, b.pos.x);
  const simS = wrap((th1 - th0) * R), L = Math.sqrt(R * R - r0 * r0), tf = L / (OM * r0), anaS = R * (Math.atan(L / r0) - OM * tf);
  // searah putaran: bola melenceng ke belakang dan menabrak menara (tidak lagi menembus)
  S.goDeck(); P.za = D.za - (D.half + D.inner) / 2; P.heading = Math.PI / 2; await wait(100);
  S.dropBall(); const bw = S.getLastBall();
  for (let i = 0; i < 400 && !bw.done; i++) S.physicsStep(0.05);
  out[`searah putaran: bola ${bw.hitTower ? 'menabrak menara' : 'tidak menabrak menara'}`] = bw.done && bw.hitTower;
  out[`jatuh dari ${h0.toFixed(1)} m: belok ${simS.toFixed(2)} m (analitik ${anaS.toFixed(2)} m, waktu jatuh ${tf.toFixed(2)} s), bola ${b.done ? 'mendarat' : 'belum mendarat'}`] =
    b.done && Math.abs(Math.abs(simS) - Math.abs(anaS)) < 0.05 * Math.abs(anaS) && Math.abs(anaS) > 20;
  // pembanding di tanah: jatuh dari 20 m
  S.teleport('cooper'); await wait(300);
  const keep = S.LAB.drop; S.LAB.drop = 20; S.dropBall(); S.LAB.drop = keep;
  const g0 = S.getLastBall(), q0 = g0.pos.clone();
  for (let i = 0; i < 400 && !g0.done; i++) S.physicsStep(0.05);
  const gS = wrap((Math.atan2(g0.pos.y, g0.pos.x) - Math.atan2(q0.y, q0.x)) * R);
  out[`pembanding di tanah (20 m): belok ${gS.toFixed(3)} m; dari dek ${(Math.abs(simS) / Math.max(Math.abs(gS), 1e-3)).toFixed(0)}x lebih besar`] = g0.done && Math.abs(simS) > 10 * Math.abs(gS);
  // turun: E dari sisi belakang dek (bukan titik datang)
  S.goDeck(); P.za = D.za + (D.half + D.inner) / 2; await wait(200);
  const a2 = S.availableAction();
  out[`aksi di dek: ${a2 ? a2.key : 'tidak ada'}`] = !!a2 && a2.key === 'towerdown';
  S.doAction();
  out[`turun ke lobi: state ${P.state}, dek ${P.deck}, h ${P.h.toFixed(2)}`] = P.state === 'ground' && !P.deck && P.h === 0;
  // revisi bangunan
  const churchTowers = S.BUILD.hip.filter((b) => b[6] === '#e9e4da');
  out[`gereja: ${churchTowers.length} menara, semua berpintu depan (${churchTowers.filter((b) => b[8] === 1).length})`] = churchTowers.length > 0 && churchTowers.every((b) => b[8] === 1);
  const big = S.MARKET.list.filter((m) => m.big);
  out[`pasar besar: ${big.length}, atap dasar ${big[0] ? big[0].roofY[0].toFixed(2) : '-'} m (dinding 6,5 m), puncak ${big[0] ? big[0].roofY[1].toFixed(2) : '-'} m`] =
    big.length > 0 && big.every((m) => m.roofY[0] > 6.0 && m.roofY[0] < 6.5);
  const glass = []; S.COOPER_HOUSE.traverse((o) => { if (o.material && o.material.transparent && o.material.userData.spec && o.material.userData.spec.glass) glass.push(o); });
  const panes = glass.reduce((a, o) => a + o.geometry.attributes.position.count, 0) / 6;   // mesh rumah digabung per material; 21b: 1 bidang = 6 verteks (dulu kotak 36)
  out[`rumah Cooper: ${panes} panel kaca bening (mesh digabung per material)`] = panes >= 20;
  S.teleport('cooper');
  return out;
})()
"""

async def main():
    page_url = pathlib.Path(__file__).resolve().parent.parent.joinpath('experiences/cooper-station/index.html').as_uri()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 320, 'height': 200})
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror ' + str(e)))
        pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' else None)
        await pg.goto(page_url)
        await pg.wait_for_function('window.__stationReady === true', timeout=240000)
        for k, v in (await pg.evaluate(UJI)).items(): print(('OK   ' if v else 'GAGAL'), k)
        print('error:', errs[:10] or 'tidak ada')
        await b.close()

asyncio.run(main())

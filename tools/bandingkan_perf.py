"""Banding performa dua salinan repo (mis. main vs cabang optimasi) per halaman: muat, byte, memori, biaya CPU per frame.

Pakai:
  python tools/bandingkan_perf.py --a /jalur/worktree-main --b . --json hasil.json
  python tools/bandingkan_perf.py --a /jalur/main --b . copper millar gargantua menu detail-copper
Lingkungan: THREE_LOCAL=<folder three.module.js + three.core.js> (three.js disajikan lokal), CHROMIUM=<jalur chrome> opsional.
Opsi: --n 3 (ulangan, median), --play 8 (detik bermain diukur), --mbps 20 --rtt 40 (jaringan tiruan CDP untuk A dan B; --mbps 0 = tanpa batas).
Halaman disajikan lewat server HTTPS lokal dengan gzip (seperti GitHub Pages); cdn.jsdelivr.net dipetakan ke server lokal yang menyajikan THREE_LOCAL,
jadi pembatasan bandwidth CDP berlaku sama untuk berkas lokal dan three.js (pembagian bandwidth nyata, bukan tunda per permintaan).

Yang diukur per halaman (median ulangan):
  - fcp: first-contentful-paint (ms); kartu: kartu mulai / tombol terlihat dapat dipakai; siap: flag siap experience (ms)
  - byte: jumlah byte berkas lokal yang diminta sampai siap + jumlah permintaan
  - ScriptDuration / TaskDuration (CDP Performance.getMetrics) selama muat dan selama bermain
  - frame: jumlah rAF selama bermain, ms thread utama per frame (TaskDuration / frame)
  - heap: JSHeapUsedSize setelah muat
Catatan: di sandbox GPU = SwiftShader, jadi ms per frame tidak mewakili GPU asli; angka thread utama (JS + perintah GL) dan byte tetap berguna
untuk banding A/B. Jalankan A dan B bergantian di mesin yang sama dan jangan menjalankan pekerjaan berat lain bersamaan.
"""
import asyncio, gzip, http.server, json, os, pathlib, ssl, statistics, subprocess, sys, tempfile, threading, time
from playwright.async_api import async_playwright

PAGES = {
    'menu':           {'path': 'index.html', 'ready': 'document.querySelector(".go")', 'play': None},
    'copper':         {'path': 'experiences/cooper-station/index.html', 'ready': 'window.__stationReady === true', 'play': '#go', 'keys': ['KeyW']},
    'millar':         {'path': 'experiences/millar/index.html', 'ready': 'window.__millarReady === true', 'play': '#go', 'keys': ['KeyW']},
    'gargantua':      {'path': 'experiences/gargantua/index.html', 'ready': '!!window.__gargantua && document.getElementById("boot").hidden', 'play': None},
    'detail-copper':  {'path': 'experiences/cooper-station/detail.html', 'ready': 'window.__detailReady === true', 'play': None},
    'detail-gargantua': {'path': 'experiences/gargantua/detail.html', 'ready': 'window.__detailReady === true', 'play': None},
    'detail-millar':  {'path': 'experiences/millar/detail.html', 'ready': 'window.__detailReady === true', 'play': None},
}

MIME = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.webp': 'image/webp',
        '.jpg': 'image/jpeg', '.png': 'image/png', '.json': 'application/json', '.md': 'text/plain', '.mp3': 'audio/mpeg'}
GZ = {'.html', '.js', '.css', '.svg', '.json', '.md'}

def make_cert(d):
    crt, key = os.path.join(d, 'c.pem'), os.path.join(d, 'k.pem')
    if not os.path.exists(crt):
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', key, '-out', crt, '-days', '2', '-subj', '/CN=localhost',
                        '-addext', 'subjectAltName=DNS:localhost,DNS:cdn.jsdelivr.net,IP:127.0.0.1'], check=True, capture_output=True)
    return crt, key

def serve(root, cdn_map, crt, key):
    """Server HTTPS (thread) untuk satu akar; cdn_map: awalan URL -> folder (untuk server CDN tiruan). Mengembalikan (server, port)."""
    cache = {}
    class H(http.server.BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        def log_message(self, *a): pass
        def do_GET(self):
            path = self.path.split('?')[0].split('#')[0]
            if cdn_map:
                f = pathlib.Path(cdn_map) / path.rsplit('/', 1)[-1]
            else:
                f = (pathlib.Path(root) / path.lstrip('/')).resolve()
                if f.is_dir(): f = f / 'index.html'
            if not f.is_file():
                self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers(); return
            ext = f.suffix.lower()
            key_ = str(f)
            if key_ not in cache:
                raw = f.read_bytes()
                cache[key_] = (raw, gzip.compress(raw, 6) if ext in GZ else None)
            raw, gz = cache[key_]
            body = gz if gz is not None else raw
            self.send_response(200)
            self.send_header('Content-Type', MIME.get(ext, 'application/octet-stream'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store')
            if gz is not None: self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try: self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(crt, key)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]

INIT = """
(() => {
  window.__fr = 0;
  const raf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = (cb) => raf((t) => { window.__fr++; cb(t); });
  let b = false;                                   // saat modul experience mulai jalan (Copper menandai window.__stationBoot)
  Object.defineProperty(window, '__stationBoot', { configurable: true, get() { return b; }, set(v) { if (v && !window.__bootAt) window.__bootAt = performance.now(); b = v; } });
})();
"""

def dbg(m):
    if os.environ.get('PERF_DEBUG'): print('   [dbg]', m, round(time.time() % 1000, 1), flush=True)

async def metrics(cdp):
    m = await cdp.send('Performance.getMetrics')
    return {x['name']: x['value'] for x in m['metrics']}

async def one(b, port, name, cfg, net, play_s):
    ctx = await b.new_context(viewport={'width': 960, 'height': 540}, device_scale_factor=1, ignore_https_errors=True)
    pg = await ctx.new_page()
    cdp = await ctx.new_cdp_session(pg)
    await cdp.send('Performance.enable'); await cdp.send('Network.enable')
    if net['mbps'] > 0:
        await cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': net['rtt'], 'downloadThroughput': net['mbps'] * 125000, 'uploadThroughput': net['mbps'] * 125000})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    sizes = {}
    def fin(ev): sizes[ev['requestId']] = ev['encodedDataLength']
    cdp.on('Network.loadingFinished', fin)
    await pg.add_init_script(INIT)
    await pg.goto(f'https://127.0.0.1:{port}/{cfg["path"]}?lang=id', wait_until='commit')
    await pg.wait_for_function(cfg['ready'], timeout=900000, polling=50)
    siap = await pg.evaluate('performance.now()'); dbg('siap')
    await pg.wait_for_timeout(800)
    fcp = await pg.evaluate("(performance.getEntriesByName('first-contentful-paint')[0] || {}).startTime || null")
    boot = await pg.evaluate('window.__bootAt || null')
    dcl = await pg.evaluate("performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd")
    res = await pg.evaluate("performance.getEntriesByType('resource').filter(r => /three\\.module|orang\\.data|rumput\\.data/.test(r.name)).map(r => [r.name.split('/').pop(), Math.round(r.startTime), Math.round(r.responseEnd)])")
    m1 = await metrics(cdp)
    out = {'fcp': fcp, 'dcl': dcl, 'modul_mulai': boot, 'siap': siap, 'bytes': sum(sizes.values()), 'reqs': len(sizes), 'heap_mb': m1['JSHeapUsedSize'] / 1048576,
           'script_load_s': m1['ScriptDuration'], 'task_load_s': m1['TaskDuration'], 'res': res, 'errs': errs}
    if cfg.get('play'):
        try: await pg.click(cfg['play'], timeout=60000)
        except Exception as e: errs.append('klik gagal: ' + str(e)[:80])
        dbg('klik'); await pg.wait_for_timeout(3000)
        f0, m0 = await pg.evaluate('window.__fr'), await metrics(cdp)
        for k in cfg.get('keys', []): await pg.keyboard.down(k)
        await pg.wait_for_timeout(int(play_s * 1000))
        for k in cfg.get('keys', []): await pg.keyboard.up(k)
        f1, m2 = await pg.evaluate('window.__fr'), await metrics(cdp)
        fr = max(1, f1 - f0)
        out.update({'frames': fr, 'fps': fr / play_s, 'script_ms_frame': (m2['ScriptDuration'] - m0['ScriptDuration']) * 1000 / fr,
                    'task_ms_frame': (m2['TaskDuration'] - m0['TaskDuration']) * 1000 / fr, 'heap_play_mb': m2['JSHeapUsedSize'] / 1048576})
    await ctx.close()
    return out

def med(rows, k):
    v = [r[k] for r in rows if r.get(k) is not None]
    return statistics.median(v) if v else None

async def main():
    a = sys.argv[1:]
    def opt(n, d):
        return a[a.index(n) + 1] if n in a else d
    A, B = opt('--a', None), opt('--b', '.')
    n, play = int(opt('--n', 3)), float(opt('--play', 8))
    net = {'mbps': float(opt('--mbps', 20)), 'rtt': float(opt('--rtt', 40))}
    names = [x for x in a if x in PAGES] or list(PAGES)
    out_json = opt('--json', None)
    local, exe = os.environ['THREE_LOCAL'], os.environ.get('CHROMIUM')
    tmp = tempfile.mkdtemp(); crt, key = make_cert(tmp)
    _, cdn_port = serve(None, local, crt, key)
    roots = {}
    for tag, root in (('A', A), ('B', B)):
        if root: roots[tag] = serve(root, None, crt, key)[1]
    res = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required',
                                          '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--ignore-certificate-errors',
                                          f'--host-resolver-rules=MAP cdn.jsdelivr.net 127.0.0.1:{cdn_port}'],
                                    **({'executable_path': exe} if exe else {}))
        for name in names:
            res[name] = {}
            for i in range(n):                           # bergantian A, B agar gangguan sistem terbagi rata
                for tag, port in (list(roots.items())[::-1] if i % 2 else roots.items()):   # urutan ditukar tiap ulangan: tanpa bias "yang pertama dingin"
                    r = await one(b, port, name, PAGES[name], net, play)
                    res[name].setdefault(tag, []).append(r)
                    print(f'  {name} {tag} #{i + 1}: modul {r["modul_mulai"] or 0:.0f} ms, siap {r["siap"]:.0f} ms, {r["bytes"] / 1048576:.2f} MB, {r["reqs"]} berkas' +
                          (f', {r["fps"]:.2f} fps' if 'fps' in r else '') + (f' ERR {r["errs"][:2]}' if r['errs'] else ''), flush=True)
        await b.close()
    keys = ['fcp', 'dcl', 'modul_mulai', 'siap', 'bytes', 'reqs', 'heap_mb', 'script_load_s', 'task_load_s', 'fps', 'script_ms_frame', 'task_ms_frame', 'heap_play_mb']
    print('\n| halaman | metrik | A | B | selisih |\n| --- | --- | --- | --- | --- |')
    for name, d in res.items():
        for k in keys:
            va = med(d.get('A', []), k); vb = med(d.get('B', []), k)
            if va is None and vb is None: continue
            f = lambda x: '-' if x is None else (f'{x:,.0f}' if abs(x) >= 100 else f'{x:.2f}')
            diff = '-' if (va is None or vb is None or va == 0) else f'{(vb - va) / va * 100:+.1f}%'
            print(f'| {name} | {k} | {f(va)} | {f(vb)} | {diff} |')
    if out_json: pathlib.Path(out_json).write_text(json.dumps(res, indent=1))

if __name__ == '__main__':
    asyncio.run(main())

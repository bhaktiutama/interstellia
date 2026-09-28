"""Olah model motor GLB (Sketchfab) menjadi aset ringkas untuk Copper Corn Station (tahap 19c).
Sumber: "moto guzzi v-twin" oleh Alexios Apokaukos, CC-BY-4.0,
https://sketchfab.com/3d-models/moto-guzzi-v-twin-923c2932481141c8a1966d427a5d3b30 (file sumber 21,9 MB tidak disimpan di repo).

Yang dilakukan:
- Transformasi node dipanggang ke verteks, lalu diputar ke kerangka motor di halaman: +x = kiri, +y = atas, +z = depan,
  titik asal di tanah di tengah kedua poros roda (model: +x depan, +y atas, +z kanan).
- Hanya posisi, normal (int8), UV pertama, indeks. Peta normal, kekasaran-logam, tangen, warna verteks dibuang (stasiun memakai
  material dasar + patchLit); kekasaran dan logam diringkas jadi satu angka per material (rata-rata peta).
- Tekstur warna dasar diperkecil (JPEG; rem tetap PNG karena beralfa).
- Pulau segitiga dikelompokkan: 'front' (berputar di sumbu kemudi: garpu, roda depan, spakbor, fairing, kaca, stang jepit),
  'stand' (standar samping, disembunyikan saat dikendarai), 'body' (sisanya). Mesh ganda (kaca yang sama dua kali) dibuang.
- Titik penting (grip, pijakan, lampu, muka panel instrumen, lampu belakang, mata pengendara) ditulis di metadata.
Keluaran: experiences/cooper-station/assets/motor.data.js (window.__MOTOR_DATA = base64 dari 'MOT1' + JSON + data biner),
dimuat lewat <script> biasa agar jalan juga dari file://.
Pakai: python tools/siapkan_motor.py sumber.glb   (butuh: pip install numpy pillow)"""
import base64, io, json, pathlib, struct, sys
import numpy as np
from PIL import Image

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}
# ukuran tekstur per material (sisi terpanjang, piksel); yang dilihat dekat dari POV (tangki, kokpit) paling besar
TEX_SIZE = {'engine_mat': 1024, 'seat_fender_mat': 512, 'brakes': 512, 'light_mat_exp': 128, 'chrome_bake_mat': 1024,
            'engine_mechanics_mat': 512, 'mat_cockpit': 1024, 'tanknewlivery': 1024, 'mat_backtyre001': 512, 'headlight_glass_bake': 256}
# sumbu kemudi (kerangka model): sejajar kaki garpu bawah (PCA: kemiringan 26,2 derajat), 3,5 cm di belakang garis tengah garpu
AX_D = np.array([-0.442, 0.897]); AX_D /= np.linalg.norm(AX_D); AX_F = np.array([AX_D[1], -AX_D[0]])
AX_A = np.array([0.623, 0.502]) - 0.035 * AX_F


def load(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + jl]); b0 = 20 + jl + 8
    def acc(i):
        a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
        dt = np.dtype(CT[a['componentType']]); n = NC[a['type']]
        off = b0 + bv.get('byteOffset', 0) + a.get('byteOffset', 0); stride = bv.get('byteStride', 0) or dt.itemsize * n
        raw = np.frombuffer(b, dtype=np.uint8, count=stride * (a['count'] - 1) + dt.itemsize * n, offset=off)
        out = np.lib.stride_tricks.as_strided(raw, shape=(a['count'], dt.itemsize * n), strides=(stride, 1)).copy().view(dt).reshape(a['count'], n)
        return out.astype(np.float32) / np.iinfo(dt).max if a.get('normalized') else out
    def img(i):
        bv = j['bufferViews'][j['images'][i]['bufferView']]; o = b0 + bv.get('byteOffset', 0)
        return b[o:o + bv['byteLength']]
    world = {}
    def walk(n, M):
        nd = j['nodes'][n]; L = np.eye(4)
        if 'matrix' in nd: L = np.array(nd['matrix'], dtype=float).reshape(4, 4).T
        else:
            T = np.eye(4); T[:3, 3] = nd.get('translation', [0, 0, 0]); x, y, z, w = nd.get('rotation', [0, 0, 0, 1])
            Rm = np.eye(4); Rm[:3, :3] = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
            L = T @ Rm @ np.diag(list(nd.get('scale', [1, 1, 1])) + [1])
        world[n] = M @ L
        for c in nd.get('children', []): walk(c, world[n])
    for n in j['scenes'][j.get('scene', 0)]['nodes']: walk(n, np.eye(4))
    prims, seen = [], set()
    for n, W in world.items():
        nd = j['nodes'][n]
        if 'mesh' not in nd: continue
        for pr in j['meshes'][nd['mesh']]['primitives']:
            A = pr['attributes']; P = acc(A['POSITION']).astype(float); N = acc(A['NORMAL']).astype(float)
            uv = acc(A['TEXCOORD_0']).astype(float) if 'TEXCOORD_0' in A else np.zeros((len(P), 2))
            I = (acc(pr['indices']).reshape(-1) if 'indices' in pr else np.arange(len(P))).astype(np.int64)
            P = (np.c_[P, np.ones(len(P))] @ W.T)[:, :3]; N = N @ np.linalg.inv(W[:3, :3])
            N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
            key = (pr.get('material'), len(P), round(float(P.sum()), 4))
            if key in seen: continue                                  # mesh ganda (kaca fairing dua kali)
            seen.add(key)
            prims.append(dict(mesh=nd['mesh'], mat=pr.get('material'), P=P, N=N, uv=uv, I=I))
    return j, prims, img


def components(P, I):
    """Label pulau segitiga terhubung per segitiga (verteks dilas per posisi 0,1 mm)."""
    _, weld = np.unique(np.round(P * 1e4).astype(np.int64), axis=0, return_inverse=True); weld = weld.reshape(-1)
    parent = np.arange(weld.max() + 1)
    def find(a):
        r = a
        while parent[r] != r: r = parent[r]
        while parent[a] != r: parent[a], a = r, parent[a]
        return r
    T = weld[I.reshape(-1, 3)]
    for a, b, c in T:
        ra = find(a)
        for o in (b, c):
            ro = find(o)
            if ro != ra: parent[ro] = ra
    return np.unique(np.array([find(t[0]) for t in T]), return_inverse=True)[1].reshape(-1)


def group_of(V):
    """V = verteks satu pulau (kerangka model). Depan: sebagian besar di depan sumbu kemudi, atau stang jepit/tuas/saklar."""
    s = (V[:, :2] - AX_A) @ AX_F; med = np.median(s); c = V.mean(0)
    if V[:, 1].min() < 0.02 and c[2] < -0.1 and c[0] < 0 and len(V) < 400: return 'stand'   # standar samping (kiri, menyentuh tanah)
    if med > -0.03: return 'front'
    if V[:, 1].min() > 0.75 and med > -0.16 and abs(c[2]) > 0.1: return 'front'
    return 'body'


def main():
    src = sys.argv[1]
    out = pathlib.Path(__file__).resolve().parent.parent / 'experiences/cooper-station/assets/motor.data.js'
    j, prims, img = load(src)
    # kerangka halaman: titik asal di tanah, di tengah kedua poros roda
    tyre = [p for p in prims if j['materials'][p['mat']]['name'] == 'mat_backtyre001'][0]
    lab = components(tyre['P'], tyre['I']); tri = tyre['P'][tyre['I'].reshape(-1, 3)]
    wheels = sorted([tri[lab == c].reshape(-1, 3) for c in range(lab.max() + 1)], key=lambda v: v[:, 0].mean())
    wc = [(w.min(0) + w.max(0)) / 2 for w in wheels]; ground = np.mean([w[:, 1].min() for w in wheels])
    x0 = (wc[0][0] + wc[1][0]) / 2
    def to_page(P): return np.stack([-P[:, 2], P[:, 1] - ground, P[:, 0] - x0], 1)   # (kiri, atas, depan)
    def to_page_dir(D): return np.stack([-D[:, 2], D[:, 1], D[:, 0]], 1)
    # material
    mats, texs, blob = [], [], bytearray()
    def put(arr):
        nonlocal blob
        while len(blob) % 4: blob += b'\0'
        off = len(blob); blob += arr.tobytes(); return off
    for i, m in enumerate(j['materials']):
        pb = m.get('pbrMetallicRoughness', {}); name = m['name']
        color = pb.get('baseColorFactor', [1, 1, 1, 1]); rough, metal = pb.get('roughnessFactor', 1.0), pb.get('metallicFactor', 1.0)
        if 'metallicRoughnessTexture' in pb:
            mr = np.asarray(Image.open(io.BytesIO(img(j['textures'][pb['metallicRoughnessTexture']['index']]['source']))).convert('RGB').resize((128, 128))).reshape(-1, 3).mean(0) / 255
            rough, metal = rough * mr[1], metal * mr[2]
        if 'KHR_materials_clearcoat' in m.get('extensions', {}): rough, metal = 0.08, 0.05   # cat bening berkilap (tangki)
        tex = -1
        if 'baseColorTexture' in pb:
            im = Image.open(io.BytesIO(img(j['textures'][pb['baseColorTexture']['index']]['source'])))
            size = TEX_SIZE.get(name, 512); im.thumbnail((size, size), Image.LANCZOS)
            bio = io.BytesIO()
            if name == 'brakes': im.convert('RGBA').save(bio, 'PNG', optimize=True); mime = 'image/png'
            else: im.convert('RGB').save(bio, 'JPEG', quality=82, optimize=True); mime = 'image/jpeg'
            data = bio.getvalue(); tex = len(texs); texs.append({'off': put(np.frombuffer(data, np.uint8)), 'len': len(data), 'mime': mime})
        alpha = 'mask' if name == 'brakes' else 'blend' if m.get('alphaMode') == 'BLEND' else 'opaque'
        mats.append({'name': name, 'color': [round(c, 4) for c in color[:3]], 'opacity': round(color[3], 3), 'tex': tex, 'rough': round(float(rough), 3),
                     'metal': round(float(metal), 3), 'alpha': alpha, 'double': bool(m.get('doubleSided'))})
    # geometri per (kelompok, material)
    buckets = {}
    for p in prims:
        lab = components(p['P'], p['I']); T = p['I'].reshape(-1, 3)
        grp = [group_of(p['P'][np.unique(T[lab == c])]) for c in range(lab.max() + 1)]
        for c, g in enumerate(grp): buckets.setdefault((g, p['mat']), []).append((p, T[lab == c]))
    parts, stats = [], {}
    for (g, mi), lst in sorted(buckets.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        Ps, Ns, Us, Is, base = [], [], [], [], 0
        for p, T in lst:
            used, inv = np.unique(T.reshape(-1), return_inverse=True)
            Ps.append(to_page(p['P'][used])); Ns.append(to_page_dir(p['N'][used])); Us.append(p['uv'][used]); Is.append(inv.reshape(-1) + base); base += len(used)
        P = np.concatenate(Ps).astype(np.float32); N = np.clip(np.round(np.concatenate(Ns) * 127), -127, 127).astype(np.int8)
        U = np.concatenate(Us).astype(np.float32); I = np.concatenate(Is)
        i32 = len(P) > 65535; I = I.astype(np.uint32 if i32 else np.uint16)
        parts.append({'grp': g, 'mat': mi, 'n': len(P), 'ni': len(I), 'i32': i32, 'pos': put(P), 'nrm': put(N), 'uv': put(U), 'idx': put(I)})
        stats[g] = stats.get(g, 0) + len(I) // 3
    # titik penting (kerangka halaman)
    def pt(x, y, z): return [round(float(v), 4) for v in to_page(np.array([[x, y, z]]))[0]]
    grips = [q for q in prims if j['materials'][q['mat']]['name'] == 'leathergrips'][0]
    lab = components(grips['P'], grips['I']); T = grips['I'].reshape(-1, 3)
    gr = []
    for c in range(lab.max() + 1):
        V = grips['P'][np.unique(T[lab == c])]
        if len(V) < 100: continue
        m = V.mean(0); _, _, vt = np.linalg.svd(V - m); d = vt[0] * np.sign(vt[0][2] * m[2])   # ke arah luar
        gr.append((m, d))
    gl = [g for g in gr if g[0][2] < 0][0]                          # grip kiri (model z negatif)
    lamp_c = pt(0.612, 0.86, 0.0)
    meta = {
        'axle': pt(*AX_A, 0.0), 'axis': [0.0, round(float(AX_D[1]), 4), round(float(AX_D[0]), 4)],
        'wheelFront': pt(*wc[1]), 'wheelRear': pt(*wc[0]),
        'gripL': pt(*gl[0]), 'gripDirL': [round(float(v), 4) for v in to_page_dir(gl[1][None])[0]],
        'pegL': pt(0.085, 0.27, -0.28), 'seat': pt(-0.45, 0.735, 0.0), 'eye': pt(-0.25, 1.36, 0.0),
        'lamp': lamp_c, 'lampR': 0.072, 'tail': pt(-0.776, 0.765, 0.0), 'tailR': 0.028,
        'dial': pt(0.503, 0.928, 0.0), 'dialN': [0.0, 0.5997, -0.8002], 'dialR': 0.052,
    }
    head = {'v': 1, 'credit': j['asset'].get('extras', {}), 'mats': mats, 'texs': texs, 'parts': parts, 'meta': meta}
    js = json.dumps(head, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    data = b'MOT1' + struct.pack('<I', len(js)) + js + bytes(blob)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('/* Model motor untuk Copper Corn Station (tahap 19c), dibuat oleh tools/siapkan_motor.py.\n'
                   '   "moto guzzi v-twin" oleh Alexios Apokaukos (https://sketchfab.com/Alexios_Apokaukos), CC-BY-4.0,\n'
                   '   https://sketchfab.com/3d-models/moto-guzzi-v-twin-923c2932481141c8a1966d427a5d3b30\n'
                   '   Diubah: tekstur diperkecil, tanpa peta normal dan kekasaran, geometri dipindah ke kerangka motor. */\n'
                   'window.__MOTOR_DATA = "' + base64.b64encode(data).decode() + '";\n', encoding='ascii')
    print('keluaran', out, f'{out.stat().st_size / 1e6:.2f} MB (biner {len(data) / 1e6:.2f} MB, tekstur {sum(t["len"] for t in texs) / 1e6:.2f} MB)')
    print('segitiga per kelompok', stats, 'bagian', len(parts))
    print('metadata', json.dumps(meta))


if __name__ == '__main__':
    main()

"""Olah aset FluffyGrass (github.com/thebenezer/FluffyGrass, MIT, Copyright (c) 2023 Ebenezer) menjadi
experiences/cooper-station/assets/rumput.data.js: mesh rumpun 3 tingkat detail dari grassLODs.glb (posisi, normal, uv, indeks),
tekstur alfa grass.jpeg, dan perlinnoise.webp (data URL base64). Geometri sudah diskalakan 5x seperti sumbernya (child.geometry.scale(5, 5, 5)).
Pakai: python tools/siapkan_rumput.py <folder public FluffyGrass>"""
import base64, json, struct, sys, pathlib

src = pathlib.Path(sys.argv[1])
glb = (src / 'grassLODs.glb').read_bytes()
jl = struct.unpack('<I', glb[12:16])[0]
j = json.loads(glb[20:20 + jl])
bin0 = 20 + jl + 8
SC = 5.0
CT = {5126: ('f', 4), 5123: ('H', 2)}

def acc(i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]; f, sz = CT[a['componentType']]
    off = bin0 + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    return list(struct.unpack('<' + f * (a['count'] * n), glb[off:off + a['count'] * n * sz])), a['count']

def b64(fmt, vals): return base64.b64encode(struct.pack('<' + fmt * len(vals), *vals)).decode()

lods = []
for m in j['meshes']:
    p = m['primitives'][0]; at = p['attributes']
    pos, n = acc(at['POSITION']); nrm, _ = acc(at['NORMAL']); uv, _ = acc(at['TEXCOORD_0']); idx, ni = acc(p['indices'])
    lods.append({'n': n, 'ni': ni, 'pos': b64('f', [v * SC for v in pos]), 'nrm': b64('f', nrm), 'uv': b64('f', uv), 'idx': b64('H', idx)})

def url(name, mime): return 'data:%s;base64,%s' % (mime, base64.b64encode((src / name).read_bytes()).decode())
out = {'lods': lods, 'grass': url('grass.jpeg', 'image/jpeg'), 'noise': url('perlinnoise.webp', 'image/webp')}
dst = pathlib.Path(__file__).resolve().parent.parent / 'experiences/cooper-station/assets/rumput.data.js'
dst.write_text('// Dibuat tools/siapkan_rumput.py dari FluffyGrass (MIT, Copyright (c) 2023 Ebenezer). Jangan disunting tangan.\nwindow.RUMPUT_DATA = ' + json.dumps(out) + ';\n')
print(dst, dst.stat().st_size, 'byte;', [(l['n'], l['ni']) for l in lods])

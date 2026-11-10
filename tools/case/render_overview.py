"""case/overview.html - self-contained WebGL assembly overview (no network, no CDN).

Printed parts come from the exported assembled STLs in case/out; bought servos, modules, screws and
nuts are tessellated from the same definitions the checks use (case/model.py, case/hardware.py).
Skips work when its inputs are unchanged.  usage: case-python tools/case/render_overview.py [--force]
"""
import base64
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/robot'
sys.path.insert(0, str(ROOT / 'case'))
sys.path.insert(0, str(ROOT / 'tools/case'))
CORNERS = ('FL', 'FR', 'RL', 'RR')
SIGN = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}
CN = {'FL': 'trước trái', 'FR': 'trước phải', 'RL': 'sau trái', 'RR': 'sau phải'}

COL = {'frame': '#d6cfc1', 'cover': '#eee9df', 'clamp': '#cfc6b3', 'moving': '#9ebcca', 'foot': '#8fb0bf',
       'servo': '#4d6fa8', 'horn': '#f2f2f2', 'elec': '#4c806c', 'elec2': '#607d8b', 'bank': '#3d4650',
       'metal': '#596872', 'nut': '#7a8790'}


def stl_tris(path):
    d = path.read_bytes()
    n = int.from_bytes(d[80:84], 'little')
    a = np.frombuffer(d[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n)
    return a['v'].reshape(-1, 3, 3).astype(float)


def shape_tris(shape, tol=0.08):
    vs, ts = [], []
    for s in shape.solids().vals() if hasattr(shape, 'solids') else [shape]:
        v, t = s.tessellate(tol, 0.3)
        base = len(vs)
        vs += [(p.x, p.y, p.z) for p in v]
        ts += [(a + base, b + base, c + base) for a, b, c in t]
    V = np.array(vs)
    return V[np.array(ts)] if ts else np.zeros((0, 3, 3))


def edges_of(T, angle=28.0):
    """Feature edges: boundary or dihedral > angle."""
    if not len(T):
        return np.zeros((0, 2, 3))
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ok = ln > 1e-12
    T, n = T[ok], n[ok] / ln[ok, None]
    key = lambda p: (round(p[0], 3), round(p[1], 3), round(p[2], 3))
    E = {}
    for i, tri in enumerate(T):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            ka, kb = key(tri[a]), key(tri[b])
            k = (ka, kb) if ka < kb else (kb, ka)
            E.setdefault(k, []).append(i)
    out = []
    c = math.cos(math.radians(angle))
    for (ka, kb), fs in E.items():
        if len(fs) == 1 or (len(fs) >= 2 and float(np.dot(n[fs[0]], n[fs[1]])) < c):
            out.append((ka, kb))
    return np.array(out, dtype=float).reshape(-1, 2, 3)


def pack(arr):
    q = np.round(np.asarray(arr, dtype=float).reshape(-1) * 50).astype('<i2')   # 0.02 mm grid
    return base64.b64encode(q.tobytes()).decode()


def usb_wire():
    """W2 follows J1 as published: the checked cable route when J1 is on a side edge, the old straight rear run otherwise."""
    ev = json.loads((ROOT / 'case/reports/route-evidence.json').read_text())
    r = next((x for x in ev['routes'] if x['route'].startswith('usb')), None)
    if r:
        return {'id': 'W2', 'label': 'Cáp USB-C: pin cổng 1 → khoang giữa 2 servo sau → ra đầu khung → dọc ngoài ray bên trái → đầu USB-C vào J1 qua cửa hông', 'color': '#3b5bdb', 'pts': r['waypoints']}
    return {'id': 'W2', 'label': 'Cáp USB-C: pin cổng 1 → ra sau → J1 (cạnh sau; cáp thường không vừa, xem D23)', 'color': '#3b5bdb',
            'pts': [[-48, 14, 10], [-61, 8, 12], [-66, 0, 20], [-66, 0, 26], [-61, 0, 26]]}


def main():
    import cadquery as cq
    import model as M
    import hardware as HW
    import build as B
    srcs = sorted(OUT.glob('*.stl')) + [Path(__file__), ROOT / 'case/model.py', ROOT / 'case/hardware.py',
                                       ROOT / 'case/build.py', OUT / 'parts.json', ROOT / 'case/assembly_steps.json',
                                       Path(__file__).parent / 'overview_template.html', ROOT / 'case/reports/route-evidence.json']
    h = hashlib.sha256()
    for f in srcs:
        h.update(f.read_bytes())
    key = h.hexdigest()
    target = ROOT / 'case/overview.html'
    if target.exists() and '--force' not in sys.argv and key in target.read_text()[:4000]:
        print('overview up to date'); return 0
    meshes = []

    def add(mid, label, group, color, T, kind, corner=None, extra=None):
        meshes.append(dict(id=mid, label=label, group=group, color=color, kind=kind, corner=corner,
                           tri=pack(T), edge=pack(edges_of(T)), n=int(len(T)), **(extra or {})))

    add('frame_lower', 'frame_lower — khung dưới (nôi pin, ray, khối đỡ board)', 'frame', COL['frame'], stl_tris(OUT / 'frame_lower.stl'), 'print')
    add('frame_upper', 'frame_upper — khung trên (yên tai servo, màn hình, dải đèn)', 'cover', COL['cover'], stl_tris(OUT / 'frame_upper.stl'), 'print')
    for c in CORNERS:
        add(f'thigh_{c}', f'thigh_{c} — đùi {CN[c]}', 'thigh', COL['moving'], stl_tris(OUT / f'thigh_{c}.stl'), 'print', c)
        add(f'foot_{c}', f'foot_{c} — cẳng {CN[c]}', 'foot', COL['foot'], stl_tris(OUT / f'foot_{c}.stl'), 'print', c)
    # bought parts
    body = M.hip_servo_FL_place(M.sg90_local(with_horn=False))
    horn = M.hip_servo_FL_place(M.horn_local(0.0)).rotate((M.HIP_X, M.HIP_Y, 0), (M.HIP_X, M.HIP_Y, 1), 135)
    knee = M.leg_to_global(M.knee_servo_leg())
    for c in CORNERS:
        add(f'hip_servo_{c}', f'SG90 hông {c}', 'hipservo', COL['servo'], shape_tris(M.corner_rigid(body, c)), 'bought', c)
        add(f'hip_horn_{c}', f'horn 1 tay hông {c}', 'hiphorn', COL['horn'], shape_tris(M.corner_rigid(horn, c)), 'bought', c)
        add(f'knee_servo_{c}', f'SG90 gối {c} + horn', 'kneeservo', COL['servo'], shape_tris(M.corner_rigid(knee, c)), 'bought', c)
    bx = M.box
    xa, ya, xb, yb = M.BOARD_OUTLINE
    add('board', 'Board điện tử tích hợp (ESP32-S3 + PCA9685)' + (' — BẢN CASE ĐỀ XUẤT, chưa phải board đã chốt' if M.BOARD_STATUS == 'DRAFT' else ''),
        'elec', COL['elec'], shape_tris(bx(xa, xb, ya, yb, M.BOARD_ZB, M.BOARD_ZT)), 'bought')
    for p in M.BOARD_PARTS:
        pa, pb, pc, pd = p['robotBox']
        add('part_' + p['ref'], f"{p['ref']} trên board", 'elec', COL['elec2'], shape_tris(bx(pa, pc, pb, pd, M.BOARD_ZT, M.BOARD_ZT + p['heightMm'])), 'bought')
    disp = None
    for lab, x0, x1, y0, y1, z0, z1 in M.disp_back_boxes():
        solid = bx(x0, x1, y0, y1, z0, z1)
        disp = solid if disp is None else disp.union(solid)
    add('display', 'Màn hình Waveshare 1.9 in (xoay 180°, dây 8 sợi)', 'elec', '#3d6a8a', shape_tris(disp), 'bought')
    add('led', 'Thanh WS2812 8 LED', 'elec', '#d9b44a', shape_tris(bx(-28, 28, -6, 6, 39.5, 43.5)), 'bought')
    add('bank', 'Pin dự phòng 5000 mAh (≤100×66×15)', 'bank', COL['bank'],
        shape_tris(bx(M.BANK['x0'], M.BANK['x1'], -33, 33, 3, 18)), 'bought')
    add('adapter', 'Đầu chuyển USB → terminal vặn vít (cổng 2)', 'bank', '#8a6d3b', shape_tris(bx(-59.5, -37.5, -24, -4, 3, 18)), 'bought')
    add('usbplug', 'Đầu USB-A vuông góc của cáp USB-C (cổng 1)', 'bank', '#2e3a46', shape_tris(bx(-59.5, -37.5, 4, 24, 3, 18)), 'bought')
    uitem = dict(B.electronics_items())['USB-C plug overmold']
    add('usbc', ('Đầu USB-C thường cắm vào J1, luồn qua cửa hông bên trái' if M.USB_SIDE else 'Đầu USB-C cắm vào J1 (cạnh sau, đầu cắm rộng tối đa 9 mm, xem D23)'), 'elec', '#2e3a46', shape_tris(uitem), 'bought')
    inst = HW.instances()
    for hh in inst:
        T = shape_tris(B.screw_solid(hh), 0.05)
        corner = hh['id'][1:3] if hh['id'][0] in 'HK' else None
        move = ('thigh' if hh['id'].startswith('H') or 'tab' in hh['id'] else 'foot') if corner else None
        if hh['id'].endswith('-ctr') or hh['id'].endswith('-arm') and hh['id'][0] == 'H':
            move = 'thigh' if hh['id'][0] == 'H' else 'foot'
        add('hw_' + hh['id'], f"{hh['id']} — {hh['size']}", 'hw', COL['metal'], T, 'hw', corner,
            {'hw': hh['id'], 'axis': list(hh['axis']), 'head': list(hh['head']), 'len': hh['length'], 'moveWith': move})
        if hh.get('nut'):
            x, y, z = hh['nut']
            nut = M.hexprism_z(0, 0, z - M.NUT_T / 2, z + M.NUT_T / 2, M.NUT_AF).rotate((0, 0, 0), (0, 0, 1), 30) \
                .translate((x, y, 0)).cut(M.cyl(x, y, z - 2, z + 2, 3.0))
            add('nut_' + hh['id'], f"tán M3 của {hh['id']}", 'nut', COL['nut'], shape_tris(nut, 0.05), 'hw', None,
                {'hw': hh['id'], 'nutEntry': list(hh.get('nut_entry') or [0, 0, 0])})
    # wire paths (indicative; the real netlist and firmware/WIRING.md are the source)
    zt = M.BOARD_ZT
    zw = zt + 16.0
    wires = [
        {'id': 'W1', 'label': 'Đầu chuyển cổng 2 → terminal J12 (+ / −, vặn vít)', 'color': '#ff6a00',
         'pts': [[-45, -14, 12], [-46, -31, 22], [-20, -40, 30], [25, -40, 30], [38, -20, 36], [41.5, 0, 36], [38.5, 0, 31]]},
        usb_wire(),
        {'id': 'W3', 'label': 'Dây thanh LED: J11 → thanh LED (DIN / 5V / GND)', 'color': '#bbbbbb',
         'pts': [[20, -27, zt + 8], [26, -14, 36], [27.5, 0, 39]]},
        {'id': 'W4', 'label': 'Dây màn hình 8 sợi: J10 → màn hình Waveshare', 'color': '#9a59b5',
         'pts': [[11, 20, zt + 16], [14, 26, 39], [8, 30, 40], [1, 18, 39]]},
        {'id': 'W5', 'label': 'Dây servo hông: khoang giữa 2 servo → ra đầu khung (đường B) hoặc thẳng ra cửa hông ở góc (đường C) → cửa hông bên phải → hàng CH0/2/4/6 (nâu = GND)', 'color': '#a0522d',
         'pts': [[53, 3.5, 26], [60, 0, 27], [68, 0, 27], [68, -40, 27], [20, -44, 29], [14, -33, 30], [14, -29, 38], [-20, -27, 46], [-20, -19.5, 44]]},
        {'id': 'W6', 'label': 'Dây servo gối: vòng dư qua khớp, buộc ở tấm đùi và cột góc → dọc ngoài ray tới x ±41.5 → lên đỉnh khung (phía trong trục đùi) hoặc qua cửa hông → hàng CH1/3/5/7', 'color': '#c46a2a',
         'pts': [[75, 45, 46], [59.5, 39.2, 32], [41.5, 39.5, 32], [41.5, 39.5, 51], [41.5, -24, 51], [-13, -24, 51], [-13, -19.5, 44]]},
    ]
    # both open routes of every servo lead, from the checked route evidence: shown only in the wire-routing step
    ev = json.loads((ROOT / 'case/reports/route-evidence.json').read_text())
    for i, r in enumerate(ev['routes']):
        wires.append({'id': f'R{i + 1}', 'label': r['route'], 'color': '#1c7ed6' if ' route A ' in r['route'] else '#e8590c', 'pts': r['waypoints'], 'stepOnly': True})
    steps = json.loads((ROOT / 'case/assembly_steps.json').read_text())
    hwmap = {hh['id']: {'id': hh['id'], 'size': hh['size'], 'kind': hh['kind'], 'nut': bool(hh.get('nut')),
                        'entry': hh['entry'], 'action': hh['action'], 'parts': hh['parts']} for hh in inst}
    data = {'meshes': meshes, 'wires': wires, 'steps': steps, 'hw': hwmap,
            'joints': {'hip': {c: [SIGN[c][0] * M.HIP_X, SIGN[c][1] * M.HIP_Y] for c in CORNERS},
                       'rk': M.R_KNEE, 'zk': M.Z_KNEE, 'range': 30},
            'rev': json.loads((OUT / 'parts.json').read_text()).get('revision'), 'inputHash': key}
    html = (Path(__file__).parent / 'overview_template.html').read_text()
    html = html.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    html = html.replace('__INPUTHASH__', key)
    target.write_text(html)
    print(f'wrote case/overview.html ({len(html) / 1e6:.2f} MB, {sum(m["n"] for m in meshes)} triangles)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

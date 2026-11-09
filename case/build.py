"""Build every case part (assembled robot frame) -> case/out/*.step|*.stl + parts.json, then run the
case checks, print plates and overview.  Parallel (one process per part), cached by input hash.

    "$KICAD_CASE_PYTHON" case/build.py            # build + all checks
    "$KICAD_CASE_PYTHON" case/build.py --only-parts
"""
import concurrent.futures as cf
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'robot'
STAMP = ROOT / 'build' / 'case' / 'stamps.json'
sys.path.insert(0, str(HERE))

REVISION = 'A1V4-r3'           # base + lid: skeleton, integrated-board retention; plate-2 parts stay at A1V4-r1 (frozen)
CORNERS = ('FL', 'FR', 'RL', 'RR')

# name -> (role, printable, print base rotation [rx, ry] or None for auto, supports)
PRODUCTION = {
    'base': ('shell', [0, 0], True),
    'lid': ('lid', [180, 0], False),
    'cap_front': ('bracket', [180, 0], False),
    'cap_rear': ('bracket', [180, 0], False),
    **{f'thigh_{c}': ('other', [180, 0], False) for c in CORNERS},
    **{f'foot_{c}': ('other', 'foot', False) for c in CORNERS},
}
COUPONS = ['coupon_TEST_ONLY', 'MATING_TEST_leg_FL']
REFERENCES = ['ref_DO_NOT_PRINT_electronics', 'ref_DO_NOT_PRINT_servos', 'ref_DO_NOT_PRINT_hardware']
ALL = list(PRODUCTION) + COUPONS + REFERENCES
# Parts the owner reports printing (and the two test prints): never rebuilt, bytes verified on every run
FROZEN_MANIFEST = json.loads((HERE / 'frozen-plate2-A1V4-r1.json').read_text())
FROZEN = FROZEN_MANIFEST['parts']


def input_hash():
    h = hashlib.sha256()
    place = json.loads((HERE / 'board_placement.json').read_text())
    for f in ('model.py', 'hardware.py', 'build.py', 'board_placement.json', place['source']):
        h.update((HERE / f).read_bytes())
    return h.hexdigest()


# ----------------------------------------------------------------------------- shapes
def shape_for(name):
    import cadquery as cq
    import model as M
    import hardware as HW
    if name == 'base':
        return M.base()
    if name == 'lid':
        return M.lid()
    if name == 'cap_front':
        return M.cap(1)
    if name == 'cap_rear':
        return M.cap(-1)
    if name.startswith('thigh_') or name.startswith('foot_'):
        kind, c = name.split('_')
        th, ft = M.leg_parts(c)
        return th if kind == 'thigh' else ft
    if name == 'MATING_TEST_leg_FL':
        th, ft = M.leg_parts('FL')
        return th.union(ft) if False else cq.Workplane('XY').add(th.vals()).add(ft.vals()).combine(glue=False) \
            if False else compound([th, ft])
    if name == 'coupon_TEST_ONLY':
        return coupon()
    if name == 'ref_DO_NOT_PRINT_electronics':
        return electronics()
    if name == 'ref_DO_NOT_PRINT_servos':
        return servos()
    if name == 'ref_DO_NOT_PRINT_hardware':
        return hardware_solids(HW.instances())
    raise KeyError(name)


def compound(wps):
    import cadquery as cq
    solids = []
    for w in wps:
        solids += [s for s in w.solids().vals()]
    return cq.Workplane('XY').newObject([cq.Compound.makeCompound(solids)])


def electronics_items(labels_only=False):
    """(label, solid) for every bought reference, stable order; mech_check names solids from this list."""
    import model as M
    b = (lambda *a: None) if labels_only else M.box
    items = []
    x0, y0, x1, y1 = M.BOARD_OUTLINE
    items.append(('integrated board PCB', b(x0, x1, y0, y1, M.BOARD_ZB, M.BOARD_ZT)))
    for p in M.BOARD_PARTS:
        xa, ya, xb, yb = p['robotBox']
        z0, z1 = (M.BOARD_ZT, M.BOARD_ZT + p['heightMm']) if p.get('side', 'top') == 'top' else (M.BOARD_ZB - p['heightMm'], M.BOARD_ZB)
        items.append((f"board part {p['ref']}", b(xa, xb, ya, yb, z0, z1)))
    for lab, x0, x1, y0, y1, z0, z1 in M.disp_back_boxes():
        items.append((f'display {lab}', b(x0, x1, y0, y1, z0, z1)))
    usb = M.BOARD_IF.get('usb')
    if usb:
        ux, uy = M.board_xy(*usb['centerMm'])
        ax, ay = usb.get('access', [-1, 0, 0])[:2]
        w, h = M.USB_PLUG_REAL
        zc = M.BOARD_ZT + usb.get('zMm', 3.3) / 2
        L = 15.0
        mouth = usb.get('sizeMm', [9.5, 10.7])[0] / 2
        px, py = ux + ax * mouth, uy + ay * mouth
        xa, xb = sorted((px - abs(ay) * w / 2, px + ax * L + abs(ay) * w / 2)) if ax else (px - w / 2, px + w / 2)
        ya, yb = sorted((py - abs(ax) * w / 2, py + ay * L + abs(ax) * w / 2)) if ay else (py - w / 2, py + w / 2)
        items.append(('USB-C plug overmold', b(xa, xb, ya, yb, zc - h / 2, zc + h / 2)))
    d = M.LED
    items.append(('WS2812 bar envelope', b(d['cx'] - d['sx'] / 2, d['cx'] + d['sx'] / 2, d['cy'] - d['sy'] / 2, d['cy'] + d['sy'] / 2,
                                            d['cz'] - d['sz'] / 2, d['cz'] + d['sz'] / 2)))
    items.append(('power bank envelope', b(M.BANK['x0'], M.BANK['x1'], -M.BANK['y'], M.BANK['y'], M.BANK['z0'], M.BANK['z1'])))
    items.append(('USB->terminal adapter', b(-59.5, -37.5, -24.0, -4.0, 3.0, 18.0)))
    items.append(('USB-A right-angle plug (port 1)', b(-59.5, -37.5, 4.0, 24.0, 3.0, 18.0)))
    return items


def electronics():
    return compound([s for _, s in electronics_items()])


def servos():
    import model as M
    parts = []
    hip = M.hip_servo_FL_place(M.sg90_local(with_horn=True, horn_angle_deg=0.0))
    # horn arm must lie along the thigh (45 deg outward): local arm +X maps to -Y; rotate about shaft
    hip = hip.rotate((M.HIP_X, M.HIP_Y, 0), (M.HIP_X, M.HIP_Y, 1), 135)
    # body must stay toward -Y: rotate the body-only part back
    body = M.hip_servo_FL_place(M.sg90_local(with_horn=False))
    horn = M.hip_servo_FL_place(M.horn_local(0.0)).rotate((M.HIP_X, M.HIP_Y, 0), (M.HIP_X, M.HIP_Y, 1), 135)
    knee = M.leg_to_global(M.knee_servo_leg())
    for c in CORNERS:
        parts += [M.corner_rigid(body, c), M.corner_rigid(horn, c), M.corner_rigid(knee, c)]
    return compound(parts)


def screw_solid(h):
    import cadquery as cq
    hx, hy, hz = h['head']
    ax = h['axis']
    d = 3.0 if h['kind'] == 'M3' else 2.0
    head_d, head_h = (5.5, 3.0) if h['kind'] == 'M3' else (4.0, 1.4)
    # build along +Z from origin then orient: shank goes along the axis, head opposite
    shank = cq.Workplane('XY').circle(d / 2).extrude(h['length'])
    head = cq.Workplane('XY').circle(head_d / 2).extrude(head_h).translate((0, 0, -head_h))
    s = shank.union(head)
    v = cq.Vector(*ax)
    z = cq.Vector(0, 0, 1)
    if (v - z).Length > 1e-6:
        if (v + z).Length < 1e-6:
            s = s.rotate((0, 0, 0), (1, 0, 0), 180)
        else:
            axis = z.cross(v)
            ang = math.degrees(math.acos(max(-1, min(1, z.dot(v)))))
            s = s.rotate((0, 0, 0), axis.toTuple(), ang)
    return s.translate((hx, hy, hz))


def hardware_solids(inst):
    import model as M
    parts = []
    for h in inst:
        parts.append(screw_solid(h))
        if h.get('nut'):
            x, y, z = h['nut']
            nut = M.hexprism_z(0, 0, z - M.NUT_T / 2, z + M.NUT_T / 2, M.NUT_AF).rotate((0, 0, 0), (0, 0, 1), 30)
            parts.append(nut.translate((x, y, 0)).cut(M.cyl(x, y, z - 2, z + 2, 3.0)))   # flats face the slot walls
    return compound(parts)


def coupon():
    """TEST ONLY coupon: SG90 hip pocket corner (real walls), hip horn slot (as printed: open upward),
    one M3 hole with the side nut slot, and the slenderest post (USB-end saddle ridge, real height)."""
    import cadquery as cq
    import model as M
    b = M.box
    s = b(0, 70, 0, 34, 0, 2.0)
    # SG90 pocket: 12.5 x 23.2 opening (same as the base), 3 mm walls, 10 mm tall
    s = s.union(b(0, 18.5, 0, 29.2, 0, 10.0)).cut(b(3.0, 15.5, 3.0, 26.2, 2.0, 10.1))
    # horn slot block, printed slot-up exactly like the thigh (thigh prints upside down)
    blk = b(22, 50, 2, 16, 0, 8.0)
    hub2d, arm2d = M.horn_profile(M.FIT * 0.6)
    depth = M.HORN['hub_h'] + 0.2
    slot = hub2d.extrude(depth).union(arm2d.extrude(depth)).translate((27.0, 9.0, 8.0 - depth + 0.01))
    blk = blk.cut(slot).cut(M.cyl(27.0 + M.HORN['hole_r'], 9.0, 2.0, 8.1, 1.5))
    s = s.union(blk)
    # M3 hole + side-entry nut slot identical to the cap-screw corner (nut 2.4 in a 5.9 x 2.8 slot)
    nb = b(54, 64, 2, 16, 0, 14.0).cut(M.cyl(59, 9, 0.5, 14.1, M.M3_CLEAR))
    nb = nb.cut(b(59 - M.NUT_SLOT_W / 2, 59 + M.NUT_SLOT_W / 2, 9 - (M.NUT_AF / 2 + 0.3), 16.1, 6.0, 6.0 + M.NUT_SLOT_H))
    s = s.union(nb)
    # slenderest feature: the LILYGO USB-end support rib, 2.3 x 12.6 mm, 3.7 mm free height, same print direction
    s = s.union(b(20, 32.6, 23, 25.3, 0, 2.0 + 3.7))
    txt = cq.Workplane('XY').workplane(offset=2.0).text('TEST ONLY', 5.0, 0.6, halign='left', valign='bottom',
                                                       kind='bold').translate((33, 26, 0))
    s = s.union(txt)
    return s.translate((-35, -100, 0))


# ----------------------------------------------------------------------------- export worker
def export_one(name):
    import cadquery as cq
    s = shape_for(name)
    step = OUT / f'{name}.step'
    stl = OUT / f'{name}.stl'
    cq.exporters.export(s, str(step))
    cq.exporters.export(s, str(stl), tolerance=0.02, angularTolerance=0.1)
    v = s.val()
    bb = v.BoundingBox()
    return name, {'volumeMm3': round(sum(x.Volume() for x in s.solids().vals()), 1),
                  'bbox': [round(a, 3) for a in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)]}


# ----------------------------------------------------------------------------- print rotation
def rot_points(P, r):
    import numpy as np
    P = P.copy()
    for axis, deg in enumerate(r):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        x, y, z = P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy()
        if axis == 0:
            P[:, 1], P[:, 2] = y * c - z * s, y * s + z * c
        elif axis == 1:
            P[:, 0], P[:, 2] = x * c + z * s, -x * s + z * c
        else:
            P[:, 0], P[:, 1] = x * c - y * s, x * s + y * c
    return P


def stl_points(path):
    import numpy as np
    data = path.read_bytes()
    n = int.from_bytes(data[80:84], 'little')
    if 84 + 50 * n == len(data):
        arr = np.frombuffer(data[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n)
        return arr['v'].reshape(-1, 3).astype(float)
    pts = [list(map(float, l.split()[1:4])) for l in data.decode().splitlines() if l.strip().startswith('vertex')]
    return np.array(pts)


def print_rotation(name, base):
    """[rx, ry, rz]: lay the part on its flat print face, then turn about Z so the long side runs along X."""
    import numpy as np
    import model as M
    P = stl_points(OUT / f'{name}.stl')
    if base == 'foot':
        c = name.split('_')[1]
        sx, sy = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}[c]
        a = math.radians(45)
        v = np.array([sx * -math.sin(a), sy * math.cos(a), 0.0])   # +t (outer flat face) must face down
        best = None
        for rx in range(-180, 180, 1):
            for ry in (-90, -45, 0, 45, 90, 135, 180, -135):
                w = rot_points(v[None, :], [rx, ry, 0])[0]
                err = np.linalg.norm(w - np.array([0, 0, -1]))
                if best is None or err < best[0]:
                    best = (err, rx, ry)
        base = [best[1], best[2]]
    best = None
    for rz in range(0, 180, 1):
        Q = rot_points(P, [base[0], base[1], rz])
        ext = Q.max(0) - Q.min(0)
        if ext[0] + 1e-6 >= ext[1]:
            if best is None or ext[1] < best[0] - 1e-6:
                best = (ext[1], rz)
    return [base[0], base[1], best[1]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    h = input_hash()
    stamps = json.loads(STAMP.read_text()) if STAMP.exists() else {}
    bad = [e for n, f in FROZEN.items() for e, k in ((f'{n}.stl', 'stlSha256'), (f'{n}.step', 'stepSha256'))
           if not (OUT / e).exists() or hashlib.sha256((OUT / e).read_bytes()).hexdigest() != f[k]]
    if bad:
        sys.exit(f'frozen plate-2 files changed or missing: {bad} (restore them from git commit 2ef9e2c)')
    only = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--parts=')), None)
    todo = [n for n in ALL if n not in FROZEN and (only is None or n in only) and (
        stamps.get(n, {}).get('hash') != h or not (OUT / f'{n}.step').exists() or not (OUT / f'{n}.stl').exists())]
    if todo:
        print(f'building {len(todo)} parts on {os.cpu_count()} cores: {todo}', flush=True)
        with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            for name, info in ex.map(export_one, todo):
                stamps[name] = {'hash': h, **info}
                print('  built', name, info['bbox'], flush=True)
        STAMP.write_text(json.dumps(stamps, indent=1))
    else:
        print('parts up to date')
    rots = stamps.get('_rotations', {})
    if rots.get('hash') != h:
        rots = {'hash': h}
        for n, (role, base, sup) in PRODUCTION.items():
            rots[n] = FROZEN[n]['printRotateDeg'] if n in FROZEN else print_rotation(n, base)
        rots['MATING_TEST_leg_FL'] = [0, 0, 0]
        stamps['_rotations'] = rots
        STAMP.write_text(json.dumps(stamps, indent=1))
    parts = []
    for n, (role, base, sup) in PRODUCTION.items():
        parts.append({'name': n, 'role': role, 'stl': f'{n}.stl', 'step': f'{n}.step', 'printRotateDeg': rots[n],
                      'supports': sup, 'material': 'PETG', 'revision': 'A1V4-r1' if n in FROZEN else REVISION,
                      'volumeMm3': FROZEN[n]['volumeMm3'] if n in FROZEN else stamps[n]['volumeMm3']})
    parts.append({'name': 'coupon_TEST_ONLY', 'role': 'coupon', 'stl': 'coupon_TEST_ONLY.stl',
                  'step': 'coupon_TEST_ONLY.step', 'printRotateDeg': [0, 0, 0], 'supports': False, 'material': 'PETG',
                  'note': 'TEST ONLY - do not assemble; see case/README.md "In thử trước"'})
    parts.append({'name': 'MATING_TEST_leg_FL', 'role': 'coupon', 'stl': 'MATING_TEST_leg_FL.stl',
                  'step': 'MATING_TEST_leg_FL.step', 'printRotateDeg': [0, 0, 0], 'supports': False, 'material': 'PETG',
                  'note': 'MATING_TEST: the real thigh_FL + foot_FL; printed separately in case/print/mating-test.3mf'})
    for n in REFERENCES:
        parts.append({'name': n, 'role': 'other', 'stl': f'{n}.stl', 'step': f'{n}.step', 'printable': False})
    manifest = {
        'schema': 1, 'revision': REVISION, 'frame': 'PILOT_CONTRACT.json robot body frame (mm, +X front, +Y left, +Z up)',
        'pilotContractSha256': hashlib.sha256((ROOT / 'PILOT_CONTRACT.json').read_bytes()).hexdigest(),
        'variant': 'integrated board (ESP32-S3 + PCA9685 on one PCB; Waveshare display on a harness)',
        'verification': {'nativePCBCheckerApplies': True, 'report': '../reports/mechanical.json',
                         'nativeReport': '../reports/native-case-check.json', 'boardContract': json.loads((HERE / 'board_placement.json').read_text())['source'],
                         'boardFitReport': '../reports/board-fit.json'},
        'overview': '../overview.html',
        'parts': parts,
    }
    if (HERE / 'print/production-check.json').exists():
        manifest['printProject'] = {'file': '../print/production.3mf', 'report': '../print/production-check.json'}
    (OUT / 'parts.json').write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n')
    print('wrote case/robot/parts.json')
    subprocess.run([sys.executable, str(ROOT / 'tools/case/export_board_frame.py')], cwd=ROOT, check=True)
    if '--only-parts' in sys.argv:
        return
    py = sys.executable
    for script in ('write_fastener_map.py', 'mech_check.py', 'make_print.py', 'render_overview.py', 'print_check.py'):
        r = subprocess.run([py, str(ROOT / 'tools/case' / script)], cwd=ROOT)
        if r.returncode:
            sys.exit(f'{script} failed ({r.returncode})')
    # native check and assembly-access evidence on the real board contract
    place = json.loads((HERE / 'board_placement.json').read_text())
    subprocess.run([py, str(ROOT / 'tools/case/board_fit.py'), str(HERE / place['source'])], cwd=ROOT)
    subprocess.run([py, str(ROOT / 'tools/case/export_board_frame.py')], cwd=ROOT, check=True)
    subprocess.run([py, str(ROOT / 'tools/case/assembly_access.py')], cwd=ROOT)
    r = subprocess.run([py, str(ROOT / 'tools/case/case_check.py')], cwd=ROOT)
    if r.returncode:
        sys.exit('case_check failed')


if __name__ == '__main__':
    main()

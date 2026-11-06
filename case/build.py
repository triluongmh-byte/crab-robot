"""Build every case part (assembled, contract frame) -> case/out/*.step|*.stl + parts.json.

Fast:  "$KICAD_CASE_PYTHON" case/build.py          (skips parts whose sources did not change)
Force: "$KICAD_CASE_PYTHON" case/build.py --force
Then the checks/plates/overview run from tools/case/ (see case/HANDOFF.md).
"""
import hashlib, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
sys.path.insert(0, str(HERE))
REVISION = 'r001-v1'

# name -> (builder expression, role, printRotateDeg, printable, note)
PARTS = {
    'P01_day':            ("g.bottom()", 'shell', [0, 0, 0], True, 'day nam duoi; support cay trong ham pin'),
    'P02_nap':            ("g.lid()", 'lid', [180, 0, 0], True, 'up mat tren xuong ban in (lop tan sang 0.8 nam tren ban)'),
    'P03_thanh_de_truoc': ("g.clamp_bar(1)", 'bracket', [0, 0, 0], True, 'nam phang'),
    'P04_thanh_de_sau':   ("g.clamp_bar(-1)", 'bracket', [0, 0, 0], True, 'nam phang'),
    'P05_dui_FL':         ("g.femur('FL')", 'other', [180, 0, 0], True, 'up mat tren xuong'),
    'P06_dui_FR':         ("g.femur('FR')", 'other', [180, 0, 0], True, 'up mat tren xuong'),
    'P07_dui_RL':         ("g.femur('RL')", 'other', [180, 0, 0], True, 'up mat tren xuong'),
    'P08_dui_RR':         ("g.femur('RR')", 'other', [180, 0, 0], True, 'up mat tren xuong'),
    'P09_cang_FL':        ("g.tibia('FL')", 'other', 'tibia:FL', True, 'nam nghieng, mat ngoai xuong, ranh horn huong len'),
    'P10_cang_FR':        ("g.tibia('FR')", 'other', 'tibia:FR', True, 'nam nghieng, mat ngoai xuong, ranh horn huong len'),
    'P11_cang_RL':        ("g.tibia('RL')", 'other', 'tibia:RL', True, 'nam nghieng, mat ngoai xuong, ranh horn huong len'),
    'P12_cang_RR':        ("g.tibia('RR')", 'other', 'tibia:RR', True, 'nam nghieng, mat ngoai xuong, ranh horn huong len'),
    'C01_TEST_ONLY_coupon':      ("coupon.coupon()", 'coupon', [0, 0, 0], True, 'in truoc tien; KHONG lap vao robot'),
    'C02_MATING_TEST_dui_FL':    ("g.femur('FL')", 'coupon', [180, 0, 0], True, 'ban in thu that cua P05; dat thi giu lam P05'),
    'C03_MATING_TEST_cang_FL':   ("g.tibia('FL')", 'coupon', 'tibia:FL', True, 'ban in thu that cua P09; dat thi giu lam P09'),
    'REF_servos_DO_NOT_PRINT':   ("refs.servos()", 'other', [0, 0, 0], False, 'tham chieu 8 SG90 + horn'),
    'REF_modules_DO_NOT_PRINT':  ("refs.modules()", 'other', [0, 0, 0], False, 'tham chieu pin, LILYGO, PCA9685, LED'),
    'REF_hardware_DO_NOT_PRINT': ("refs.hardware()", 'other', [0, 0, 0], False, 'tham chieu 8 vit M3 + 8 tan'),
}


def tibia_rotation(leg):
    """Euler [rx, ry, rz] (applied X, then Y, then Z) laying the tibia flat, horn groove up."""
    import math
    import numpy as np
    import geometry as g
    ang = math.radians(g.LEGS[leg][3])
    sx, sy = g.LEGS[leg][0], g.LEGS[leg][1]
    # leg t axis in the world (FL: CCW tangent); groove faces -t for FL, mirrored legs flip
    t = np.array([-math.sin(math.radians(45)), math.cos(math.radians(45)), 0.0])
    t = np.array([t[0] * sx, t[1] * sy, 0.0])
    r = np.array([math.cos(ang), math.sin(ang), 0.0])
    zc = np.array([0, 0, 1.0])
    # target: -t -> +Z (groove up), world z -> +X (long side), r -> whatever keeps det = +1
    R = np.zeros((3, 3))
    tgt = {'t': np.array([0, 0, -1.0]), 'z': np.array([1.0, 0, 0])}
    A = np.stack([t, zc, np.cross(t, zc)], axis=1)
    B = np.stack([tgt['t'], tgt['z'], np.cross(tgt['t'], tgt['z'])], axis=1)
    R = B @ np.linalg.inv(A)
    # R = Rz(c) Ry(b) Rx(a)
    b = math.asin(max(-1, min(1, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return [round(math.degrees(a), 4), round(math.degrees(b), 4), round(math.degrees(c), 4)]


def rotation_of(spec):
    return tibia_rotation(spec.split(':')[1]) if isinstance(spec, str) else spec


def src_hash():
    h = hashlib.sha256()
    for f in sorted(HERE.glob('*.py')):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def build_one(name):
    import cadquery as cq
    import geometry as g, coupon, refs  # noqa: F401
    expr = PARTS[name][0]
    shape = eval(expr)
    step, stl = OUT / f'{name}.step', OUT / f'{name}.stl'
    cq.exporters.export(shape, str(step))
    cq.exporters.export(shape, str(stl), tolerance=0.03, angularTolerance=0.15)
    v = shape.val()
    bb = v.BoundingBox()
    return name, dict(volume=v.Volume(), valid=v.isValid(), solids=len(shape.solids().vals()),
                      bbox=[bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = OUT / '.build-stamp.json'
    h = src_hash()
    old = json.loads(stamp.read_text()) if stamp.exists() else {}
    force = '--force' in sys.argv
    if not force and old.get('src') == h and all((OUT / f'{n}.stl').exists() for n in PARTS):
        print('case/build.py: sources unchanged, parts up to date')
        info = old['info']
    else:
        t = time.time()
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            info = dict(ex.map(build_one, PARTS))
        stamp.write_text(json.dumps({'src': h, 'info': info}, indent=1))
        print(f'built {len(PARTS)} parts in {time.time() - t:.1f}s')
    parts = []
    for name, (expr, role, rot, printable, note) in PARTS.items():
        e = dict(name=name, role=role, stl=f'{name}.stl', step=f'{name}.step', printRotateDeg=rotation_of(rot),
                 supports=(name == 'P01_day'), quantity=1, revision=REVISION, note=note,
                 sha256STL=sha(OUT / f'{name}.stl'))
        if not printable:
            e['printable'] = False
        parts.append(e)
    manifest = dict(schema=1, revision=REVISION, frame='contract body frame (PILOT_CONTRACT.json r1)',
                    material='PETG', overview='../overview.html', parts=parts,
                    verification={'nativePCBCheckerApplies': False, 'report': '../reports/mechanical.json'})
    pp = ROOT / 'case/print/production-check.json'
    if pp.exists() and '--no-print-binding' not in sys.argv:
        manifest['printProject'] = {'file': '../print/production.3mf', 'report': '../print/production-check.json'}
    (OUT / 'parts.json').write_text(json.dumps(manifest, indent=1) + '\n')
    for n, i in info.items():
        if not i['valid'] or i['solids'] != 1:
            print('WARN', n, i)
    write_fastener_map()
    print('parts.json + fastener_map.csv written')


def write_fastener_map():
    import csv, geometry as g
    rows = [['id', 'size', 'qty', 'nut', 'x_mm', 'y_mm', 'head_z_mm', 'entry', 'tool', 'parts', 'step', 'note']]
    for f in g.fasteners():
        rows.append([f['id'], f['size'] + ' (chu so huu)', 1, 'M3 nut in side slot z=%.1f' % f['nut'], f['x'], f['y'], f['zhead'],
                     f['entry'], f['tool'], ' + '.join(f['parts']), f['step'], f['note']])
    for leg in g.LEGS:
        rows.append([f'FT-{leg}', 'SG90 bag tab screw (factory, ~M2 self-tapping)', 2, 'none', '', '', '', 'horizontal from the horn side',
                     'tua vit 4 canh nho', f'knee SG90 + femur {leg}', 7, 'factory screw, not M3'])
        rows.append([f'FH-{leg}', 'SG90 bag horn centre screw (factory)', 1, 'none', '', '', '', 'down through the d6 hole in the femur',
                     'tua vit 4 canh nho', f'hip horn + femur {leg}', 8, 'factory screw, not M3'])
        rows.append([f'FK-{leg}', 'SG90 bag horn centre screw (factory)', 1, 'none', '', '', '', 'through the d6 hole in the tibia',
                     'tua vit 4 canh nho', f'knee horn + tibia {leg}', 9, 'factory screw, not M3'])
    with open(HERE / 'fastener_map.csv', 'w', newline='') as fh:
        csv.writer(fh).writerows(rows)


if __name__ == '__main__':
    main()

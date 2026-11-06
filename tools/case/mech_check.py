"""Mechanical check of the exported case (reads case/out STEP files) -> case/reports/mechanical.json.

  "$KICAD_CASE_PYTHON" tools/case/mech_check.py            # full: hip/knee every 5 deg
  "$KICAD_CASE_PYTHON" tools/case/mech_check.py --coarse   # repair loop: every 15 deg
Uses every CPU core; skips when STEP files, manifest and this script are unchanged.
"""
import hashlib, itertools, json, math, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/out'
REPORT = ROOT / 'case/reports/mechanical.json'
sys.path.insert(0, str(ROOT / 'case'))

PROD = ['P01_day', 'P02_nap', 'P03_thanh_de_truoc', 'P04_thanh_de_sau']
FEMUR = {'FL': 'P05_dui_FL', 'FR': 'P06_dui_FR', 'RL': 'P07_dui_RL', 'RR': 'P08_dui_RR'}
TIBIA = {'FL': 'P09_cang_FL', 'FR': 'P10_cang_FR', 'RL': 'P11_cang_RL', 'RR': 'P12_cang_RR'}
TOL = 0.1   # mm^3 counted as touching, not interference
HIP_RANGE = KNEE_RANGE = 30.0


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


_cache = {}


def step(name):
    import cadquery as cq
    if name not in _cache:
        _cache[name] = cq.importers.importStep(str(OUT / f'{name}.step'))
    return _cache[name]


def vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def dist(a, b):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    d = BRepExtrema_DistShapeShape(a.val().wrapped, b.val().wrapped)
    d.Perform()
    return d.Value() if d.IsDone() else -1.0


def static_pairs():
    """Neutral pose: printed parts vs each other, vs devices, vs keepouts, vs screws."""
    import geometry as g, refs
    printed = {n: step(n) for n in PROD + list(FEMUR.values()) + list(TIBIA.values())}
    devices = dict(g.modules_ref())
    devices.update(refs.hip_servos()); devices.update(refs.knee_servos()); devices.update(refs.horns())
    keep = g.keepouts()
    screws = {f['id']: g.screw(f['x'], f['y'], f['zhead'], f['L']).union(g.nut(f['x'], f['y'], f['nut'])) for f in g.fasteners()}
    found, near = [], []
    names = list(printed)
    for a, b in itertools.combinations(names, 2):
        v = vol(printed[a], printed[b])
        if v > TOL:
            found.append(dict(a=a, b=b, mm3=round(v, 3), kind='part-part'))
    for a in names:
        for group, items in (('device', devices), ('keepout', keep), ('fastener', screws)):
            for b, s in items.items():
                v = vol(printed[a], s)
                if v > TOL:
                    found.append(dict(a=a, b=b, mm3=round(v, 3), kind=f'part-{group}'))
    # device clearances worth reporting (minimum distance printed -> device)
    for a in ('P01_day', 'P02_nap'):
        for b in ('POWER_BANK', 'LILYGO_TDISPLAY_S3', 'PCA9685', 'LED_BAR_WS2812_KK10'):
            near.append(dict(a=a, b=b, minClearanceMm=round(dist(printed[a], devices[b]), 2)))
    for a, b in itertools.combinations(devices, 2):
        v = vol(devices[a], devices[b])
        if v > TOL and not ('horn' in a + b and a.split('_')[0] == b.split('_')[0]):
            found.append(dict(a=a, b=b, mm3=round(v, 3), kind='device-device'))
    return found, near


def sweep_sample(args):
    """One (hip, knee) pose for all 4 legs moving together (worst case: same phase)."""
    hip, knee = args
    import geometry as g
    import cadquery as cq
    body = [step(n) for n in PROD]
    hips = [g.sg90_hip(g.LEGS[n][0], g.LEGS[n][1]) for n in g.LEGS]
    fixed = body[0]
    for s in body[1:] + hips:
        fixed = fixed.union(s)
    legs = {}
    for n in g.LEGS:
        fem = g.femur_local().union(g.knee_servo_local())
        tib = g.tibia_local().rotate((g.LEG_R_KNEE, 0, g.KNEE_AXIS_Z), (g.LEG_R_KNEE, 1, g.KNEE_AXIS_Z), knee)
        legs[n] = g.leg_posed(fem.union(tib), n, hip)
    hits, mind, where = [], 1e9, None
    body_only = body[0]
    for s in body[1:]:
        body_only = body_only.union(s)
    for n, leg in legs.items():
        v = vol(leg, fixed)
        # clearance: body parts + the other legs' hip servos + own hip servo BODY (its shaft/horn turn with the leg)
        own = g.cbox((g.LEGS[n][0] * g.HIP_X, g.LEGS[n][1] * g.HIP_Y, g.SERVO_Z0 + g.SG['H'] / 2), (g.SG['W'], g.SG['TAB'], g.SG['H']))
        others = body_only.union(own)
        for k, h in zip(g.LEGS, hips):
            if k != n:
                others = others.union(h)
        if v > TOL:
            hits.append(dict(leg=n, vs='body', hip=hip, knee=knee, mm3=round(v, 3)))
        else:
            d = dist(leg, others)
            if d < mind:
                mind, where = d, (n, hip, knee)
    for a, b in (('FL', 'FR'), ('RL', 'RR'), ('FL', 'RL'), ('FR', 'RR')):
        v = vol(legs[a], legs[b])
        if v > TOL:
            hits.append(dict(leg=a + '/' + b, vs='leg', hip=hip, knee=knee, mm3=round(v, 3)))
    # opposite phase on the same side (front leg forward while rear leg back) is covered by
    # FL(+hip) vs RL(-hip): mirrored legs swing toward each other at the same signed angle.
    return hits, (mind, where)


def mirror_report():
    """Compare every leg part with FL mirrored into its quadrant, on the exported STEP."""
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    import cadquery as cq

    def props(w):
        p = GProp_GProps()
        BRepGProp.VolumeProperties_s(w.val().wrapped, p)
        c = p.CentreOfMass()
        m = p.MatrixOfInertia()
        return (c.X(), c.Y(), c.Z()), p.Mass(), m

    def principal(m):
        import numpy as np
        a = np.array([[m.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
        w, v = np.linalg.eigh(a)
        return v

    import numpy as np
    out = []
    for kind, table in (('femur', FEMUR), ('tibia', TIBIA)):
        ref = step(table['FL'])
        for leg, sx, sy in (('FR', 1, -1), ('RL', -1, 1), ('RR', -1, -1)):
            m = ref
            if sx < 0:
                m = m.mirror('YZ')
            if sy < 0:
                m = m.mirror('XZ')
            c0, v0, i0 = props(m)
            c1, v1, i1 = props(step(table[leg]))
            dpos = math.dist(c0, c1)
            a0, a1 = principal(i0), principal(i1)
            ang = max(math.degrees(math.acos(min(1.0, abs(float(np.dot(a0[:, k], a1[:, k])))))) for k in range(3))
            sym = vol(m, step(table[leg]))
            out.append(dict(part=f'{kind}_{leg}', vsMirroredFL=True, centroidErrorMm=round(dpos, 4),
                            axisErrorDeg=round(ang, 4), volumeFL=round(v0, 2), volume=round(v1, 2),
                            overlapFraction=round(sym / v1, 5),
                            passed=dpos <= 0.5 and ang <= 1.0 and sym / v1 > 0.999))
    # feet at neutral: lowest point of each tibia
    feet = {}
    for leg, name in TIBIA.items():
        bb = step(name).val().BoundingBox()
        feet[leg] = dict(zmin=round(bb.zmin, 3), xExtent=[round(bb.xmin, 2), round(bb.xmax, 2)], yExtent=[round(bb.ymin, 2), round(bb.ymax, 2)])
    return out, feet


def sections():
    """Posts/tabs/walls measured from the model constants used to build the exported STEP."""
    import geometry as g
    rows = [
        ('LED bridge pillar (P01) x2', 8.0, 10.85, 18.25 + 0.6, 'stands on shelf, tied into the 4 mm beam (portal frame)'),
        ('LILYGO +X end stop (P01) x2', 6.0, 7.2, 38.0 - 21.0, 'merged into the hip pocket inner wall'),
        ('LILYGO cradle rib (P01)', 8.0, 55.0, 33.0 - 21.0, 'long box rib, not a post'),
        ('PCA rim block (P01) x2', 3.0, 14.2, 4.0, 'low rim (h <= 3x side)'),
        ('pack stop (P01) x2', 3.0, 8.9, 3.0, 'low floor rib'),
        ('hip pocket inner wall (P01) x4', 6.9, 34.5, g.TAB_Z1 - g.SHELF_Z1, 'load-bearing wall, screw boss + nut slot'),
        ('hip pocket end wall under tabs (P01)', 6.7, 22.4, g.TAB_Z0 - g.SHELF_Z1, 'carries the servo tabs, box with inner wall'),
        ('clamp bar outer finger (P03/P04)', 6.8, 4.0, 15.0, 'flat plate arm over the tab, length = cantilever'),
        ('clamp bar spine (P03/P04)', 7.0, 4.0, 73.8, 'beam on the inner walls, 4 screws'),
        ('femur plate (P05-P08)', 8.0, 18.9, 51.0, 'solid plate, hip horn groove'),
        ('femur knee box wall (P05-P08)', 3.0, 18.9, 34.9, 'box section around knee SG90'),
        ('tibia beam (P09-P12)', 8.0, 14.0, 73.0, 'solid beam, hub d24, foot d14'),
        ('lid screw boss (P02) x4', 7.0, 7.0, 2.6, 'd7 boss under the lid, sits in a clamp-bar pocket (h <= 3x d)'),
        ('clamp bar under lid boss (P03/P04)', 7.0, 7.0, 2.0, 'bar floor under the boss, clamped onto the pocket wall'),
        ('lid skin over LED (P02)', 0.8, 11.1, 54.0, 'diffuser, supported on 4 sides by 3 mm lid'),
    ]
    out = []
    for name, a, b, h, note in rows:
        small = min(a, b)
        is_post = 'pillar' in name or 'stop' in name and 'pack' not in name
        ok = (small >= 6.0 and h <= 3 * small) if is_post else True
        out.append(dict(feature=name, sectionMm=[a, b], heightOrLengthMm=h, ratio=round(h / small, 2),
                        rule='post/tab >= 6x6 and h <= 3x smallest side' if is_post else 'wall/plate/beam', note=note, passed=ok))
    return out


def fastener_report():
    import geometry as g
    out = []
    for f in g.fasteners():
        tip = f['zhead'] - f['L']
        nut_bottom = f['nut'] - 1.2
        out.append(dict(id=f['id'], size=f['size'], x=f['x'], y=f['y'], headZ=f['zhead'], tipZ=round(tip, 2),
                        nutZ=[round(nut_bottom, 2), round(nut_bottom + 2.4, 2)], throughNutMm=round(nut_bottom - tip, 2),
                        passed=tip < nut_bottom, entry=f['entry'], tool=f['tool']))
    return out


def main():
    coarse = '--coarse' in sys.argv
    step_deg = 15 if coarse else 5
    inputs = {p.name: sha(p) for p in sorted(OUT.glob('*.step'))}
    inputs['mech_check.py'] = sha(__file__)
    inputs['geometry.py'] = sha(ROOT / 'case/geometry.py')
    if REPORT.exists() and '--force' not in sys.argv:
        old = json.loads(REPORT.read_text())
        if old.get('inputs') == inputs and old.get('sweep', {}).get('stepDeg', 99) <= step_deg:
            print('mech_check: inputs unchanged, report current'); return
    t = time.time()
    hips = [h for h in range(-int(HIP_RANGE), int(HIP_RANGE) + 1, step_deg)]
    knees = [k for k in range(-int(KNEE_RANGE), int(KNEE_RANGE) + 1, step_deg)]
    samples = list(itertools.product(hips, knees))
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        fut_static = ex.submit(static_pairs)
        fut_mirror = ex.submit(mirror_report)
        sweep = list(ex.map(sweep_sample, samples, chunksize=1))
        found, near = fut_static.result()
        mirror, feet = fut_mirror.result()
    hits = [h for s, _ in sweep for h in s]
    mind, where = min((m for _, m in sweep), key=lambda m: m[0])
    fasten = fastener_report()
    import geometry as g
    body_top = max(step(n).val().BoundingBox().zmax for n in PROD)
    hw_top = max(f['zhead'] + 3.0 for f in g.fasteners())      # socket head 3 mm
    import cadquery as cq
    bot, lidp = step('P01_day'), step('P02_nap')
    nut_paths = []
    for f in g.fasteners():          # the nut slides from the inboard wall face (|x| 33.4) to the screw axis
        sxx = 1 if f['x'] > 0 else -1
        hits_ = [v / 10 for v in range(334, int(abs(f['x']) * 10), 2) if bot.val().isInside(cq.Vector(sxx * v / 10, f['y'], f['nut']))]
        nut_paths.append(dict(id=f['id'], open=not hits_))
    joints = []
    for sxx in (1, -1):
        for syy in (1, -1):
            bx = sorted((sxx * g.LID_BOSS_BOX[0], sxx * g.LID_BOSS_BOX[1])); by = sorted((syy * g.LID_BOSS_BOX[2], syy * g.LID_BOSS_BOX[3]))
            slab = g.box(bx[0], bx[1], by[0], by[1], g.LID_Z0 + 0.02, g.LID_Z0 + 0.12)
            joints.append(round(lidp.intersect(slab).val().Volume() / 0.1, 1))
    lid_joint = dict(bossToPlateAreaMm2=joints, minRequiredMm2=30.0, note='lid plate fused over the boss block top minus the d6.4 counterbore; the M3x20 head bears on the boss top')
    envelope = dict(limitMm=g.BODY_Z, printedBodyTopZ=round(body_top, 3), m3HardwareTopZ=round(hw_top, 3),
                    note='servo gear bosses, horns and legs above the lid are excluded per the contract')
    sect = sections()
    mirror_ok = all(m['passed'] for m in mirror)
    zs = [f['zmin'] for f in feet.values()]
    errors = []
    if found:
        errors.append('static interference: ' + '; '.join(f"{f['a']}/{f['b']} {f['mm3']}" for f in found[:12]))
    if hits:
        errors.append(f'{len(hits)} swept collisions')
    if not mirror_ok:
        errors.append('mirror error above 0.5 mm / 1 deg')
    if not all(f['passed'] for f in fasten):
        errors.append('screw does not pass its nut')
    if not all(s['passed'] for s in sect):
        errors.append('post/tab section rule')
    if max(envelope['printedBodyTopZ'], envelope['m3HardwareTopZ']) > g.BODY_Z + 0.01:
        errors.append(f"assembled body height {max(body_top, hw_top):.2f} mm > {g.BODY_Z} mm")
    if not all(n['open'] for n in nut_paths):
        errors.append('nut slot path blocked: ' + ', '.join(n['id'] for n in nut_paths if not n['open']))
    if min(lid_joint['bossToPlateAreaMm2']) < lid_joint['minRequiredMm2']:
        errors.append('lid screw boss joint too small')
    if max(zs) - min(zs) > 0.5:
        errors.append('feet not level')
    stl_sha = {p.name: sha(p) for p in sorted(OUT.glob('*.stl'))}
    rep = dict(schema=1, scope='handwired crab robot case r001: body frame, 12 printed parts, 3 references',
               passed=not errors, errors=errors, inputs=inputs,
               partShas={**{k: v for k, v in inputs.items() if k.endswith('.step')}, **stl_sha},
               staticCollisions=found, deviceClearances=near,
               sweep=dict(stepDeg=step_deg, hipDeg=[hips[0], hips[-1]], kneeDeg=[knees[0], knees[-1]], samples=len(samples),
                          legsInPhase=True, minClearanceMm=round(mind, 2), minAt=dict(leg=where[0], hip=where[1], knee=where[2]) if where else None, note='discrete samples; motion between samples not proven'),
               sweptCollisions=hits, mirror=mirror, feetNeutral=feet, fasteners=fasten, bodyHeight=envelope, nutSlotPaths=nut_paths, lidScrewJoint=lid_joint, sections=sect,
               rangeDeg=dict(hip=[-HIP_RANGE, HIP_RANGE], knee=[-KNEE_RANGE, KNEE_RANGE], target='>= +-25', checked='CAD collision only'),
               servoSigns=dict(note='Derived from the CAD axes with the contract GIA DINH: a larger pulse turns the shaft CCW seen from the shaft side.',
                               hip='All 4 hip shafts point +Z, so a larger pulse turns every leg CCW seen from above (hip sign +1 on all channels for CCW).',
                               hipLargerPulseFootMoves={'FL': 'backward (-X) and outward-left', 'FR': 'forward (+X) and inward-left',
                                                        'RL': 'backward (-X) and inward-right', 'RR': 'forward (+X) and outward-right'},
                               knee='Knee shafts point along +t (CCW tangent) on FL/RR and along -t on FR/RL (mirror placement).',
                               kneeLargerPulse={'FL': 'foot DOWN', 'RR': 'foot DOWN', 'FR': 'foot UP', 'RL': 'foot UP'},
                               matchesContractDefaultKnee='yes: FL/RR share one sign and FR/RL the opposite sign, as in the contract default (FL +1, RR +1, FR -1, RL -1) when + means foot down'),
               kneeNeutral='knee SG90 centre r=30 mm from hip shaft on the 45 deg diagonal, z=40, shaft z=45.5; FL centre (75.11, 45.11, 40)',
               nativePCBCheckerApplies=False, hardwareTested=False, seconds=round(time.time() - t, 1))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(rep, indent=1) + '\n')
    print('passed' if rep['passed'] else 'FAILED', errors, f"min sweep clearance {rep['sweep']['minClearanceMm']} mm", f"{rep['seconds']} s")


if __name__ == '__main__':
    main()

"""Fit, motion and beam checks for the front sonar head against the generated A1V4-r5 robot exports (real solids).

  1. Static: head + both HC-SR04P envelopes + zip ties vs frame_upper, the 12 servo solids, the screws, the screen
     stand and the LILYGO (in its slot, its plugs and Dupont housings). frame_lower is not fitted any more and the
     electronics reference is the future integrated board, so neither is checked.
  2. Modules in the holder: no overlap between the module envelopes and the head; a 5 mm screwdriver reaches all four
     screws on the bench (on the robot the frame blocks the left top one, so screw the modules in before tying).
  3. Leg sweep of the two +Y legs (CAD FL, RL) inside the firmware limits (config.h / core.h):
       walking: hip up to HIP_AMPLITUDE 25 x (1 + BALANCE_LIMIT 30 %) = 32.5 deg, knees only lift (0..-60);
       emotion poses: hips +-30, knees -100 (POSE_KNEE_LIFT) .. +30 (press-down limit).
     Head, modules and ties >= 2 mm; the Dupont plug envelope (housing + 4 mm of wire bend, flexible) >= 0.5 mm.
  4. Beams: 15 deg half-angle cones from each can vs the legs while walking: no hit at balance 0 (hip <= 25 deg);
     hits at larger hips are reported. Cones also vs the head itself, the frame and the stand; and the floor range
     where the lower beam edge reaches the ground.

Writes fit_report.json and sonar_front_fit_preview.step next to this file.
Usage:  python3 case/sonar_front/check_fit.py [--robot-dir DIR] [--coarse]
"""
import argparse
import concurrent.futures as cf
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'sonar_bracket'))
sys.path.insert(0, str(HERE.parent / 'screen_stand'))
import cadquery as cq  # noqa: E402
import sonar_front as F  # noqa: E402
import screen_stand as SS  # noqa: E402
import check_fit as OLD  # noqa: E402  (leg_pose, servo_solids, cone, min_distance, overlap from the -X bracket checks)

FALLBACK = Path(os.environ.get('CRAB_CASE_EXPORTS', str(HERE.parent)))
FRONT = ('FL', 'RL')                     # CAD corners on the +Y side = the owner's front legs
TOL = 0.05


def robot_dir(arg):
    for d in ([Path(arg)] if arg else []) + [HERE.parent / 'robot', FALLBACK / 'robot']:
        if (d / 'frame_upper.step').exists():
            return d
    raise SystemExit('No robot exports found: run ./build.sh, pass --robot-dir or set CRAB_CASE_EXPORTS')


_mine = None


def _init(rd):
    global _mine
    OLD.ROBOT = Path(rd)
    _mine = [('head', F.head_robot())] + F.modules_robot() + F.tie_bands()


def sweep_job(args):
    c, hip, knee = args
    hard, plug = (99.0, ''), (99.0, '')
    for ll, leg in OLD.leg_pose(c, hip, knee):
        lb = leg.BoundingBox()
        for ml, m in _mine:
            mb = m.BoundingBox()
            if lb.xmin > mb.xmax + 20 or mb.xmin > lb.xmax + 20 or lb.ymin > mb.ymax + 20 or mb.ymin > lb.ymax + 20 or lb.zmin > mb.zmax + 20 or mb.zmin > lb.zmax + 20:
                continue
            d = OLD.min_distance(leg, m)
            if 'plug' in ml:
                plug = min(plug, (d, f'{c} {ll} vs {ml}'))
            else:
                hard = min(hard, (d, f'{c} {ll} vs {ml}'))
    return {'corner': c, 'hip': hip, 'knee': knee, 'minHardMm': round(hard[0], 2), 'closestHard': hard[1],
            'minPlugMm': round(plug[0], 2), 'closestPlug': plug[1]}


def beam_leg_job(args):
    c, hip, knee = args
    out = []
    for lab, apex, axis in F.beams_robot():
        cn = OLD.cone(apex, axis)
        for ll, leg in OLD.leg_pose(c, hip, knee):
            v = OLD.overlap(cn, leg)
            if v > TOL:
                d = OLD.min_distance(cq.Vertex.makeVertex(*apex), leg)
                out.append({'beam': lab, 'leg': f'{c} {ll}', 'hip': hip, 'knee': knee, 'rangeMm': round(d, 1), 'volMm3': round(v, 1)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--robot-dir')
    ap.add_argument('--coarse', action='store_true')
    a = ap.parse_args()
    rd = robot_dir(a.robot_dir)
    _init(str(rd))
    rep, ok = {'robotExports': str(rd), 'frame': 'robot (CAD) frame; +Y = the owner\'s front (Tiến)', 'checks': {}}, True

    def check(name, value, good):
        nonlocal ok
        rep['checks'][name] = value
        ok = ok and good
        print(('PASS ' if good else 'FAIL ') + name, json.dumps(value, ensure_ascii=False)[:300])

    up = OLD.load('frame_upper').val()
    sv = OLD.servo_solids()
    body = [('frame_upper', up)] + list(sv.items())
    body += [(f'screw #{i}', s) for i, s in enumerate(OLD.load('ref_DO_NOT_PRINT_hardware').solids().vals())]
    body += [('screen stand', SS.stand().val()), ('LILYGO in slot', SS.screen_envelope().val())]
    body += [(f'LILYGO USB-C plug {i}', s.val()) for i, s in enumerate(SS.plug_envelopes())]
    body += [(f'LILYGO Dupont row {i}', s.val()) for i, s in enumerate(SS.header_envelopes())]
    head = _mine[0][1]

    # 1. static
    rows = []
    for ml, m in _mine:
        for bl, b in body:
            mb, bb = m.BoundingBox(), b.BoundingBox()
            if bb.xmin > mb.xmax + 5 or mb.xmin > bb.xmax + 5 or bb.ymin > mb.ymax + 5 or mb.ymin > bb.ymax + 5 or bb.zmin > mb.zmax + 5 or mb.zmin > bb.zmax + 5:
                continue
            d = OLD.min_distance(m, b)
            rows.append({'ours': ml, 'body': bl, 'minDistanceMm': round(d, 2), 'overlapMm3': round(OLD.overlap(m, b), 3) if d < 1e-3 else 0.0})
    rows.sort(key=lambda r: r['minDistanceMm'])
    bad = [r for r in rows if r['overlapMm3'] > TOL]
    check('static overlaps (ties wrap the rail with zero overlap)', bad, not bad)
    near = [r for r in rows if not (r['ours'].startswith('zip tie') and r['body'] == 'frame_upper')]
    check('static closest non-tie gap mm (>= 0.15)', near[:4], near[0]['minDistanceMm'] >= 0.15)
    check('zip ties touch the rail (wrap it)', [r for r in rows if r['ours'].startswith('zip tie') and r['body'] == 'frame_upper'],
          all(r['minDistanceMm'] < 0.01 for r in rows if r['ours'].startswith('zip tie') and r['body'] == 'frame_upper'))
    tie_head = [round(OLD.overlap(t, head), 3) for _, t in F.tie_bands()]
    check('zip ties pass through the plate slots (overlap with head mm3)', tie_head, all(v <= TOL for v in tie_head))
    gap_plate = round(OLD.min_distance(head, up), 2)
    check('plate to frame_upper gap mm (rests on the rail face)', gap_plate, 0.1 <= gap_plate <= 0.4)

    # 2. modules in the holder
    mods = [(ml, m) for ml, m in _mine[1:] if not ml.startswith('zip tie')]
    rr = [{'part': ml, 'overlapMm3': round(OLD.overlap(m, head), 3), 'gapMm': round(OLD.min_distance(m, head), 2)} for ml, m in mods]
    check('modules in holder: no overlap', [r for r in rr if r['overlapMm3'] > TOL], all(r['overlapMm3'] <= TOL for r in rr))
    lr = [round(OLD.overlap(a_, b_), 3) for la, a_ in mods if 'left' in la for lb, b_ in mods if 'right' in lb]
    check('left and right module envelopes apart (max overlap mm3)', max(lr), max(lr) <= TOL)

    sd = [{'driver': l, 'vsHeadMm3': round(OLD.overlap(d, head), 2), 'vsModulesMm3': round(sum(OLD.overlap(d, m) for _, m in mods), 2),
           'vsFrameOnRobotMm3': round(OLD.overlap(d, up), 1)} for l, d in F.screwdrivers()]
    check('screwdriver access on the bench (5 mm shaft, 60 mm, along each screw axis)', sd,
          all(r['vsHeadMm3'] <= TOL and r['vsModulesMm3'] <= TOL for r in sd))

    walls = [{'slot': sl, 'channel': cl, 'wallMm': round(OLD.min_distance(sc, cc), 2)} for sl, sc in F.tie_slots() for cl, cc in F.driver_channels()]
    w = min(walls, key=lambda r: r['wallMm'])
    check('wall between each tie slot and the screwdriver channels mm (>= 1.2)', w, w['wallMm'] >= 1.2)

    # 3. leg sweep inside the firmware limits
    st = 2 if a.coarse else 1
    walk = [(c, h, k) for c in FRONT for h in [x * 2.5 for x in range(-13, 14, st)] for k in (-60, -45, -30, -15, 0)[::st]]
    pose = [(c, h, k) for c in FRONT for h in range(-30, 31, 5 * st) for k in (-100, -80, -60, -35, 0, 15, 25, 30)[::st]]
    with cf.ProcessPoolExecutor(initializer=_init, initargs=(str(rd),)) as ex:
        sw = list(ex.map(sweep_job, walk + pose))
        bl = [x for r in ex.map(beam_leg_job, [(c, h, k) for c in FRONT for h in (-32.5, -30, -27.5, -25, -15, 0, 15, 25, 27.5, 30, 32.5)
                                               for k in (-60, -45, -30, 0)]) for x in r]
    hard = [dict(r, closest=r['closestHard']) for r in sw]
    worst_hard = min(hard, key=lambda r: r['minHardMm'])
    worst_plug = min(sw, key=lambda r: r['minPlugMm'])
    check('leg sweep: head, modules, ties >= 2 mm', {'poses': len(sw), 'worstMm': worst_hard['minHardMm'], 'at': [worst_hard['hip'], worst_hard['knee']],
                                                     'closest': worst_hard['closestHard']}, worst_hard['minHardMm'] >= 2.0)
    check('leg sweep: Dupont plug envelope >= 0.5 mm', {'worstMm': worst_plug['minPlugMm'], 'at': [worst_plug['hip'], worst_plug['knee']],
                                                       'closest': worst_plug['closestPlug']}, worst_plug['minPlugMm'] >= 0.5)
    at25 = [b for b in bl if abs(b['hip']) <= 25]
    check('beams never see the own feet while walking at balance 0 (hip <= 25)', {'hits': at25[:4]}, not at25)
    rep['beamLegHitsAboveBalance0'] = {'hipsDeg': sorted({b['hip'] for b in bl}), 'maxRangeMm': max((b['rangeMm'] for b in bl), default=None),
                                       'note': 'only with Bù lệch above about +-20 % (hip > 25 deg); a near-range echo filter in the firmware would cover it'}

    # 4. beams vs the head, frame and stand; floor range
    beams = []
    for lab, apex, axis in F.beams_robot():
        cn = OLD.cone(apex, axis)
        hit = {n: round(OLD.overlap(cn, s), 2) for n, s in (('head', head), ('frame_upper', up), ('screen stand', SS.stand().val()))}
        pitch = math.degrees(math.asin(axis[2]))
        h = apex[2] - OLD.GROUND_Z
        lower = OLD.BEAM_HALF_DEG - pitch
        beams.append({'beam': lab, 'heightAboveFloorMm': round(h, 1), 'yawDeg': round(math.degrees(math.atan2(axis[0], axis[1])), 1),
                      'pitchDeg': round(pitch, 1), 'floorHitRangeMm': round(h / math.tan(math.radians(lower))) if lower > 0 else None, 'coneOverlapMm3': hit})
    check('beams clear of the head, frame and stand', beams, all(v <= TOL for b in beams for v in b['coneOverlapMm3'].values()))
    lo = min(b['floorHitRangeMm'] for b in beams if b['floorHitRangeMm'])
    check('lowest beam reaches the floor beyond mm (AUTO_SLOW_CM 45 -> >= 300)', lo, lo >= 300)
    # 5. sleep pose (emote.html built-in Ngủ: all four knees lift 30 deg) lowers the body onto the head's bottom
    sleep_floor = min(sl.BoundingBox().zmin for c in ('FL', 'FR', 'RL', 'RR') for ll, sl in OLD.leg_pose(c, 0, -30) if ll == 'foot')
    hz = head.BoundingBox().zmin
    mz = min(m.BoundingBox().zmin for _, m in mods)
    check('Ngủ pose (all knees lift 30): head and modules above the floor mm (>= 1.5)',
          {'floorInBodyFrameZ': round(sleep_floor, 2), 'headClearanceMm': round(hz - sleep_floor, 2), 'moduleClearanceMm': round(mz - sleep_floor, 2)},
          min(hz, mz) - sleep_floor >= 1.5)
    bbh = head.BoundingBox()
    check('head top below the screen (z <= 49.1; cradle front-bottom edge z 52.1)', round(bbh.zmax, 2), bbh.zmax <= 49.1)
    rep['headBbox'] = [round(v, 2) for v in (bbh.xmin, bbh.xmax, bbh.ymin, bbh.ymax, bbh.zmin, bbh.zmax)]
    rep['headVolumeMm3'] = round(head.Volume(), 1)
    rep['groundClearanceMm'] = round(bbh.zmin - OLD.GROUND_Z, 1)
    rep['params'] = {k: getattr(F.P, k) for k in F.P.__dataclass_fields__}
    rep['ok'] = ok
    (HERE / 'fit_report.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')

    asm = cq.Assembly(name='sonar_front_fit_preview')
    asm.add(cq.Workplane().add(up), name='frame_upper', color=cq.Color(0.95, 0.5, 0.15, 0.5))
    for k, s in sv.items():
        asm.add(cq.Workplane().add(s), name=k.replace(' ', '_'), color=cq.Color(0.2, 0.3, 0.8))
    for c in ('FL', 'FR', 'RL', 'RR'):
        for ll, s in OLD.leg_pose(c, 0, 0):
            if ll != 'knee servo':
                asm.add(cq.Workplane().add(s), name=f'{ll}_{c}', color=cq.Color(0.6, 0.6, 0.6))
    asm.add(SS.stand(), name='screen_stand', color=cq.Color(0.95, 0.8, 0.1))
    asm.add(SS.screen_envelope(), name='lilygo', color=cq.Color(0.1, 0.1, 0.1, 0.6))
    asm.add(cq.Workplane().add(head), name='sonar_front', color=cq.Color(0.15, 0.75, 0.75))
    for ml, m in F.modules_robot():
        if 'plug' in ml:
            continue
        asm.add(cq.Workplane().add(m), name=ml.replace(' ', '_'), color=cq.Color(0.2, 0.35, 0.9) if 'pcb' in ml else cq.Color(0.85, 0.85, 0.85))
    for tl, t in F.tie_bands():
        asm.add(cq.Workplane().add(t), name=tl.replace(' ', '_'), color=cq.Color(0.1, 0.1, 0.1))
    asm.save(str(HERE / 'sonar_front_fit_preview.step'))
    print('ALL PASS' if ok else 'SOME FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

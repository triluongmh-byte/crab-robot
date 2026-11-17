"""Fit, sweep and beam checks for the sonar turret against the robot exports (case/robot/*.step, outside Git).

Writes fit_report.json and sonar_turret_fit_preview.step here. Never contacts the robot or a printer.

Usage:  python3 case/sonar_turret/check_fit.py [--robot-dir DIR]
"""
import argparse
import concurrent.futures as cf
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'sonar_bracket'))
import cadquery as cq  # noqa: E402
import sonar_turret as T  # noqa: E402
import check_fit as OLD  # noqa: E402  (leg_pose, servo_solids, cone, min_distance, overlap)

P = T.P
ANGLES = list(range(-90, 91, 15))
TOL = 0.05
CLEAR = 1.0      # mm: hard parts must keep at least this gap


def robot_dir(arg):
    for d in ([Path(arg)] if arg else []) + [HERE.parent / 'robot', Path('/Users/macbookpro/harnesses/crab-robot-v17g/case/robot')]:
        if (d / 'frame_upper.step').exists() and (d / 'frame_lower.step').exists():
            return d
    raise SystemExit('No robot exports found: pass --robot-dir')


def head(angle):
    mods, beams = T.modules(angle=angle)
    return [('cradle', T.cradle(angle=angle).val())] + mods, beams


def near(a, b, pad=10.0):
    x, y = a.BoundingBox(), b.BoundingBox()
    return not (x.xmin > y.xmax + pad or y.xmin > x.xmax + pad or x.ymin > y.ymax + pad or y.ymin > x.ymax + pad or
                x.zmin > y.zmax + pad or y.zmin > x.zmax + pad)


def leg_job(args):
    rd, c, hip, knee = args
    OLD.ROBOT = Path(rd)
    best = (99.0, '')
    legs = OLD.leg_pose(c, hip, knee)
    for ang in (-90, -45, 0, 45, 90):
        parts, _ = head(ang)
        for ll, leg in legs:
            for ml, m in parts:
                if near(leg, m, 5):
                    d = OLD.min_distance(leg, m)
                    best = min(best, (d, f'{c} {ll} vs {ml} @ turret {ang}'))
    return {'corner': c, 'hip': hip, 'knee': knee, 'minMm': round(best[0], 2), 'closest': best[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--robot-dir')
    a = ap.parse_args()
    rd = robot_dir(a.robot_dir)
    OLD.ROBOT = rd
    T.validate()
    rep, ok = {'robotExports': str(rd), 'frame': "robot (CAD) frame; +Y = the owner's front (Tiến)", 'checks': {}}, True

    def check(name, value, good):
        nonlocal ok
        rep['checks'][name] = {'value': value, 'pass': good}
        ok = ok and good
        print(('PASS ' if good else 'FAIL ') + name, json.dumps(value, ensure_ascii=False)[:400])

    up = OLD.load('frame_upper').val()
    sv = OLD.servo_solids()
    body = [('frame_upper', up)] + list(sv.items())
    body += [(f'screw #{i}', s) for i, s in enumerate(OLD.load('ref_DO_NOT_PRINT_hardware').solids().vals())]
    legs0 = [(f'{c} {ll}', s) for c in OLD.CORNERS for ll, s in OLD.leg_pose(c, 0, 0)]
    col = T.column().val()
    servo, horn = T.sg90()
    servo, horn = servo.val(), horn.val()

    # 1. static: column + turret servo against the body
    worst = []
    for n, s in [('column', col), ('SG90 turret', servo)]:
        for bn, b in body + legs0:
            if near(s, b):
                v = OLD.overlap(s, b)
                if v > TOL:
                    worst.append((n, bn, round(v, 2)))
    check('column and servo clear of frame, leg servos, screws, legs', worst or 'none', not worst)
    check('servo in the pocket (no overlap, fit gap)', round(OLD.overlap(col, servo), 3), OLD.overlap(col, servo) <= TOL)
    gap = round(OLD.min_distance(col, up), 3)
    check('glue pad on the spine top (gap to frame_upper)', gap, gap <= 0.01)

    # 2. turret sweep -90..90: head against everything fixed
    hits, closest = [], (99.0, '')
    fixed = body + legs0 + [('column', col), ('SG90 turret', servo)]
    for ang in ANGLES:
        parts, _ = head(ang)
        for ml, m in parts:
            for bn, b in fixed:
                if near(m, b, 3):
                    d = OLD.min_distance(m, b)
                    closest = min(closest, (round(d, 2), f'{ml} vs {bn} @ {ang}'))
                    if d < CLEAR and not (ml == 'cradle' and bn == 'SG90 turret'):
                        hits.append((ang, ml, bn, round(d, 2)))
    check(f'turret sweep {ANGLES[0]}..{ANGLES[-1]} keeps >= {CLEAR} mm', hits or {'closest': closest}, not hits)
    hb = T.head_bottom()
    check('rotating head over the 45 mm wire bundle (owner)', {'headBottomOverFrame': round(hb - P.frame_top, 1), 'bundle': P.wires_h},
          hb - P.frame_top >= P.wires_h + P.wire_margin)

    # 3. legs in every pose the page can send (v34 emotions: hips +-40, knee lift up to 150, press down to 55) against
    # the head at five turret angles. In OLD.leg_pose a NEGATIVE knee lifts the foot up and out (-100: foot z 44..83,
    # x 53..111); a positive knee folds it inwards, and +100 already runs into frame_upper, so +150 cannot be reached.
    jobs = [(str(rd), c, h, k) for c, h, k in itertools.product(OLD.CORNERS, (-40, -25, 0, 25, 40), (-150, -120, -100, -55, 0, 30, 55))]
    with cf.ProcessPoolExecutor() as ex:
        res = list(ex.map(leg_job, jobs))
    w = min(res, key=lambda r: r['minMm'])
    bad = [r for r in res if r['minMm'] < CLEAR]
    check('legs (hip +-40, knee lift 150 / press 55) never reach the head', {'worst': w, 'below': len(bad)}, not bad)

    # 4. beams: clear of the body and the standing legs at every angle; floor range
    beam_hits = []
    for ang in ANGLES:
        _, beams = head(ang)
        for lab, apex, axis in beams:
            cn = OLD.cone(apex, axis, half_deg=P.beam_half, length=300)
            for bn, b in body + legs0 + [('column', col)]:
                if near(cn, b, 0):
                    v = OLD.overlap(cn, b)
                    if v > TOL:
                        beam_hits.append((ang, lab, bn, round(v, 1)))
    check('beams clear of the body and the standing legs', beam_hits or 'none', not beam_hits)
    h = T.can_z() - OLD.GROUND_Z
    rep['beams'] = {'canCentreOverFloorMm': round(h, 1), 'floorHitMm': round(h / math.tan(math.radians(P.beam_half)), 0),
                    'lowestSeenAt25cmMm': round(h - 250 * math.tan(math.radians(P.beam_half)), 0),
                    'bundleClearedBeyondMm': round((T.can_z() - P.frame_top - P.wires_h) / math.tan(math.radians(P.beam_half)), 0)}
    print('INFO beams', rep['beams'])

    rep['ok'] = ok
    (HERE / 'fit_report.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    asm = cq.Assembly(name='sonar_turret_fit_preview')
    asm.add(up, name='frame_upper', color=cq.Color(1.0, 0.45, 0.1, 0.6))
    for n, s in list(sv.items()):
        asm.add(s, name=n, color=cq.Color(0.15, 0.3, 0.8, 0.6))
    for n, s in legs0:
        asm.add(s, name=n, color=cq.Color(1.0, 0.85, 0.1, 0.6))
    asm.add(col, name='column (print)', color=cq.Color(0.9, 0.15, 0.1))
    asm.add(servo, name='SG90 turret CH8', color=cq.Color(0.1, 0.25, 0.9))
    asm.add(horn, name='horn', color=cq.Color(0.95, 0.95, 0.95))
    parts, beams = head(0)
    for n, s in parts:
        asm.add(s, name=n + (' (print)' if n == 'cradle' else ''), color=cq.Color(0.9, 0.15, 0.1) if n == 'cradle' else
                cq.Color(0.1, 0.5, 0.25) if 'HC' in n else cq.Color(0.05, 0.05, 0.05))
    for lab, apex, axis in beams:
        asm.add(OLD.cone(apex, axis, half_deg=P.beam_half, length=160), name=f'beam {lab}', color=cq.Color(0.3, 1.0, 0.5, 0.15))
    asm.add(cq.Workplane().box(60, 25, P.wires_h, centered=(True, False, False)).translate((0, -34, P.frame_top)).val(),
            name='wire bundle 45 mm (position illustrative)', color=cq.Color(0.6, 0.3, 0.1, 0.3))
    asm.export(str(HERE / 'sonar_turret_fit_preview.step'))
    asm.export(str(HERE / 'sonar_turret_fit_preview.glb'), tolerance=0.1, angularTolerance=0.2)
    print('OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

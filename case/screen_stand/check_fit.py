"""Fit checks for the screen stand against the generated A1V4-r5 robot exports (real solids).

  1. Seated: the stand does not overlap frame_upper or the servos.
  2. Screen: the shell envelope sits in the slots with no overlap with the stand, frame or servos, and it can
     slide in along the screen's own height from above without touching the stand.
  3. USB-C: a plug path at either end clears the stand, the frame and the servos.
  4. Snap: lowering the stand straight down onto the crossbar only meets it at the barbs, and by no more
     than the barb depth.

Writes fit_report.json and screen_stand_fit_preview.step next to this file.
Usage:  python3 case/screen_stand/check_fit.py [--robot-dir DIR]   ($CRAB_CASE_EXPORTS/robot as a fallback)
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cadquery as cq  # noqa: E402
import screen_stand as S  # noqa: E402

FALLBACK = Path(os.environ.get('CRAB_CASE_EXPORTS', str(HERE.parent)))
TOL = 0.05


def robot_dir(arg):
    for d in ([Path(arg)] if arg else []) + [HERE.parent / 'robot', FALLBACK / 'robot']:
        if (d / 'frame_upper.step').exists():
            return d
    raise SystemExit('No robot exports found: run ./build.sh or set CRAB_CASE_EXPORTS to a checkout with case/robot')


def overlap(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
        return 0.0
    try:
        return a.intersect(b).Volume()
    except Exception:
        return -1.0


def min_distance(a, b):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value() if d.IsDone() else -1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--robot-dir')
    a = ap.parse_args()
    rd = robot_dir(a.robot_dir)
    up = cq.importers.importStep(str(rd / 'frame_upper.step')).val()
    sv = cq.importers.importStep(str(rd / 'ref_DO_NOT_PRINT_servos.step')).val()
    st = S.stand().val()
    scr = S.screen_envelope().val()
    plugs = [p.val() for p in S.plug_envelopes()]
    rep, ok = {'robotDir': str(rd), 'checks': {}}, True

    def check(name, value, good):
        nonlocal ok
        rep['checks'][name] = value
        ok = ok and good
        print(('PASS ' if good else 'FAIL ') + name, value)

    for n, f in (('frame_upper', up), ('servos', sv)):
        v = overlap(st, f)
        check(f'seated stand vs {n} overlap mm3', round(v, 3), 0 <= v <= TOL)
        check(f'stand to {n} min gap mm', round(min_distance(st, f), 2), min_distance(st, f) >= 0.15)
        v = overlap(scr, f)
        check(f'screen vs {n} overlap mm3', round(v, 3), 0 <= v <= TOL)
    v = overlap(scr, st)
    check('screen vs stand overlap mm3', round(v, 3), 0 <= v <= TOL)
    # screen slides in along its own height from 40 mm above
    a_ = math.radians(S.P.tilt)
    wdir = cq.Vector(-math.sin(a_), 0, math.cos(a_))
    worst = 0.0
    for i in range(1, 81):
        worst = max(worst, overlap(scr.translate(wdir * (0.5 * i)), st))
    check('screen drop-in vs stand worst overlap mm3', round(worst, 3), worst <= TOL)
    for i, h in enumerate(S.header_envelopes()):
        for n, f in (('stand', st), ('frame_upper', up), ('servos', sv)):
            v = overlap(h.val(), f)
            check(f'header row{i} Dupont housings vs {n} overlap mm3', round(v, 3), 0 <= v <= TOL)
    for i, pl in enumerate(plugs):
        for n, f in (('stand', st), ('frame_upper', up), ('servos', sv)):
            v = overlap(pl, f)
            check(f'USB-C plug end{i} vs {n} overlap mm3', round(v, 3), 0 <= v <= TOL)
    # snap: lower the stand onto the crossbar; contact only at the barbs
    worst, at = 0.0, None
    for i in range(1, 41):
        dz = 0.25 * i
        v = overlap(st.translate(cq.Vector(0, 0, dz)), up)
        if v > worst:
            worst, at = v, dz
    barb_vol = 2 * S.P.tab_w * 0.5 * (S.P.barb + S.P.gap) * 1.0
    check('snap-on interference (barbs only) mm3', {'worst': round(worst, 2), 'atLiftMm': at, 'barbBound': round(barb_vol * 1.6, 2)},
          0 < worst <= barb_vol * 1.6)
    bb = st.BoundingBox()
    rep['bbox'] = [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)]
    rep['params'] = {k: getattr(S.P, k) for k in S.P.__dataclass_fields__}
    rep['ok'] = ok
    (HERE / 'fit_report.json').write_text(json.dumps(rep, indent=1) + '\n')
    asm = cq.Assembly(name='screen_stand_fit_preview')
    asm.add(cq.Workplane().add(up), name='frame_upper', color=cq.Color(0.95, 0.5, 0.15, 0.5))
    asm.add(cq.Workplane().add(sv), name='servos', color=cq.Color(0.2, 0.3, 0.8))
    asm.add(cq.Workplane().add(st), name='screen_stand', color=cq.Color(0.95, 0.8, 0.1))
    asm.add(cq.Workplane().add(scr), name='lilygo_in_shell', color=cq.Color(0.1, 0.1, 0.1, 0.6))
    for i, pl in enumerate(plugs):
        asm.add(cq.Workplane().add(pl), name=f'usb_c_path_{i}', color=cq.Color(0.9, 0.1, 0.1, 0.35))
    asm.save(str(HERE / 'screen_stand_fit_preview.step'))
    print('ALL PASS' if ok else 'SOME FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

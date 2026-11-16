"""Fit checks for the power tray against the generated A1V4-r5 robot exports.

Checks, all with real solids (no grid):
  1. Seated: the tray and the bought-part envelopes do not overlap frame_lower,
     frame_upper or the servos, and the tray floor rests on the floor bars.
  2. Drop-in path: the tray and every part envelope (inflated by the slop on the
     owner's ruler measurements) can be lowered from above the frame_lower
     columns (z 34.4) to their seat without touching frame_lower.
  3. Charging: a USB-C plug envelope reaches the module's +X end straight in
     through the old bank mouth without touching either frame.

Writes fit_report.json and power_tray_fit_preview.step next to this file.

Usage:  python3 case/power_tray/check_fit.py [--robot-dir DIR]
        DIR defaults to ../robot (this checkout), then $CRAB_CASE_EXPORTS/robot.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cadquery as cq  # noqa: E402
import power_tray as PT  # noqa: E402

FALLBACK = Path(os.environ.get('CRAB_CASE_EXPORTS', str(HERE.parent)))
TOL = 0.05            # mm3 overlap treated as numeric noise
INFLATE = 0.75        # mm added on each side of a part envelope (ruler measurements)
TOP_Z = 34.4          # frame_lower column tops: everything enters from above here
STEP_Z = 0.5          # sweep step
# USB-C plug (GIA DINH): overmould 12.5 x 7 mm, port centre 3.5 mm above the module floor
PLUG_W, PLUG_H, PLUG_ZC = 12.5, 7.0, 3.5


def robot_dir(arg):
    for d in ([Path(arg)] if arg else []) + [HERE.parent / 'robot', FALLBACK / 'robot']:
        if (d / 'frame_lower.step').exists():
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


def inflate(s, d):
    bb = s.BoundingBox()
    return PT.box(bb.xmin - d, bb.xmax + d, bb.ymin - d, bb.ymax + d, bb.zmin, bb.zmax).val()


def sweep_hits(shape, frame, z_from):
    """Lower `shape` from z_from (its bottom) to its seat; return the worst overlap and where."""
    bb = shape.BoundingBox()
    worst, at = 0.0, None
    dz = z_from - bb.zmin
    while dz > 0:
        v = overlap(shape.translate(cq.Vector(0, 0, dz)), frame)
        if v > worst:
            worst, at = v, round(bb.zmin + dz, 2)
        dz -= STEP_Z
    return worst, at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--robot-dir')
    a = ap.parse_args()
    rd = robot_dir(a.robot_dir)
    lo = cq.importers.importStep(str(rd / 'frame_lower.step')).val()
    up = cq.importers.importStep(str(rd / 'frame_upper.step')).val()
    sv = cq.importers.importStep(str(rd / 'ref_DO_NOT_PRINT_servos.step')).val()
    tray = PT.tray().val()
    parts = [(n, s.val()) for n, s in PT.components()]
    rep = {'robotDir': str(rd), 'params': PT.P.__dict__ if hasattr(PT.P, '__dict__') else {}, 'checks': {}}
    ok = True

    def check(name, value, good):
        nonlocal ok
        rep['checks'][name] = value
        ok = ok and good
        print(('PASS ' if good else 'FAIL ') + name, value)

    # 1. seated
    for fname, frame in (('frame_lower', lo), ('frame_upper', up), ('servos', sv)):
        v = overlap(tray, frame)
        check(f'seated tray vs {fname} overlap mm3', round(v, 3), 0 <= v <= TOL)
        for n, s in parts:
            v = overlap(inflate(s, INFLATE), frame)
            check(f'seated {n} (+{INFLATE}) vs {fname} overlap mm3', round(v, 3), 0 <= v <= TOL)
    d = min_distance(tray, lo)
    check('tray rests on frame_lower floor bars (gap mm)', round(d, 3), d <= 0.01)
    for n, s in parts:
        v = overlap(s, tray)
        check(f'{n} vs tray overlap mm3', round(v, 3), 0 <= v <= TOL)
    # clearance above the tallest part to frame_upper
    top = max(s.BoundingBox().zmax for _, s in parts)
    check('tallest part top z', round(top, 2), True)
    # 2. drop-in path
    w, at = sweep_hits(tray, lo, TOP_Z + 0.5)
    check('drop-in tray vs frame_lower worst overlap mm3', {'mm3': round(w, 3), 'atZ': at}, w <= TOL)
    for n, s in parts:
        w, at = sweep_hits(inflate(s, INFLATE), lo, TOP_Z + 0.5)
        check(f'drop-in {n} (+{INFLATE}) vs frame_lower worst overlap mm3', {'mm3': round(w, 3), 'atZ': at}, w <= TOL)
    # 3. USB-C plug straight in from the old bank mouth to the module's +X end
    m = PT.pockets()['module']
    zc = PT.P.floor_z + PT.P.floor_t + PLUG_ZC
    yc = (m[2] + m[3]) / 2
    plug = PT.box(m[0] + PT.P.module[0], 75.0, yc - PLUG_W / 2, yc + PLUG_W / 2, zc - PLUG_H / 2, zc + PLUG_H / 2).val()
    for fname, frame in (('frame_lower', lo), ('frame_upper', up), ('servos', sv), ('tray', tray)):
        v = overlap(plug, frame)
        check(f'USB-C plug path vs {fname} overlap mm3', round(v, 3), 0 <= v <= TOL)

    rep['ok'] = ok
    rep['bbox'] = {k: round(getattr(tray.BoundingBox(), k), 2) for k in ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax')}
    rep['params'] = {k: getattr(PT.P, k) for k in PT.P.__dataclass_fields__}
    (HERE / 'fit_report.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    asm = cq.Assembly(name='power_tray_fit_preview')
    asm.add(cq.Workplane().add(lo), name='frame_lower', color=cq.Color(0.95, 0.45, 0.1, 0.5))
    asm.add(cq.Workplane().add(up), name='frame_upper', color=cq.Color(0.95, 0.6, 0.2, 0.35))
    asm.add(cq.Workplane().add(sv), name='servos', color=cq.Color(0.2, 0.3, 0.8))
    asm.add(cq.Workplane().add(tray), name='power_tray', color=cq.Color(0.1, 0.7, 0.3))
    colours = {'holder': cq.Color(0.1, 0.1, 0.1), 'module': cq.Color(0.1, 0.3, 0.9), 'lipo': cq.Color(0.8, 0.8, 0.8)}
    for n, s in parts:
        asm.add(cq.Workplane().add(s), name=n, color=colours[n])
    asm.add(cq.Workplane().add(plug), name='usb_c_plug_path', color=cq.Color(0.9, 0.1, 0.1, 0.4))
    asm.save(str(HERE / 'power_tray_fit_preview.step'))
    print('ALL PASS' if ok else 'SOME FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

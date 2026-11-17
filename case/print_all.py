"""All printed parts designed for the A1V4-r5 crab, on one A1 plate, so the owner can print them in one go to look at.

Writes case/print_all.3mf (unsliced Bambu Studio project, repo PETG profile) and case/print_all_preview.step (the
same layout as a named, coloured STEP for the CAD Viewer). Optionally slices offline. Never contacts a printer.

Status of each part (2026-11-17):
  screen_stand       current: holds the bare LILYGO on the +Y (Tiến) display rim
  switch_holder      usable: zip-ties a rocker switch to a frame bar
  power_tray         shelved: frame_lower is not fitted any more
  sonar_front        current: both HC-SR04P flat in a V, four eyes in a row, on the +Y (Tiến) face
  (sonar_bracket, made for the -X end, is obsolete and no longer on the plate)

Usage:  python3 case/print_all.py [--slice OUTDIR]
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
for d in ('screen_stand', 'power_tray', 'sonar_front'):
    sys.path.insert(0, str(HERE / d))
import screen_stand as SS  # noqa: E402
import power_tray as PT  # noqa: E402
import sonar_front as SF  # noqa: E402

_spec = importlib.util.spec_from_file_location('power_tray_3mf', HERE / 'power_tray' / 'make_3mf.py')
PT3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PT3)

BED, GAP = 256.0, 12.0
PLATE_NAME = 'TẤT CẢ ĐỒ IN — ĐỂ SOI'


def wp(s):
    return s if isinstance(s, cq.Workplane) else cq.Workplane().add(s)


def parts():
    """(name, shape in print orientation on z = 0, support, colour)."""
    stand = SS.stand_local().rotate((0, 0, 0), (1, 0, 0), -90)
    return [(n, wp(s), sup, col) for n, s, sup, col in [
        ('screen_stand', stand, True, (0.95, 0.8, 0.1)),
        ('switch_holder', PT.switch_holder(), False, (0.3, 0.7, 0.3)),
        ('power_tray', PT.gen_step(), False, (0.6, 0.6, 0.65)),
        ('sonar_front', SF.to_print(SF.head_robot()), False, (0.15, 0.75, 0.75)),
    ]]


def layout(sizes):
    """Shelf packing, largest first; returns the centre (x, y) of each part, bed-centred."""
    order = sorted(range(len(sizes)), key=lambda i: -sizes[i][1])
    pos, x, y, row_h, rows = {}, 0.0, 0.0, 0.0, []
    for i in order:
        w, h = sizes[i]
        if x and x + w > BED - 2 * GAP:
            rows.append((y, row_h))
            x, y, row_h = 0.0, y + row_h + GAP, 0.0
        pos[i] = (x + w / 2, y + h / 2)
        x, row_h = x + w + GAP, max(row_h, h)
    total_w = max(pos[i][0] + sizes[i][0] / 2 for i in pos)
    total_h = max(pos[i][1] + sizes[i][1] / 2 for i in pos)
    assert total_w <= BED - 2 * GAP and total_h <= BED - 2 * GAP, f'parts do not fit one plate: {total_w:.0f} x {total_h:.0f}'
    return [(pos[i][0] - total_w / 2, pos[i][1] - total_h / 2) for i in range(len(sizes))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    a = ap.parse_args()
    ps = parts()
    tris = [PT3.export_stl(s, HERE / f'.print_all_{n}.stl') for n, s, _, _ in ps]
    for n, *_ in ps:
        (HERE / f'.print_all_{n}.stl').unlink()
    sizes = [(T[:, :, 0].max() - T[:, :, 0].min(), T[:, :, 1].max() - T[:, :, 1].min()) for T in tris]
    centres = layout(sizes)
    objects = [(n, PT3.centred(T, cx, cy), {} if sup else {'enable_support': '0'})
               for (n, _, sup, _), T, (cx, cy) in zip(ps, tris, centres)]
    dst = HERE / 'print_all.3mf'
    PT3.write_3mf(dst, objects, plate_name=PLATE_NAME, title='print_all', support=True)
    asm = cq.Assembly(name='print_all_preview')
    for (n, s, _, col), (cx, cy) in zip(ps, centres):
        bb = s.val().BoundingBox()
        asm.add(s.translate((cx - (bb.xmin + bb.xmax) / 2, cy - (bb.ymin + bb.ymax) / 2, -bb.zmin)), name=n, color=cq.Color(*col))
    asm.save(str(HERE / 'print_all_preview.step'))
    for (n, *_), (w, h) in zip(ps, sizes):
        print(f'{n}: {w:.0f} x {h:.0f} mm')
    print(dst)
    if a.slice:
        print(json.dumps(PT3.slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

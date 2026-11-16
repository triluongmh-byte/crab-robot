"""Write screen_stand.3mf: an unsliced Bambu Studio project (A1, 0.4 mm, the repo PETG profile) and optionally
slice it offline with the Bambu Studio CLI. Never contacts a printer.

Print orientation: standing on its flat -Y end face. Every wall, lip, post and the snap barbs are then straight
prisms going up, so only the end shelf and the tab roots need a little tree support.

Usage:  python3 case/screen_stand/make_3mf.py [--slice OUTDIR] [--upright]   (--upright = as on the robot, to compare)
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'sonar_bracket'))
import screen_stand as S  # noqa: E402

_spec = importlib.util.spec_from_file_location('power_tray_3mf', HERE.parent / 'power_tray' / 'make_3mf.py')
PT3 = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(HERE.parent / 'power_tray'))
_spec.loader.exec_module(PT3)

PLATE_NAME = 'GIÁ MÀN HÌNH — MỚI — CẦN IN'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    ap.add_argument('--upright', action='store_true')
    a = ap.parse_args()
    shape = S.stand()
    if not a.upright:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), -90)      # -Y end face down onto the bed
    stl = HERE / 'screen_stand_print.stl'
    T = PT3.export_stl(shape, stl)
    dst = HERE / 'screen_stand.3mf'
    PT3.write_3mf(dst, [('screen_stand', PT3.centred(T, 0, 0))], plate_name=PLATE_NAME, title='screen_stand', support=True)
    print(dst)
    if a.slice:
        print(json.dumps(PT3.slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

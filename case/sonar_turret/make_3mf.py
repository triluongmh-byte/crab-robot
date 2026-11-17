"""Write sonar_turret.3mf: both turret parts on one plate, an unsliced Bambu Studio project (A1, 0.4 mm, the repo
PETG profile), and optionally slice it offline with the Bambu Studio CLI. Never contacts a printer.

Print orientation, no support: the column stands on its glue pad; the cradle lies on its disc (the horn recess is
on the bed side, so the disc above it is a short bridge).

Usage:  python3 case/sonar_turret/make_3mf.py [--slice OUTDIR]
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sonar_turret as T  # noqa: E402

_spec = importlib.util.spec_from_file_location('power_tray_3mf', HERE.parent / 'power_tray' / 'make_3mf.py')
PT3 = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(HERE.parent / 'power_tray'))
_spec.loader.exec_module(PT3)

PLATE_NAME = 'THÁP XOAY SONAR — PHỤ KIỆN — CỘT + GIÁ'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    a = ap.parse_args()
    T.validate()
    col = PT3.export_stl(T.column_print(), HERE / 'sonar_turret_column.stl')
    cra = PT3.export_stl(T.cradle_print(), HERE / 'sonar_turret_cradle.stl')
    dst = HERE / 'sonar_turret.3mf'
    PT3.write_3mf(dst, [('turret_column', PT3.centred(col, 0, -18)), ('turret_cradle', PT3.centred(cra, 0, 18))],
                  plate_name=PLATE_NAME, title='sonar_turret', support=False)
    print(dst)
    if a.slice:
        print(json.dumps(PT3.slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

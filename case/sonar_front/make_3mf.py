"""Write sonar_front.3mf: an unsliced Bambu Studio project (A1, 0.4 mm, the repo PETG profile) and optionally slice it
offline with the Bambu Studio CLI. Never contacts a printer.

Print orientation: upside down, the flat top plane on the bed. The back plate, the spine and both module holders then
stand up from it; the can holes and bosses carry teardrops and the tie slots are short bridges, so no support.

Usage:  python3 case/sonar_front/make_3mf.py [--slice OUTDIR]
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sonar_front as F  # noqa: E402

_spec = importlib.util.spec_from_file_location('power_tray_3mf', HERE.parent / 'power_tray' / 'make_3mf.py')
PT3 = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(HERE.parent / 'power_tray'))
_spec.loader.exec_module(PT3)

PLATE_NAME = 'GIÁ SIÊU ÂM TRƯỚC — MỚI — CẦN IN'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    a = ap.parse_args()
    shape = F.to_print(F.head_robot())
    T = PT3.export_stl(shape, HERE / 'sonar_front_print.stl')
    dst = HERE / 'sonar_front.3mf'
    PT3.write_3mf(dst, [('sonar_front', PT3.centred(T, 0, 0))], plate_name=PLATE_NAME, title='sonar_front', support=False)
    print(dst)
    if a.slice:
        print(json.dumps(PT3.slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

"""case/out/: the tile's native frame copies of case/robot (board frame: origin at the outline centre, z=0 on top copper).

case/robot/ holds the sealed robot-frame exports (mechanical checks, print plates, overview). The native case checker
reads parts in the board frame, so every part is rigidly moved by (-dx, -dy, -z_top) and written to case/out/ with the
same names. Parallel over all cores; skips unchanged files. Usage: case-python tools/case/export_board_frame.py [--force]
"""
import concurrent.futures as cf
import hashlib
import json
import math
import os
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ROBOT = ROOT / 'case/robot'
OUT = ROOT / 'case/out'
STAMP = ROOT / 'build/case/board-frame-stamps.json'


def transform():
    place = json.loads((ROOT / 'case/board_placement.json').read_text())
    src = json.loads((ROOT / 'case' / place['source']).read_text())
    return -place['dxMm'], -place['dyMm'], -(place['zBottomMm'] + src['board']['thicknessMm']), -place.get('rotDeg', 0)


def job(args):
    name, (dx, dy, dz, rot) = args
    import cadquery as cq
    s = cq.importers.importStep(str(ROBOT / f'{name}.step')).translate((dx, dy, dz)).rotate((0, 0, 0), (0, 0, 1), rot)
    cq.exporters.export(s, str(OUT / f'{name}.step'))
    data = (ROBOT / f'{name}.stl').read_bytes()
    n = int.from_bytes(data[80:84], 'little')
    rec = np.frombuffer(data[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n).copy()
    V = rec['v'].reshape(-1, 3).astype(float)
    V[:, 0] += dx
    V[:, 1] += dy
    V[:, 2] += dz
    c, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    x, y = V[:, 0].copy(), V[:, 1].copy()
    V[:, 0], V[:, 1] = x * c - y * si, x * si + y * c
    rec['v'] = V.reshape(-1, 9).astype(np.float32)
    (OUT / f'{name}.stl').write_bytes(data[:84] + rec.tobytes())
    return name


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tr = transform()
    man = json.loads((ROBOT / 'parts.json').read_text())
    stamps = json.loads(STAMP.read_text()) if STAMP.exists() else {}
    todo = []
    for p in man['parts']:
        name = p['name']
        h = hashlib.sha256(json.dumps(tr).encode())
        for e in ('step', 'stl'):
            h.update((ROBOT / f'{name}.{e}').read_bytes())
        h = h.hexdigest()
        if '--force' in sys.argv or stamps.get(name) != h or not (OUT / f'{name}.step').exists() or not (OUT / f'{name}.stl').exists():
            todo.append((name, h))
    if todo:
        with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            for name in ex.map(job, [(n, tr) for n, _ in todo]):
                pass
        stamps.update(dict(todo))
        STAMP.parent.mkdir(parents=True, exist_ok=True)
        STAMP.write_text(json.dumps(stamps, indent=1))
    man['frame'] = 'BOARD frame for the native case checker (origin outline centre, z=0 top copper); robot-frame exports are in ../robot/'
    man['robotFrameExports'] = '../robot/'
    man['boardFrameTransform'] = {'translateMm': list(tr[:3]), 'rotateZDeg': tr[3]}
    (OUT / 'parts.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n')
    print(f'case/out board-frame: {len(todo)} rebuilt, {len(man["parts"])} parts')
    return 0


if __name__ == '__main__':
    sys.exit(main())

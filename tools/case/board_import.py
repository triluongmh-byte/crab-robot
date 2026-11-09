"""Pin one published integrated-board enclosure contract as the case's single board source.

Usage: case-python tools/case/board_import.py <path/to/main.enclosure.json> [--dx X --dy Y --rot R --zb Z]

Copies the contract (read-only source) into case/ref/board-<sha8>.enclosure.json and points
case/board_placement.json at it. Geometry never reads a board path outside case/ref/.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--dx', type=float)
    ap.add_argument('--dy', type=float)
    ap.add_argument('--rot', type=float)
    ap.add_argument('--zb', type=float)
    a = ap.parse_args()
    src = Path(a.src)
    data = src.read_bytes()
    json.loads(data)                    # must be valid JSON
    sha = hashlib.sha256(data).hexdigest()
    dst = ROOT / f'case/ref/board-{sha[:8]}.enclosure.json'
    dst.write_bytes(data)
    pf = ROOT / 'case/board_placement.json'
    place = json.loads(pf.read_text())
    place['source'] = f'ref/{dst.name}'
    place['sourceSha256'] = sha
    for k, v in (('dxMm', a.dx), ('dyMm', a.dy), ('rotDeg', a.rot), ('zBottomMm', a.zb)):
        if v is not None:
            place[k] = v
    pf.write_text(json.dumps(place, indent=1, ensure_ascii=False) + '\n')
    print(f'board source -> {dst.relative_to(ROOT)}  {sha[:12]}  placement {place}')


if __name__ == '__main__':
    main()

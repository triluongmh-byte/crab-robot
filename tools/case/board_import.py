"""Pin one published integrated-board contract as the case's single board source, then show what moved.

Usage: case-python tools/case/board_import.py <main.enclosure.json> [--interface engineering/board-interface.json] [--dx X --dy Y --rot R --zb Z]

Copies the contract to case/ref/board-published.enclosure.json and the board interface to case/ref/board-interface.json, and
records the published STEP hash in case/board_placement.json. Geometry never reads a board path outside case/ref/.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / 'case/ref'


def _interfaces(data):
    return {i.get('key') or i.get('name'): {k: i.get(k) for k in ('centerMm', 'access', 'sizeMm', 'zMm')} for i in data.get('interfaces', [])}


def measure_j1(step, contract):
    """Bounds of the J1 body in the published STEP (board-local mm, z from top copper). The contract's box only locates it."""
    import cadquery as cq
    box = next(p['boxMm'] for p in contract['parts'] if p['ref'] == 'J1')
    best = None
    for s in cq.importers.importStep(str(step)).solids().vals():
        b = s.BoundingBox()
        if b.xmin >= box[0] - 1.5 and b.xmax <= box[2] + 1.5 and b.ymin >= box[1] - 1.5 and b.ymax <= box[3] + 1.5:
            if best is None or s.Volume() > best[0]:
                best = (s.Volume(), b)
    if best is None:
        raise SystemExit('J1 body not found in the published STEP')
    b = best[1]
    return {'xMm': [round(b.xmin, 3), round(b.xmax, 3)], 'yMm': [round(b.ymin, 3), round(b.ymax, 3)], 'zMm': [round(b.zmin, 3), round(b.zmax, 3)], 'volumeMm3': round(best[0], 1),
            'note': 'largest solid inside the contract J1 box in the published STEP; a conservative envelope, not a detailed socket (engineering/3D-MODELS.md)'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--interface', default=str(ROOT / 'engineering/board-interface.json'))
    for k in ('dx', 'dy', 'rot', 'zb'):
        ap.add_argument(f'--{k}', type=float)
    a = ap.parse_args()
    data = Path(a.src).read_bytes()
    new = json.loads(data)
    dst = REF / 'board-published.enclosure.json'
    old = json.loads(dst.read_text()) if dst.exists() else {}
    sha = hashlib.sha256(data).hexdigest()
    dst.write_bytes(data)
    pf = ROOT / 'case/board_placement.json'
    place = json.loads(pf.read_text())
    place['source'] = f'ref/{dst.name}'
    place['sourceSha256'] = sha
    for k, v in (('dxMm', a.dx), ('dyMm', a.dy), ('rotDeg', a.rot), ('zBottomMm', a.zb)):
        if v is not None:
            place[k] = v
    bi_path = Path(a.interface)
    if bi_path.exists():
        bi_bytes = bi_path.read_bytes()
        (REF / 'board-interface.json').write_bytes(bi_bytes)
        bi = json.loads(bi_bytes)
        place['interfaceSource'] = 'ref/board-interface.json'
        place['interfaceSha256'] = hashlib.sha256(bi_bytes).hexdigest()
        step_sha = bi.get('pcb', {}).get('stepSha256')
        place['boardStepSha256'] = step_sha
        rel = bi.get('pcb', {}).get('step')
        step = ROOT / rel if rel else None
        if step is not None and step.exists() and hashlib.sha256(step.read_bytes()).hexdigest() != step_sha:
            print(f'WARNING: {rel} does not match the stepSha256 published in board-interface.json')
    if step is not None and step.exists():
        place['stepJ1'] = measure_j1(step, new)
        print('J1 body measured in the published STEP:', place['stepJ1'])
    pf.write_text(json.dumps(place, indent=1, ensure_ascii=False) + '\n')
    o, n = _interfaces(old), _interfaces(new)
    changed = {k: {'was': o.get(k), 'now': n.get(k)} for k in set(o) | set(n) if o.get(k) != n.get(k)}
    print(f'board source -> {dst.relative_to(ROOT)}  {sha[:12]}')
    print('interfaces that changed:', json.dumps(changed, ensure_ascii=False, indent=1) if changed else 'none')
    print('Next: case-python case/build.py (the frame is rebuilt only if its inputs changed), then read reports/assembly-access.json usbCableAssessment.')


if __name__ == '__main__':
    main()

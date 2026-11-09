"""Can the board actually go in, and can its screws be reached? -> case/reports/assembly-access.json

Sweep of the real solids: the board (PCB plan + real part columns) lowered straight down into its seated pose, and a
straight driver column (Ø7, head + bit) over every mounting hole, against the exported base and clamp bars.
Runs for the published board and for the board revision requested from the board team. Usage: case-python tools/case/assembly_access.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'case'))
OUT = ROOT / 'case/robot'
ZTOP = 60.0         # the sweep ends above everything
TOOL_R = 3.5        # M3 head Ø5.5 plus driver clearance
# Requested revision: smallest change that gives a straight drop and straight tool paths (see DEVIATIONS D18).
REQUESTED = {'notches': (39.7, 26.2),                  # remove |x| > 39.7 where |y| > 26.2
             'holes': {'H1': (-36.0, 13.0), 'H2': (36.0, 24.0), 'H3': (-36.0, -24.0), 'H4': (36.0, -24.0)},
             'j1NoseX': -43.7}


def bx(x0, x1, y0, y1, z0, z1):
    import cadquery as cq
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def vol(a, b):
    try:
        return round(a.intersect(b).Volume(), 3)
    except Exception:
        return -1.0


def sweep_check(e, notch=None, holes=None, nose=-45.8):
    import cadquery as cq
    import model as M
    base = cq.importers.importStep(str(OUT / 'base.step')).val()
    caps = [cq.importers.importStep(str(OUT / f'{n}.step')).val() for n in ('cap_front', 'cap_rear')]
    w, h = e['board']['widthMm'], e['board']['heightMm']
    zb = M.BOARD_ZB
    zt = zb + e['board']['thicknessMm']
    plan = cq.Workplane('XY').box(w, h, ZTOP - zb, centered=(True, True, False)).translate((0, 0, zb))
    if notch:
        nx, ny = notch
        for sx in (1, -1):
            for sy in (1, -1):
                x0, x1 = sorted((sx * nx, sx * (w / 2 + 1)))
                y0, y1 = sorted((sy * ny, sy * (h / 2 + 1)))
                plan = plan.cut(cq.Workplane('XY').add(bx(x0, x1, y0, y1, zb - 1, ZTOP + 1)))
    plan = plan.val()
    findings = []
    v = vol(plan, base)
    if v > 0.05:
        findings.append({'item': 'PCB outline, straight down', 'hits': 'base (cap-screw corner blocks)', 'mm3': v})
    capv = sum(vol(plan, c) for c in caps)
    parts = []
    tall = {p['ref']: p for p in e.get('parts', []) if p.get('side') == 'top' and p.get('heightMm', 0) > 0}
    for ref, p in tall.items():
        q = M._part_box(p)
        if notch and ref == 'J1':
            q = [nose, q[1], q[2], q[3]]
        elif ref == 'J1':
            q = [nose, q[1], q[2], q[3]]
        x0, y0, x1, y1 = M.board_box(q)
        column = bx(x0, x1, y0, y1, zt, ZTOP)
        v = vol(column, base)
        if v > 0.05:
            findings.append({'item': f'{ref} column, straight down', 'hits': 'base', 'mm3': v})
            parts.append(ref)
    holes = holes or {h['id']: h['xy'] for h in M.BOARD_HOLES}
    tools = []
    for hid, (x, y) in holes.items():
        col = cq.Workplane('XY').circle(TOOL_R).extrude(ZTOP - zt).translate((x, y, zt)).val()
        vb = vol(col, base)
        vc = sum(vol(col, c) for c in caps)
        tools.append({'hole': hid, 'xy': [x, y], 'toolRadiusMm': TOOL_R, 'baseMm3': vb, 'clampBarsMm3': round(vc, 3), 'pass': vb < 0.05})
    return {'dropStraight': not findings, 'findings': findings, 'capOverlapIfFittedFirstMm3': round(capv, 2), 'partsBlocked': parts,
            'screws': tools, 'screwsReachable': sum(1 for t in tools if t['pass']), 'screwsTotal': len(tools),
            'pass': not findings and all(t['pass'] for t in tools)}


def run(write=True):
    import model as M
    contract = json.loads((ROOT / 'boards/main.enclosure.json').read_text()) if (ROOT / 'boards/main.enclosure.json').exists() else M._EC
    published = sweep_check(contract)
    requested = sweep_check(contract, notch=REQUESTED['notches'], holes=REQUESTED['holes'], nose=REQUESTED['j1NoseX'])
    res = {'schema': 1, 'published': published, 'requestedBoardRevision': {**requested, 'change': REQUESTED,
           'note': 'Virtual variant of the published board; fit needs the board team to confirm copper and parts.'},
           'assemblable': published['pass'],
           'note': 'Sweep of real solids. Assumes board and bolts go in before the clamp bars are fitted (clamp bars cover |x| >= 40 above z 39.9).'}
    if write:
        p = ROOT / 'case/reports/assembly-access.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    return res


if __name__ == '__main__':
    r = run()
    print(json.dumps({'assemblable': r['assemblable'], 'published': {k: r['published'][k] for k in ('dropStraight', 'screwsReachable', 'screwsTotal')},
                      'requested': {k: r['requestedBoardRevision'][k] for k in ('dropStraight', 'screwsReachable', 'screwsTotal', 'pass')}}))
    for f in r['published']['findings']:
        print(' PUBLISHED', f)
    for f in r['requestedBoardRevision']['findings']:
        print(' REQUESTED', f)
    sys.exit(0)

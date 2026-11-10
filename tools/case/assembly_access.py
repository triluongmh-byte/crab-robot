"""Real assembly and access evidence on the exported solids -> case/reports/assembly-access.json

Order checked (the guide follows it): board straight down into frame_lower and its 4 screws; frame_upper straight down
onto the columns; 3 joint screws; hip servos straight down through their windows, 8 tab screws from above; servo plugs
onto the headers; USB-C along the J1 mouth direction; bank slid in from the front. Each path is sampled as real solids.
Parallel over all cores. Usage: case-python tools/case/assembly_access.py
"""
import concurrent.futures as cf
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'case'))
OUT = ROOT / 'case/robot'
ZTOP = 75.0
TOOL_R = 3.5        # M3 head Ø5.5 plus driver clearance


def bx(x0, x1, y0, y1, z0, z1):
    import cadquery as cq
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


_s = {}


def S(name):
    import cadquery as cq
    if name not in _s:
        _s[name] = cq.importers.importStep(str(OUT / f'{name}.step')).val()
    return _s[name]


def vol(a, b):
    try:
        return round(a.intersect(b).Volume(), 3)
    except Exception:
        return -1.0


def sweep_box_job(j):
    """(label, list of boxes [x0,x1,y0,y1,z0,z1], against part names, tolerance). One static column already spans the sweep."""
    lab, boxes, against, tol = j
    out = []
    for b in boxes:
        c = bx(*b)
        for a in against:
            v = vol(c, S(a))
            if v > tol or v < 0:
                out.append({'item': lab, 'box': [round(x, 2) for x in b], 'hits': a, 'mm3': v})
    return {'label': lab, 'pass': not out, 'findings': out}


def board_columns(M, zb, zt):
    """PCB slab column + every top part column, swept straight down from above: lowest position = seated."""
    x0, y0, x1, y1 = M.BOARD_OUTLINE
    cols = [[x0, x1, y0, y1, zb, ZTOP]]
    for p in M.BOARD_PARTS:
        a, b, c, d = p['robotBox']
        cols.append([a, c, b, d, zt, ZTOP])
    return cols


def build_jobs(M, HW):
    zb, zt = M.BOARD_ZB, M.BOARD_ZT
    L, U = ['frame_lower'], ['frame_upper']
    jobs = [('board straight down into frame_lower (PCB + all parts)', board_columns(M, zb, zt), L, 0.05)]
    # every board screw: straight driver column above the hole, with only frame_lower present (they go in before frame_upper)
    for h in M.BOARD_HOLES:
        x, y = h['xy']
        jobs.append((f"board screw {h['id']} driver column (frame_lower only)", [[x - TOOL_R, x + TOOL_R, y - TOOL_R, y + TOOL_R, zt, ZTOP]], L, 0.05))
    # frame_upper straight down onto the columns, board fitted: swept column of frame_upper vs board parts is done as
    # a real sweep below (sweep_upper). Joint screws: driver column above each pad, with frame_upper present.
    for i, (x, y) in enumerate(M.JOINT_SCREWS):
        jobs.append((f'joint screw J{i + 1} driver column (frame_upper fitted)', [[x - TOOL_R, x + TOOL_R, y - TOOL_R, y + TOOL_R, M.TAB_Z1 + 0.02, ZTOP]], U, 0.05))
    # hip servos: body + tabs straight down through frame_upper with the frame assembled
    from build import CORNERS
    for c in CORNERS:
        sx, sy = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}[c]
        cxr, cyr = sx * M.HIP_X, sy * (M.HIP_Y - 5.5)
        # body column 12.2 x 22.8 x down, tabs drop until seated at z 37.4
        jobs.append((f'hip servo {c} straight down into its window', [
            [cxr - 6.1, cxr + 6.1, cyr - 11.4, cyr + 11.4, 21.5, ZTOP],
            [cxr - 5.9, cxr + 5.9, cyr - 16.1, cyr + 16.1, M.TAB_Z0, ZTOP]], ['frame_lower', 'frame_upper'], 0.05))
    # tab screws: a thin screwdriver straight down over each tab hole, with the frame and all hip servos present
    for h in HW.instances():
        if h['id'].startswith('T'):
            x, y, _ = h['head']
            jobs.append((f"tab screw {h['id']} driver column (frame + servos fitted)", [[x - 1.75, x + 1.75, y - 1.75, y + 1.75, M.TAB_Z1 + 0.02, ZTOP]], U + ['ref_DO_NOT_PRINT_servos'], 0.05))
    # board-side connectors: a plug column above each header with the frame assembled and the LED bar excluded
    for p in M.BOARD_PARTS:
        name = (p.get('value', '') or '') + ' ' + p.get('footprint', '')
        if p['heightMm'] >= 6 and any(k in name for k in ('CH', 'LED')):        # J10 (display harness) is plugged before frame_upper goes on
            a, b, c, d = p['robotBox']
            jobs.append((f"plug {p['ref']} straight down onto its header", [[a, c, b, d, zt + 2.0, ZTOP]], ['frame_upper'], 0.5))
    # USB-C: straight plug and cable pulled along the J1 mouth direction, past everything on the way out
    px, py, ax, ay, zc = M.usb_mouth()
    w, h = M.USB_PLUG_REAL
    far = 80.0
    xa, xb = sorted((px, px + ax * far)) if ax else (px - w / 2, px + w / 2)
    ya, yb = sorted((py, py + ay * far)) if ay else (py - w / 2, py + w / 2)
    jobs.append((f'USB-C plug ({w} x {h}) straight out from J1, against the frame and the hip servos', [[xa, xb, ya, yb, zc - h / 2, zc + h / 2]], ['frame_lower', 'frame_upper', 'ref_DO_NOT_PRINT_servos'], 0.05))
    # power bank: slides in from the open front, all the way
    jobs.append(('power bank slides in from the front', [[M.BANK['x0'], 80.0, -M.BANK['y'], M.BANK['y'], M.BANK['z0'], M.BANK['z1']]], ['frame_lower', 'frame_upper'], 0.05))
    # LED bar and display: from below into the upper frame, with frame_upper off the robot
    jobs.append(('LED bar up into its channel (frame_upper off the robot)', [[-28.0, 28.0, -6.0, 6.0, 30.0, 43.49]], U, 0.05))
    d = M.DISP
    jobs.append(('display up into its rim (frame_upper off the robot)', [[M.DISP_X0, M.DISP_X1, M.DISP_Y0, M.DISP_Y1, 34.0, d['z_ledge'] - 0.02]], U, 0.05))
    return jobs


def sweep_upper(M):
    """frame_upper lowered straight down (in steps) onto the frame_lower with the seated board and plugs out: real collision at every step."""
    import cadquery as cq
    up = S('frame_upper')
    zb, zt = M.BOARD_ZB, M.BOARD_ZT
    obstacles = [bx(*M.BOARD_OUTLINE[:2:1], 0, 0, 0, 0) if False else None]
    obstacles = [bx(M.BOARD_OUTLINE[0], M.BOARD_OUTLINE[2], M.BOARD_OUTLINE[1], M.BOARD_OUTLINE[3], zb, zt)]
    for p in M.BOARD_PARTS:
        a, b, c, d = p['robotBox']
        obstacles.append(bx(a, c, b, d, zt, zt + p['heightMm']))
    obstacles.append(S('frame_lower'))
    hits, n = [], 0
    for lift in (40.0, 25.0, 15.0, 10.0, 6.0, 3.0, 1.0, 0.0):
        n += 1
        mv = up.translate(cq.Vector(0, 0, lift))
        for o in obstacles:
            v = vol(mv, o)
            if v > 0.05 or v < 0:
                hits.append({'liftMm': lift, 'mm3': v})
    return {'label': 'frame_upper straight down onto frame_lower (board fitted, no plugs)', 'steps': n, 'pass': not hits, 'findings': hits}


def harness_check(M):
    """Display harness on real solids with the frame seated: GH1.25 plug in the module's back socket, 8 wires to the 8 Dupont housings on J10."""
    import cadquery as cq
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape as D
    import build as B
    items = dict(B.electronics_items())
    mouth = M.DISP_GH_MOUTH_X
    yc = sum(M.DISP_GH_Y) / 2
    plug_len, plug_w = 6.0, 12.5                 # GH1.25 8-pin plug with its wire crimps (GIA DINH; a real plug is shorter and narrower)
    zb, zt = M.DISP_GH_Z[0] + 0.2, M.DISP_GH_Z[1] - 0.2
    plug = bx(mouth, mouth + plug_len, yc - plug_w / 2, yc + plug_w / 2, zb, zt)
    # J10 Dupont housings: the seated box from the board contract, split by pin only for the wire end points
    j10 = items['board part J10'].val()
    bb = j10.BoundingBox()
    fixed = [('frame_upper', S('frame_upper')), ('J10 housings', j10), ('LED bar', items['WS2812 bar envelope'].val())]
    module = [(n, v.val()) for n, v in items.items() if n.startswith('display') and 'connector' not in n]
    plug_hits = {n: vol(plug, s) for n, s in fixed + module if vol(plug, s) > 0.02}
    R = 0.65
    wires, worst = [], (1e9, '')
    for i in range(8):
        xp = bb.xmin + 1.27 + 2.54 * i
        ygh = yc + (i - 3.5) * 1.25
        z_up = 43.5 + 0.7 * i                     # wires rise in the open span y 13..27.5 in front of the module, never under it
        pts = [(mouth + plug_len, ygh, 40.6), (3.5, ygh, 41.6), (6.0, ygh, 41.6), (max(xp + 0.5, 6.0), ygh, z_up), (max(xp + 0.5, 6.0), (bb.ymin + bb.ymax) / 2, z_up), (max(xp + 0.5, 6.0), (bb.ymin + bb.ymax) / 2, bb.zmax + 1.05), (xp, (bb.ymin + bb.ymax) / 2, bb.zmax + 0.7)]
        w = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)) for a, b in zip(pts, pts[1:])])
        for n, s in fixed + module:
            d = D(w.wrapped, s.wrapped)
            d.Perform()
            c = d.Value() - R
            if c < worst[0]:
                worst = (c, n)
        wires.append([[round(v, 2) for v in p] for p in pts])
    ok = not plug_hits and worst[0] > 0.0
    return {'label': 'display harness with frame_upper seated: GH1.25 plug in the module socket, 8 wires to the J10 housings', 'pass': ok,
            'plugBoxMm': {'x': [round(mouth, 2), round(mouth + plug_len, 2)], 'y': [round(yc - plug_w / 2, 2), round(yc + plug_w / 2, 2)], 'z': [round(zb, 2), round(zt, 2)]},
            'plugHits': plug_hits, 'wireMinClearanceMm': round(worst[0], 2), 'closest': worst[1], 'wireTubeDiaMm': 2 * R, 'wires': wires,
            'findings': [] if ok else [{'plugHits': plug_hits, 'wire': worst}],
            'note': 'The plug fits under the module, in front of the socket. All 8 J10 pins are in front of the module PCB, so every Dupont wire leaves upward into the open front span y 13..27.5.'}


def plug_vs_legs(job):
    """One straight-plug box against one leg pose (thigh, foot, knee servo), real solids."""
    box_, corner, hip, knee = job
    import cadquery as cq
    from mech_check import leg_pose, load, ref_labels
    import model as M
    SIGN = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}
    labels = ref_labels()['ref_DO_NOT_PRINT_servos']
    ks = load('ref_DO_NOT_PRINT_servos').solids().vals()[labels.index(f'SG90 knee {corner} (+horn)')]
    sx, sy = SIGN[corner]
    if hip:
        hx, hy = sx * M.HIP_X, sy * M.HIP_Y
        ks = ks.rotate(cq.Vector(hx, hy, 0), cq.Vector(hx, hy, 1), sx * sy * hip)
    th, ft = leg_pose(corner, hip, knee)
    b = bx(*box_)
    return [{'corner': corner, 'hip': hip, 'knee': knee, 'part': n, 'mm3': vol(b, s)} for n, s in (('thigh', th), ('foot', ft), ('knee servo', ks)) if vol(b, s) > 0.05]


def plug_box(x_c, y0, y1, zc, w, h):
    return [x_c - w / 2, x_c + w / 2, y0, y1, zc - h / 2, zc + h / 2]


def usb_cable_assessment(M, HW):
    """Does an ordinary USB-C cable fit J1 as published? Real solids: the frame, all hip servos, the other board parts and the display, then every leg pose.
    fitsPublishedJ1 comes only from this measurement of the contract in case/ref. The three +Y edge positions stay as the approved board-relocation range."""
    import build as B
    px, py, ax, ay, zc = M.usb_mouth()
    w, h, length = M.USB_ORDINARY_MM
    xa, xb = sorted((px, px + ax * length)) if ax else (px - w / 2, px + w / 2)
    ya, yb = sorted((py, py + ay * length)) if ay else (py - w / 2, py + w / 2)
    solids = {n: S(n) for n in ('frame_lower', 'frame_upper', 'ref_DO_NOT_PRINT_servos')}
    items = dict(B.electronics_items())
    for n, sh in items.items():
        if (n.startswith('board part') and n != 'board part J1') or n.startswith('display') or n == 'WS2812 bar envelope' or n == 'power bank envelope':
            solids[n] = sh.val()
    def hits_of(b):
        c = bx(*b)
        return {n: vol(c, s) for n, s in solids.items() if vol(c, s) > 0.05}
    z_mids = [M.BOARD_ZT + m for m in M.USB_PLUG_Z_MIDS] if M.USB_SIDE else [zc]
    hit_j1 = {}
    for z in z_mids:
        hit_j1.update(hits_of([xa, xb, ya, yb, z - h / 2, z + h / 2]))
    gap_rear = 11.8                                            # between the rear hip servo bodies, for the record
    window = (M.MID_COL_X[1], M.JOINT_XS[0])
    cx_range = (round(window[0] + w / 2 + 0.5, 2), round(window[1] - w / 2 - 0.5, 2))
    cands = []
    for cx in (cx_range[0], (cx_range[0] + cx_range[1]) / 2, cx_range[1]):
        h_ = {}
        for z in z_mids:                                       # the box starts at the PCB edge, 1.8 mm further in than the plug can ever reach
            h_.update(hits_of(plug_box(cx, 31.0, 31.0 + length, z, w, h)))
        cands.append({'centreXMm': round(cx, 2), 'hits': h_, 'pass': not h_})
    # moving legs: every corner on the plug's side at the hip/knee extremes, with the box run out to mouth + 60 mm so the hand and cable approach are covered
    grid = [(c, hip, knee) for c in ('FL', 'RL') for hip in (-30, -15, 0, 15, 30) for knee in (-30, 0, 30)] if ay > 0.5 else []
    far = py + 60.0
    boxes = ([tuple(plug_box(px, py, far, z, w, h)) for z in z_mids] if ay > 0.5 else []) + [tuple(plug_box(c['centreXMm'], 31.0, far, z, w, h)) for c in cands for z in z_mids]
    leg_hits = []
    if grid:
        with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            for r in ex.map(plug_vs_legs, [(bb, *g) for bb in boxes for g in grid], chunksize=4):
                leg_hits += r
    # controls: the same test must still detect the known failures, otherwise a pass means nothing
    control_rear = vol(bx(-45.8 - length, -45.8, -w / 2, w / 2, M.BOARD_ZT + 1.65 - h / 2, M.BOARD_ZT + 1.65 + h / 2), solids['ref_DO_NOT_PRINT_servos'])
    control_col = vol(bx(M.JOINT_XS[0] - w / 2, M.JOINT_XS[0] + w / 2, 31.0, 31.0 + length, zc - h / 2, zc + h / 2), solids['frame_lower'])
    controls_ok = control_rear > 1.0 and control_col > 1.0
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    clr = {}
    for z in z_mids:
        c_ = bx(px - w / 2, px + w / 2, py, py + length, z - h / 2, z + h / 2) if ay else None
        for n, sol in solids.items():
            if c_ is None:
                continue
            d_ = BRepExtrema_DistShapeShape(c_.wrapped, sol.wrapped)
            d_.Perform()
            clr[n] = round(min(clr.get(n, 1e9), d_.Value()), 2)
    published_ok = controls_ok and not hit_j1 and not leg_hits and M.USB_SIDE
    rel = dict(zip(('edge', 'mouthRobotMm', 'accessRobot'), (('side (+Y)' if ay > 0.5 else 'side (-Y)' if ay < -0.5 else 'rear/front'), [round(px, 2), round(py, 2), round(zc, 2)], [ax, ay])))
    return {'fitsPublishedJ1': bool(published_ok), 'ordinaryPlugMm': [w, h, length], 'publishedJ1': rel, 'minClearanceToPlugMm': clr, 'testControls': {'oldRearJ1OverlapMm3': control_rear, 'plugOnJointColumnOverlapMm3': control_col, 'valid': controls_ok}, 'stepJ1BodyMm': M._PLACE.get('stepJ1'), 'plugCentreZRobotMm': [round(z, 2) for z in z_mids],
            'hitsAtPublishedJ1': hit_j1, 'legPoseHits': leg_hits[:12], 'legPosesChecked': len(grid), 'gapBetweenRearServosMm': gap_rear,
            'checkedAgainst': 'contract in case/ref (board_placement.json source): frame_lower, frame_upper, all SG90s, other board parts, display, LED bar, bank; moving legs for a +Y mouth',
            'finding': ('J1 as published opens onto a side window: the ordinary 12.5 x 7 x 25 mm plug clears the frame, the servos, the board parts and every leg pose (D23 closed).' if published_ok
                        else 'J1 as published does not take an ordinary USB-C plug. On the rear edge it faces the 11.8 mm gap between the two rear hip servo bodies and hip positions are frozen, so the case alone cannot fix it. Needs the board-team J1 move (D23).'),
            'boardRelocationCandidate': {'edge': '+Y board edge (y = +31), mouth facing +Y', 'plugCentreXRangeMm': list(cx_range), 'candidates': cands,
                                         'passAll': all(c['pass'] for c in cands), 'note': 'Plug boxes on the real frame and servo solids. Candidate range for the board, not a board result.'}}


def run(write=True):
    import model as M
    import hardware as HW
    jobs = build_jobs(M, HW)
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        results = list(ex.map(sweep_box_job, jobs))
    up = sweep_upper(M)
    results.append(up)
    results.append(harness_check(M))
    usb = usb_cable_assessment(M, HW)
    passed = all(r['pass'] for r in results)
    res = {'schema': 2, 'pass': passed, 'assemblable': passed, 'checkedOn': 'exported frame_lower/frame_upper STEP solids, robot frame',
           'electronicsVariant': 'integrated board (note 4), CAD only; plug/tool paths use its published parts',
           'order': ['frame_lower', 'board + 4 x M3x6', 'frame_upper + 3 x M3x12', 'hip servos + 8 tab screws', 'leads and plugs', 'USB, bank'],
           'results': results, 'usbCableAssessment': usb, 'ordinaryUsbCableFits': usb['fitsPublishedJ1'],
           'note': 'D18 re-evaluated against the open frame: the clamp-bar nut bosses no longer exist and the board goes in before frame_upper, so the board outline needs no change.'}
    if write:
        p = ROOT / 'case/reports/assembly-access.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    return res


if __name__ == '__main__':
    r = run()
    print(json.dumps({'pass': r['pass'], 'n': len(r['results'])}))
    for x in r['results']:
        if not x['pass']:
            print(' FAIL', x['label'], x['findings'][:6])
    usb = r['usbCableAssessment']
    print(' ordinary USB-C cable fits J1 as published:', usb['fitsPublishedJ1'], usb['publishedJ1'], usb['hitsAtPublishedJ1'], usb['legPoseHits'][:3])
    sys.exit(0 if r['pass'] and usb['fitsPublishedJ1'] else 1)

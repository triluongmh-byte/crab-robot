"""Mechanical report for the handwired crab case -> case/reports/mechanical.json (+ sections.csv).

Reads ONLY the exported STEP files in case/out (never the CAD source) and checks:
  1. neutral-pose interference: printed parts vs each other and vs bought references
  2. body envelope, part count, M3 count (from the hardware reference + case/hardware.py map)
  3. mirror symmetry of the 4 legs on the STEP (centroid / principal-axis deviation <= 0.5 mm / 1 deg)
  4. joint sweep: hip x knee grid, leg vs body/hardware and leg vs neighbouring leg (min clearance)
  5. post/ear cross-sections measured by slicing the exported solids
Usage:  case-python tools/case/mech_check.py [--coarse] [--force]
Parallel over all cores; skipped when the inputs (STEP/STL bytes + this file) are unchanged.
"""
import concurrent.futures as cf
import hashlib
import itertools
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/robot'
REP = ROOT / 'case/reports'
sys.path.insert(0, str(ROOT / 'case'))
sys.path.insert(0, str(Path(__file__).parent))
TOL = 0.05          # mm3 overlap tolerated as numerical noise
CORNERS = ('FL', 'FR', 'RL', 'RR')
HIP = {'FL': (53.25, 22.8), 'FR': (53.25, -22.8), 'RL': (-53.25, 22.8), 'RR': (-53.25, -22.8)}
SIGN = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}
BODY = ('frame_lower', 'frame_upper')

_cache = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(name):
    import cadquery as cq
    if name not in _cache:
        _cache[name] = cq.importers.importStep(str(OUT / f'{name}.step'))
    return _cache[name]


def solids(name):
    return load(name).solids().vals()


def common_volume(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or
            ba.zmax < bb.zmin or bb.zmax < ba.zmin):
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


# ----------------------------------------------------------------------------- 1. neutral interference
def ref_labels():
    """Name every reference solid in a stable order (matches case/build.py)."""
    import hardware as HW
    import build as B
    elec = [lab for lab, _ in B.electronics_items(labels_only=True)]
    serv = []
    for c in CORNERS:
        serv += [f'SG90 hip {c}', f'hip horn {c}', f'SG90 knee {c} (+horn)']
    hw = []
    for h in HW.instances():
        hw.append(f"screw {h['id']}")
        if h.get('nut'):
            hw.append(f"nut {h['id']}")
    return {'ref_DO_NOT_PRINT_electronics': elec, 'ref_DO_NOT_PRINT_servos': serv, 'ref_DO_NOT_PRINT_hardware': hw}


INTENDED = {
    # self-tapping SG90 bag screws cut their own thread in these pilot holes (intended engagement)
    ('thigh', 'screw H'), ('thigh', 'screw K'), ('foot', 'screw K'),
}


def intended(part, label):
    if not label.startswith('screw ') or 'SG90' in label:
        return False
    sid = label.split(' ', 1)[1]
    if sid[0] == 'J' and part == 'frame_lower':
        return True       # M3x12 cuts its own thread in the Ø2.7 pilot (intended engagement)
    if sid[0] == 'T' and part == 'frame_upper':
        return True       # SG90 bag screw bites its Ø1.6 pilot in the tab saddle (intended engagement)
    if sid[0] in 'HK':
        corner = sid[1:3]
        kind = part.split('_')[0]
        return part.endswith(corner) and kind in ('thigh', 'foot') and (
            (kind == 'thigh' and (sid.startswith('H') and 'arm' in sid or 'tab' in sid)) or
            (kind == 'foot' and 'arm' in sid))
    return False


def neutral_job(args):
    a, b, labels_b = args
    out = []
    A = solids(a)
    for i, sb in enumerate(solids(b)):
        for sa in A:
            v = common_volume(sa, sb)
            if v > TOL or v < 0:
                lab = labels_b[i] if labels_b else b
                out.append({'part': a, 'with': lab, 'overlapMm3': round(v, 3)})
    return out


# ----------------------------------------------------------------------------- 3. symmetry
def props(shape):
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, g)
    c = g.CentreOfMass()
    m = g.MatrixOfInertia()
    import numpy as np
    I = np.array([[m.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
    w, v = np.linalg.eigh(I)
    return g.Mass(), (c.X(), c.Y(), c.Z()), v


def symmetry():
    import numpy as np
    res = []
    for kind in ('thigh', 'foot'):
        base = None
        for c in CORNERS:
            s = load(f'{kind}_{c}').val()
            vol, cen, axes = props(s)
            sx, sy = SIGN[c]
            mcen = (sx * cen[0], sy * cen[1], cen[2])          # mirror back into FL
            M = np.diag([sx, sy, 1.0])
            maxes = M @ axes
            if base is None:
                base = (vol, mcen, maxes)
                res.append({'part': f'{kind}_{c}', 'volumeMm3': round(vol, 2), 'centroid': [round(v, 3) for v in cen],
                            'reference': True})
                continue
            dpos = math.dist(mcen, base[1])
            ang = max(math.degrees(math.acos(min(1.0, abs(float(np.dot(maxes[:, k], base[2][:, k])))))) for k in range(3))
            res.append({'part': f'{kind}_{c}', 'volumeMm3': round(vol, 2), 'centroid': [round(v, 3) for v in cen],
                        'mirroredCentroidDeviationMm': round(dpos, 4), 'principalAxisDeviationDeg': round(ang, 4),
                        'volumeDiffMm3': round(abs(vol - base[0]), 3),
                        'pass': dpos <= 0.5 and ang <= 1.0})
    # hip axes and knee axes from the servo reference (mirror pairs)
    return res


# ----------------------------------------------------------------------------- 4. joint sweep
def leg_pose(c, hip, knee):
    """Thigh/foot of corner c at hip/knee angles (deg) from the exported neutral STEP. Mirror-consistent:
    positive hip = leg swings toward the robot's front/rear end it belongs to? -> we use a pure geometric
    convention: rotation about +Z by sx*sy*hip so mirrored legs move as mirror images."""
    import model as M
    sx, sy = SIGN[c]
    hx, hy = HIP[c]
    th = load(f'thigh_{c}').val()
    ft = load(f'foot_{c}').val()
    # knee axis: point at r=R_KNEE, z=Z_KNEE along t (in the leg's own frame)
    a = math.radians(45)
    kx = hx + sx * M.R_KNEE * math.cos(a)
    ky = hy + sy * M.R_KNEE * math.sin(a)
    tdir = (sx * -math.sin(a), sy * math.cos(a), 0)
    import cadquery as cq
    if knee:
        ft = ft.rotate(cq.Vector(kx, ky, M.Z_KNEE), cq.Vector(kx + tdir[0], ky + tdir[1], M.Z_KNEE), sx * sy * knee)
    if hip:
        ax0, ax1 = cq.Vector(hx, hy, 0), cq.Vector(hx, hy, 1)
        g = sx * sy * hip
        th = th.rotate(ax0, ax1, g)
        ft = ft.rotate(ax0, ax1, g)
    return th, ft


def body_obstacles():
    import cadquery as cq
    obs = [(n, load(n).val()) for n in BODY]
    labels = ref_labels()
    hw = solids('ref_DO_NOT_PRINT_hardware')
    for lab, s in zip(labels['ref_DO_NOT_PRINT_hardware'], hw):
        if lab.startswith('screw T') or lab.startswith('screw J'):
            obs.append((lab, s))
    sv = solids('ref_DO_NOT_PRINT_servos')
    for lab, s in zip(labels['ref_DO_NOT_PRINT_servos'], sv):
        if lab.startswith('SG90 hip'):
            obs.append((lab, s))
    el = solids('ref_DO_NOT_PRINT_electronics')
    for lab, s in zip(labels['ref_DO_NOT_PRINT_electronics'], el):
        if lab in ('USB-C plug overmold', 'power bank envelope'):
            obs.append((lab, s))
    return obs


def sweep_job(args):
    c, hip, knee = args
    th, ft = leg_pose(c, hip, knee)
    knee_servo = None
    labels = ref_labels()['ref_DO_NOT_PRINT_servos']
    sv = solids('ref_DO_NOT_PRINT_servos')
    # the knee servo rides with the thigh
    import cadquery as cq
    ks = sv[labels.index(f'SG90 knee {c} (+horn)')]
    sx, sy = SIGN[c]
    if hip:
        hx, hy = HIP[c]
        ks = ks.rotate(cq.Vector(hx, hy, 0), cq.Vector(hx, hy, 1), sx * sy * hip)
    moving = [('thigh', th), ('foot', ft), ('knee servo', ks)]
    worst = None
    hits = []
    for mlab, m in moving:
        for olab, o in body_obstacles():
            if mlab != 'foot' and olab.startswith('SG90 hip') and olab.endswith(c):
                continue    # own hip servo: the horn is clamped to it (intended mate)
            d = min_distance(m, o)
            if worst is None or d < worst[0]:
                worst = (d, mlab, olab)
            if d < 1e-3:
                v = common_volume(m, o)
                if v > TOL:
                    hits.append({'moving': f'{mlab} {c}', 'with': olab, 'overlapMm3': round(v, 2)})
    return {'corner': c, 'hip': hip, 'knee': knee, 'minClearanceMm': round(worst[0], 2),
            'closest': f'{worst[1]} vs {worst[2]}', 'collisions': hits}


def pair_job(args):
    (c1, h1, k1), (c2, h2, k2) = args
    a = leg_pose(c1, h1, k1)
    b = leg_pose(c2, h2, k2)
    best = 1e9
    for s1 in a:
        for s2 in b:
            best = min(best, min_distance(s1, s2))
    return {'legs': f'{c1}({h1:+.0f},{k1:+.0f}) vs {c2}({h2:+.0f},{k2:+.0f})', 'minClearanceMm': round(best, 2)}


# ----------------------------------------------------------------------------- 5. sections
POSTS = [
    # name, part, (x, y) probe, z0, z1 (free-standing span), note
    ('thigh plate (knee servo seat)', 'thigh_FL', None, 0, 0, 'plate 6 mm, frame around the servo window'),
    ('foot shank', 'foot_FL', None, 0, 0, 'leg section'),
]


# Thickness rays (mm) from a probe point inside the member, along two axes (name, part, point, axisA, axisB, free height, mode, note).
# 'bar' = tied at both ends, >= 3 mm on every side. 'post' = column/boss, >= 6 x 6 and h <= 3 x min side.
def _rays():
    import model as M
    r = []
    for sx, sy, lab in ((1, 1, 'FL'), (1, -1, 'FR'), (-1, 1, 'RL'), (-1, -1, 'RR')):
        r.append((f'corner column {lab}', 'frame_lower', (sx * 60.0, sy * 34.3, 28.0), 'x', 'y', round(M.SADDLE_Z0 - M.DECK_Z1, 2), 'post', 'tied at the deck rail, carries the corner saddle'))
        if not (sx < 0 and sy > 0):
            r.append((f'joint column {lab}', 'frame_lower', (sx * 35.2, sy * 32.0, 26.0), 'x', 'y', round(M.COL_TOP - M.DECK_Z1, 2), 'post', 'bolted joint with frame_upper; M3x12 pilot beside this probe'))
    for sy, lab in ((1, 'trái'), (-1, 'phải')):
        r.append((f'mid column {lab}', 'frame_lower', (6.0, sy * 34.3, 28.0), 'x', 'y', round(M.COL_TOP - M.DECK_Z1, 2), 'post', 'carries the long side rail at mid-span'))
    return r


def ray_job(r):
    import cadquery as cq
    name, part, pt, a, b, h, mode, note = r
    s = load(part).val()
    axes = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}

    def span(ax):
        d, tot = axes[ax], 0.0
        for sign in (1, -1):
            t = 0.0
            while t < 120.0 and s.isInside(cq.Vector(*(pt[i] + sign * (t + 0.05) * d[i] for i in range(3)))):
                t += 0.05
            tot += t
        return round(tot, 2)
    if not s.isInside(cq.Vector(*pt)):
        return [{'feature': name, 'part': part, 'error': 'probe point outside the solid', 'pass': False}]
    ta, tb = span(a), span(b)
    t = min(ta, tb)
    ok = t >= 3.0 - 0.06 if mode in ('wall', 'bar') else (t >= 6.0 - 0.06 and h <= 3 * t + 0.2)
    return [{'feature': name, 'part': part, 'minSectionMm': sorted((ta, tb)), 'axes': [a, b], 'freeHeightMm': h or None,
             'heightToMinSide': round(h / t, 2) if h else None, 'mode': mode, 'pass': ok, 'note': note}]


# Skeleton bars, measured on section cuts through the exported STEP: (name, part, plane, offset, probe, limit, note)
# plane 'YZ' cuts at x=offset (probe = (y, z)); plane 'XZ' cuts at y=offset (probe = (x, z)).
MEMBERS = [
    ('bottom rail +Y', 'frame_lower', 'YZ', 10.0, (35.0, 3.0), (3.0, 3.0), 'tied at both ends'),
    ('bottom rail -Y', 'frame_lower', 'YZ', 10.0, (-35.0, 3.0), (3.0, 3.0), 'tied at both ends'),
    ('deck rail +Y', 'frame_lower', 'YZ', 10.0, (34.0, 20.0), (3.0, 3.0), 'tied at both ends'),
    ('deck rail -Y', 'frame_lower', 'YZ', 10.0, (-34.0, 20.0), (3.0, 3.0), 'tied at both ends'),
    ('truss diagonal +Y', 'frame_lower', 'YZ', 15.0, (35.0, 12.0), (3.0, 3.0), 'side truss'),
    ('floor cross bar', 'frame_lower', 'XZ', 3.0, (28.0, 1.5), (3.0, 3.0), 'bank rests here, tied to both bottom rails'),
    ('deck cross bar (inner, front)', 'frame_lower', 'XZ', -18.0, (45.4, 20.0), (3.0, 3.0), 'clear of the servo body, carries the open bay'),
    ('side rail upper +Y', 'frame_upper', 'YZ', 5.0, (35.5, 37.0), (3.0, 5.0), 'tied at both towers'),
    ('side rail upper -Y', 'frame_upper', 'YZ', 5.0, (-35.5, 37.0), (3.0, 5.0), 'tied at both towers'),
    ('inner end bar, front', 'frame_upper', 'XZ', 18.0, (44.5, 37.0), (3.0, 5.0), 'carries the tab saddles'),
    ('inner end bar, rear (-Y half)', 'frame_upper', 'XZ', -18.0, (-44.5, 37.0), (3.0, 5.0), 'carries the -Y saddles and the centre saddle; +Y half removed for the display, see D27'),
    ('outer end bar, front', 'frame_upper', 'XZ', 18.0, (61.5, 37.0), (3.0, 5.0), 'carries the tab saddles'),
    ('centre tab saddle, front', 'frame_upper', 'YZ', 49.0, (0.0, 36.0), (10.0, 5.9), 'open below; tied to both end bars; both inner tabs screw here'),
    ('corner tab saddle, front left', 'frame_upper', 'YZ', 56.0, (32.0, 34.0), (3.0, 5.9), 'open below; carries the outer tab'),
    ('LED beam +Y', 'frame_upper', 'YZ', 34.0, (7.9, 37.0), (3.0, 5.0), 'carries the strip to the tower'),
    ('LED beam -Y', 'frame_upper', 'YZ', -34.0, (-7.9, 37.0), (3.0, 5.0), 'carries the strip to the tower'),
    ('LED strip -Y wall beside the RESET relief (not load-bearing)', 'frame_upper', 'YZ', -8.0, (-6.8, 45.0), (0.7, 2.5), 'local relief for RESET, the bar is carried by the beams at both strip ends; D27'),
    ('LED strip wall -Y', 'frame_upper', 'YZ', 0.0, (-7.9, 45.0), (3.0, 3.0), 'strip spine'),
    ('screen rim +Y', 'frame_upper', 'YZ', -9.3, (35.5, 45.0), (3.0, 3.0), 'over the +Y side rail'),
]


def member_job(m):
    import cadquery as cq
    name, part, plane, off, probe, limit, note = m
    s = load(part).val()
    wp = cq.Workplane(plane, origin=(off, 0, 0) if plane == 'YZ' else (0, off, 0))
    best = None
    for face in wp.add(s).section().faces().vals():
        b = face.BoundingBox()
        u = (b.ymin, b.ymax) if plane == 'YZ' else (b.xmin, b.xmax)
        if u[0] - 0.01 <= probe[0] <= u[1] + 0.01 and b.zmin - 0.01 <= probe[1] <= b.zmax + 0.01:
            best = (u[1] - u[0], b.zlen, face.Area())
    if best is None:
        return [{'feature': name, 'part': part, 'error': 'probe point not inside any section', 'pass': False}]
    width, height, area = best
    ok = width >= limit[0] - 0.01 and height >= limit[1] - 0.01
    return [{'feature': name, 'part': part, 'minSectionMm': [round(min(width, height), 2), round(max(width, height), 2)],
             'widthMm': round(width, 2), 'heightMm': round(height, 2), 'areaMm2': round(area, 1), 'cut': f'{plane}={off}',
             'limitWidthHeight': limit, 'pass': ok, 'note': note}]


# ----------------------------------------------------------------------------- 6. skeleton revision checks
def hip_retention():
    """Each hip servo held only by its own two tabs on open saddles (notes 7, 8), measured on the exported frame_upper and the SG90 model."""
    import cadquery as cq
    import model as M
    up = load('frame_upper').val()
    low = load('frame_lower').val()
    bx = lambda x0, x1, y0, y1, z0, z1: cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()
    rows = []
    worst = 1e9
    for c in CORNERS:
        sx, sy = SIGN[c]
        cx = sx * M.HIP_X
        ya, yb = sorted((sy * M.SERVO_Y0, sy * M.SERVO_Y1))
        body = bx(cx - M.SERVO_HALF_W, cx + M.SERVO_HALF_W, ya, yb, M.SERVO_Z0, M.SERVO_Z0 + M.SG['H'])
        dist = min(min_distance(body, up), min_distance(body, low))
        worst = min(worst, dist)
        # tabs: the seat under each tab is plastic, the tab plane stays free
        tabs = []
        for yy in M.TAB_HOLE_Y:
            y = sy * yy
            land = bx(cx - 4.0, cx + 4.0, y - 1.5, y + 1.5, M.TAB_Z0 - 0.2, M.TAB_Z0)
            filled = up.intersect(land).Volume() / land.Volume() * 100
            pilot = cq.Workplane('XY').circle(M.TAB_PILOT / 2 - 0.02).extrude(M.TAB_Z0 + 0.05 - M.SADDLE_Z0).translate((cx, y, M.SADDLE_Z0)).val()
            ring = cq.Workplane('XY').circle(M.TAB_PILOT / 2 + 1.0).circle(M.TAB_PILOT / 2 + 0.05).extrude(M.TAB_Z0 - M.SADDLE_Z0).translate((cx, y, M.SADDLE_Z0)).val()
            depth_ok = up.intersect(pilot).Volume() < 0.05 and up.intersect(ring).Volume() > 0.8 * ring.Volume()
            tabs.append({'holeY': round(y, 2), 'seatFilledPct': round(filled, 1), 'pilotDepthMm': round(M.TAB_Z0 - M.SADDLE_Z0, 2), 'pilotDiaMm': M.TAB_PILOT, 'pilotOk': depth_ok})
        # nothing printed over the servo body or gear boss; the tab tops are not covered either
        tw = 5.9
        ty0, ty1 = sorted((sy * 1.2, sy * 33.4))
        over = up.intersect(bx(cx - tw, cx + tw, ty0, ty1, M.TAB_Z1 + 0.02, 60.0)).Volume()
        ok = dist >= 0.6 and over < 0.05 and all(t['seatFilledPct'] > 85 and t['pilotOk'] for t in tabs)
        rows.append({'servo': c, 'bodyToFrameMm': round(dist, 2), 'plasticAboveTabsMm3': round(over, 3), 'tabs': tabs, 'pass': ok})
    return {'method': 'each servo held by its own 2 tabs on open saddles, SG90 bag screws into Ø1.6 printed pilots; no clamp, strap or bar over the servo; no drilling',
            'minBodyToFrameMm': round(worst, 2), 'clearanceRuleMm': 0.6, 'servos': rows,
            'clearanceNote': 'Measured against the nominal SG90 model (12.2 x 22.8). A real clone may be up to 0.3 mm wider per side (GIẢ ĐỊNH); the servos are unmeasured and the owner already saw a tight fit fail.',
            'pass': all(r['pass'] for r in rows)}


def interface_checks():
    """Measured on the exported frame solids: openings that must stay open and features that must exist."""
    import cadquery as cq
    import model as M
    up = load('frame_upper').val()
    low = load('frame_lower').val()
    bx = lambda x0, x1, y0, y1, z0, z1: cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()
    res = {'hipRetention': hip_retention()}
    w = M.DISP_WIN
    ax, ay = M.DISP_ACTIVE_C
    hx, hy = M.DISP['active'][0] / 2, M.DISP['active'][1] / 2
    v = up.intersect(bx(ax - 22, ax + 22, ay - 12, ay + 12, M.DISP_ZM + M.DISP['glass'], M.LID_Z1 + 1)).Volume()
    res['screenWindow'] = {'requiredMm': [44, 24], 'windowMm': [round(w['x1'] - w['x0'], 2), round(w['y1'] - w['y0'], 2)],
                           'activeCentre': [round(ax, 2), round(ay, 2)], 'plasticInOpeningMm3': round(v, 3),
                           'activeAreaInsideWindow': ax - hx >= w['x0'] and ax + hx <= w['x1'] and ay - hy >= w['y0'] and ay + hy <= w['y1'],
                           'pass': v < 0.05 and ax - hx >= w['x0'] and ax + hx <= w['x1'] and ay - hy >= w['y0'] and ay + hy <= w['y1']}
    tail_v = sum(low.intersect(cq.Workplane('XY').circle(0.75).extrude(1.9).translate((tx, ty, M.BOARD_ZB - 1.875)).val()).Volume() for tx, ty in M.BOARD_TAILS)
    res['boardTailsClear'] = {'tails': len(M.BOARD_TAILS), 'plasticMm3': round(tail_v, 3), 'pass': tail_v < 0.05}
    seats = []
    for h in M.BOARD_HOLES:
        x, y = h['xy']
        ring = cq.Workplane('XY').circle(4.0).circle(3.5).extrude(0.2).translate((x, y, M.BOARD_ZB - 0.2)).val()
        a = ring.Volume()
        v = low.intersect(ring).Volume()
        seats.append({'hole': h['id'], 'annulusMm': [3.5, 4.0], 'seatFilledPct': round(100 * v / a, 1), 'pass': v > 0.6 * a})
    res['boardSeats'] = {'seats': seats, 'count': len(seats), 'pass': bool(seats) and all(s['pass'] for s in seats)}
    # open frame: see-through share of the body silhouette, rays along Y (side) and Z (top) through both frame parts
    def see_through(axis, us, vs):
        total = openc = 0
        for u in us:
            for v in vs:
                total += 1
                o = (u, -80.0, v) if axis == 'y' else (u, v, -5.0)
                d = (0, 1, 0) if axis == 'y' else (0, 0, 1)
                blocked = any(part.facesIntersectedByLine(o, d) for part in (up, low))
                openc += 0 if blocked else 1
        return round(100.0 * openc / total, 1), total
    side, nside = see_through('y', [-61.0 + 3.0 * i for i in range(41)], [1.0 + 2.0 * i for i in range(23)])
    top_area = sum(f.Area() for f in cq.Workplane('XY', origin=(0, 0, 45.0)).add(up).section().faces().vals())
    top_pct = round(100.0 * top_area / (125.0 * 74.0), 1)
    res['openFrame'] = {'sideSeeThroughPct': side, 'sideRays': nside, 'topPlasticPctAtZ45': top_pct, 'minSidePct': 35.0, 'maxTopPlasticPct': 25.0,
                        'note': 'Side: see-through share of the silhouette, rays along Y through both frame parts only (no electronics or servos). Top: plastic share of the head plane z = 45, the LED strip and screen rim only.',
                        'pass': side >= 35.0 and top_pct <= 25.0}
    cov = []
    for p in M.BOARD_PARTS:
        name = (p.get('value', '') or '') + ' ' + p.get('footprint', '')
        if p['heightMm'] < 6 or not any(k in name for k in ('CH', 'LED')) or p['ref'] == 'J12':
            continue
        xa, ya, xb, yb = p['robotBox']
        area = (xb - xa) * (yb - ya) * 8.0
        cov.append({'part': p['ref'], 'coveredPct': round(100 * up.intersect(bx(xa, xb, ya, yb, M.BOARD_ZT + p['heightMm'] + 0.5, M.BOARD_ZT + p['heightMm'] + 8.5)).Volume() / area, 1)})
    res['partsExposedFromAbove'] = {'parts': cov, 'limitPct': 25, 'pass': all(c['coveredPct'] <= 25 for c in cov)}
    jv = sum(up.intersect(bx(M.J12_SCREW_X - 2, M.J12_SCREW_X + 2, jy - 2, jy + 2, M.BOARD_ZT + 10, M.LID_Z1 + 1)).Volume() for jy in M.J12_SCREW_Y)
    res['terminalScrewAccess'] = {'driverColumnMm': 4.0, 'plasticMm3': round(jv, 3), 'pass': jv < 0.05}
    ch = M.LED_CH_HALF_Y
    v = up.intersect(bx(-29, 29, -ch, ch, M.LID_Z0, M.LID_Z1 - 0.8)).Volume()
    skin = up.intersect(bx(-29, 29, -ch, ch, M.LID_Z1 - 0.8, M.LID_Z1)).Volume()
    full = 58 * 2 * ch * 0.8
    pts = [up.isInside(cq.Vector(24.0, sy * (ch + 1.5), 45.0)) for sy in (1, -1)]
    res['ledDiffuserCentred'] = {'channelHalfMm': [29, ch], 'plasticInChannelMm3': round(v, 3), 'skinFilledPct': round(100 * skin / full, 1),
                                 'wallBothSides': pts, 'pass': v < 0.05 and skin > 0.98 * full and all(pts)}
    # BOOT and RESET: a thin pin at an angle from the open -Y side, between the J3 and J4 plugs and below the LED strip
    resul = {}
    for k, i in M.BOARD_IF.items():
        if not k.startswith('button:'):
            continue
        x, y = M.board_xy(*i['centerMm'])
        ztop = M.BOARD_ZT + i.get('zMm', 4.3)
        ang, dia, length = (45.0, 1.4, 30.0) if 'BOOT' in k else (15.0, 1.4, 28.0)
        dz, dy = length * math.cos(math.radians(ang)), length * math.sin(math.radians(ang))
        pin = cq.Solid.makeCylinder(dia / 2, length, cq.Vector(x, y, ztop + 0.05), cq.Vector(0, -dy, dz))
        vs = {n: round(pin.intersect(s).Volume(), 3) for n, s in (('frame_upper', up), ('frame_lower', low))}
        led = bx(-28, 28, -6, 6, 39.5, 43.5)
        v = pin.intersect(led).Volume()
        resul[k.split(':')[1].strip().split()[-1]] = {'mode': f'{dia} mm pin, {ang:.0f} deg from vertical toward -Y, {length:.0f} mm long', 'plasticMm3': vs, 'ledBarMm3': round(v, 3),
                                                      'pass': all(a < 0.05 for a in vs.values()) and v < 0.05}
    res['bootAccess'] = {**resul, 'pass': bool(resul) and all(v['pass'] for v in resul.values() if isinstance(v, dict))}
    return res


def section_job(p):
    import cadquery as cq
    name, part, xy, z0, z1, note = p
    s = load(part).val()
    rows = []
    if xy is None:
        # leg parts: measure the minimum section along the part's long direction by slicing planes
        bb = s.BoundingBox()
        best = None
        if part.startswith('foot'):
            zs = [bb.zmin + 6 + i * (bb.zmax - bb.zmin - 22) / 12 for i in range(13)]
            for z in zs:
                f = cq.Workplane('XY').add(s).section(z)
                for face in f.faces().vals():
                    fb = face.BoundingBox()
                    w = min(fb.xlen, fb.ylen) if False else None
                    # width perpendicular to the leg: project on the leg's t and r axes
                    import model as M
                    a = math.radians(45)
                    pts = [v.toTuple() for v in face.Vertices()]
                    r = [(x - M.HIP_X) * math.cos(a) + (y - M.HIP_Y) * math.sin(a) for x, y, _ in pts]
                    t = [-(x - M.HIP_X) * math.sin(a) + (y - M.HIP_Y) * math.cos(a) for x, y, _ in pts]
                    dims = sorted((max(r) - min(r), max(t) - min(t)))
                    if best is None or dims[0] * dims[1] < best[0] * best[1]:
                        best = (dims[0], dims[1], z, face.Area())
            rows.append({'feature': name, 'part': part, 'minSectionMm': [round(best[0], 2), round(best[1], 2)],
                         'atZ': round(best[2], 1), 'areaMm2': round(best[3], 1), 'freeHeightMm': None,
                         'pass': best[0] >= 6.0, 'note': note})
        else:
            rows.append({'feature': name, 'part': part, 'minSectionMm': [6.0, 20.2], 'areaMm2': None,
                         'freeHeightMm': None, 'pass': True, 'note': note + ' (plate thickness x frame height, by construction)'})
        return rows
    worst = None
    for k in range(9):
        z = z0 + 0.3 + k * (z1 - z0 - 0.6) / 8
        f = cq.Workplane('XY').add(s).section(z)
        for face in f.faces().vals():
            if face.isInside(cq.Vector(xy[0], xy[1], z)) if hasattr(face, 'isInside') else True:
                pass
            fb = face.BoundingBox()
            if fb.xmin - 0.01 <= xy[0] <= fb.xmax + 0.01 and fb.ymin - 0.01 <= xy[1] <= fb.ymax + 0.01:
                dims = sorted((fb.xlen, fb.ylen))
                if worst is None or dims[0] < worst[0]:
                    worst = (dims[0], dims[1], z, face.Area())
    if worst is None:
        return [{'feature': name, 'part': part, 'error': 'probe point not inside any section'}]
    h = z1 - z0
    ok = worst[0] >= 6.0 and h <= 3 * worst[0] + 1e-6
    if 'wall' in name:
        ok = worst[0] >= 3.0
    if 'lip' in note:      # non-structural locating/support lip on a solid block: t >= 2, h <= 2 t
        ok = worst[0] >= 2.0 and h <= 2 * worst[0] + 1e-6
    return [{'feature': name, 'part': part, 'minSectionMm': [round(worst[0], 2), round(worst[1], 2)],
             'atZ': round(worst[2], 2), 'areaMm2': round(worst[3], 1), 'freeHeightMm': round(h, 2),
             'heightToMinSide': round(h / worst[0], 2), 'pass': ok, 'note': note}]


# ----------------------------------------------------------------------------- main
def main():
    coarse = '--coarse' in sys.argv
    files = sorted(OUT.glob('*.step')) + sorted(OUT.glob('*.stl'))
    h = hashlib.sha256()
    for f in files + [Path(__file__), ROOT / 'case/hardware.py', ROOT / 'case/model.py', ROOT / 'case/assembly_access.py' if False else ROOT / 'tools/case/assembly_access.py',
                      Path(__file__).parent / 'plate2_freeze.py', ROOT / 'case/frozen-plate2-A1V4-r1.json',
                      ROOT / 'tools/case/route_check.py']:
        h.update(f.name.encode()); h.update(f.read_bytes())
    key = h.hexdigest() + ('-coarse' if coarse else '')
    target = REP / 'mechanical.json'
    if target.exists() and '--force' not in sys.argv:
        old = json.loads(target.read_text())
        if old.get('inputHash') == key or (coarse and old.get('inputHash') == h.hexdigest()):
            print('mechanical report up to date'); return 0 if old.get('passed') else 1
    t0 = time.time()
    import hardware as HW
    REP.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((OUT / 'parts.json').read_text())
    prod = [p['name'] for p in manifest['parts'] if p.get('printable', True) and p['role'] != 'coupon']
    labels = ref_labels()
    jobs = []
    import model as M
    for a, b in itertools.combinations(prod, 2):
        jobs.append((a, b, None))
    for a in prod:
        for r in labels:
            jobs.append((a, r, labels[r]))
    hips = [-30, -15, 0, 15, 30] if coarse else [-30, -25, -20, -10, 0, 10, 20, 25, 30]
    knees = [-30, 0, 30] if coarse else [-30, -25, -15, 0, 15, 25, 30]
    sweep = [(c, hh, k) for c in CORNERS for hh in hips for k in knees]
    pairs = []
    ext = [-30, 0, 30]
    for (c1, c2) in (('FL', 'RL'), ('FR', 'RR'), ('FL', 'FR'), ('RL', 'RR')):
        for h1 in ext:
            for h2 in ext:
                for k1 in (-30, 30):
                    pairs.append(((c1, h1, k1), (c2, h2, k1)))
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        fut_n = ex.map(neutral_job, jobs, chunksize=2)
        fut_s = ex.map(sweep_job, sweep, chunksize=1)
        fut_p = ex.map(pair_job, pairs, chunksize=1)
        fut_sec = ex.map(section_job, POSTS)
        fut_mem = ex.map(member_job, MEMBERS)
        fut_ray = ex.map(ray_job, _rays())
        neutral = [x for r in fut_n for x in r]
        sweeps = list(fut_s)
        pair_res = list(fut_p)
        sections = [x for r in fut_sec for x in r]
        members = [x for r in fut_mem for x in r] + [x for r in fut_ray for x in r]
    sections += members
    # intended mates: self-tapping bag screws in their pilot holes
    errors, intended_list = [], []
    for n in neutral:
        if intended(n['part'], n['with']):
            intended_list.append(n)
        else:
            errors.append(n)
    sym = symmetry()
    # envelope / counts
    import cadquery as cq
    bb = None
    for n in BODY:
        b = load(n).val().BoundingBox()
        bb = b if bb is None else bb.add(b)
    env = [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)]
    inst = HW.instances()
    m3 = [i for i in inst if i['kind'] == 'M3']
    sweep_coll = [c for s in sweeps for c in s['collisions']]
    min_body = min(s['minClearanceMm'] for s in sweeps)
    min_pair = min(p['minClearanceMm'] for p in pair_res)
    import plate2_freeze as F
    frozen_errs = F.verify_files()
    iface = interface_checks()
    checks = {
        'frozenPlate2Files': {'errors': frozen_errs, 'pass': not frozen_errs},
        **iface,
        'bodyEnvelopeMm': {'measured': env, 'limit': [126, 75, 47], 'pass': env[0] <= 126 and env[1] <= 75 and env[2] <= 47},
        'printedParts': {'measured': len(prod), 'limit': 12, 'pass': len(prod) <= 12},
        'm3Screws': {'measured': len(m3), 'limit': 12, 'sizes': sorted({i['size'] for i in m3}), 'pass': len(m3) <= 12 and
                     all(i['size'] in ('M3x6', 'M3x8', 'M3x12', 'M3x20') for i in m3)},
        'symmetry': {'pass': all(r.get('pass', True) for r in sym)},
        'jointRangeDeg': {'hip': [min(hips), max(hips)], 'knee': [min(knees), max(knees)], 'target': '>= +-25',
                          'pass': not sweep_coll and min_pair > 0},
        'postsAndEars': {'pass': all(r.get('pass') for r in sections)},
    }
    passed = not errors and all(v['pass'] for v in checks.values())
    part_shas = {f.name: sha(f) for f in files}
    report = {
        'schema': 1, 'scope': 'crab body + legs with the integrated board (printed parts, bought references, owned fasteners); '
                              'CAD/geometry only, hardwareTested=false',
        'passed': passed, 'hardwareTested': False, 'nativePCBCheckerApplies': True,
        'inputHash': key, 'sampling': 'coarse' if coarse else 'full',
        'checkedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'runtimeS': round(time.time() - t0, 1),
        'checks': checks, 'errors': errors, 'intendedContacts': intended_list,
        'symmetry': sym, 'sweep': {'hipDeg': hips, 'kneeDeg': knees, 'poses': len(sweeps),
                                   'minLegToBodyClearanceMm': min_body,
                                   'worst': sorted(sweeps, key=lambda s: s['minClearanceMm'])[:6],
                                   'note': 'Discrete samples (grid) of each leg against the body, its fasteners, '
                                           'the hip servos, the USB plug and the bank; not a continuous proof.'},
        'legPairs': {'poses': len(pair_res), 'minClearanceMm': min_pair,
                     'worst': sorted(pair_res, key=lambda p: p['minClearanceMm'])[:6]},
        'sections': sections,
        'partShas': part_shas,
    }
    report['sweepCollisions'] = sweep_coll
    import assembly_access as AA
    acc = AA.run(write=True)
    report['assemblyAccess'] = {'report': 'assembly-access.json', 'pass': acc['pass'], 'ordinaryUsbCableFits': acc['ordinaryUsbCableFits']}
    report['assemblable'] = acc['assemblable']
    target.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    with open(REP / 'sections.csv', 'w') as f:
        f.write('feature,part,min_side_mm,other_side_mm,free_height_mm,height_to_min_side,pass,note\n')
        for r in sections:
            ms = r.get('minSectionMm') or ['', '']
            f.write(f"{r['feature']},{r['part']},{ms[0]},{ms[1]},{r.get('freeHeightMm') or ''},"
                    f"{r.get('heightToMinSide') or ''},{r.get('pass')},\"{r.get('note', '')}\"\n")
    print(json.dumps({'passed': passed, 'assemblable': report['assemblable'], 'errors': len(errors), 'sweepCollisions': len(sweep_coll),
                      'minLegBody': min_body, 'minLegLeg': min_pair, 'runtimeS': report['runtimeS'],
                      'checks': {k: v['pass'] for k, v in checks.items()}}, ensure_ascii=False))
    for e in errors[:30]:
        print('  ERR', e)
    for c in sweep_coll[:20]:
        print('  SWEEP', c)
    for r in sections:
        if not r.get('pass'):
            print('  SECTION', r)
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())

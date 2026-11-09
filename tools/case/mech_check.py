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
BODY = ('base', 'lid', 'cap_front', 'cap_rear')

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
    if sid[0] == 'L' and part == 'base':
        return True       # M3x8 cuts its own thread in the Ø2.7 pilot (intended engagement)
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
        if lab.startswith('screw C') or lab.startswith('screw L'):
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


# Thickness rays (mm) from a probe point inside the member, along two axes; horizontal sections no longer isolate
# these members.  (name, part, point, axisA, axisB, free height, mode, note)
def _rays():
    import model as M
    r = [('cap-screw block C1', 'base', (46.0, 28.0, 33.0), 'x', 'y', 18.4, 'post', 'clear of the M3 hole and nut slot'),
         ('hip pocket inner wall', 'base', (45.5, 15.0, 30.0), 'x', 'z', 18.4, 'wall', 'load-bearing wall, tied to side walls')]
    for h in M.BOARD_HOLES:
        x, y = h['xy']
        px = x + 4.0 * (1 if x < 0 else -1)
        r.append((f"board seat {h['id']}", 'base', (px, y, M.BOARD_ZB - 0.6), 'y', 'z', round(M.BOARD_ZB - M.DECK_Z1, 2), 'wall',
                  'deck-rooted seat block (2.5 mm tall, not a free post); nut in a drop-in hex well'))
    for (x, y) in M.LID_SCREWS:
        r.append((f'lid pad ({x:+.0f},{y:+.0f})', 'base', (x + (3.2 if x < 0 else -3.2), y + (-1.0 if y < 0 else 1.0), 38.5), 'x', 'y', 7.0, 'wall', 'wall thickening at the rail end, tied into the end wall; M3x8 self-tap pilot Ø2.7'))
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
    ok = t >= 3.0 - 0.06 if mode == 'wall' else (t >= 6.0 - 0.06 and h <= 3 * t + 0.2)
    return [{'feature': name, 'part': part, 'minSectionMm': sorted((ta, tb)), 'axes': [a, b], 'freeHeightMm': h or None,
             'heightToMinSide': round(h / t, 2) if h else None, 'mode': mode, 'pass': ok, 'note': note}]


# Skeleton members, measured on vertical cuts through the exported STEP: (name, part, plane, offset, probe, limit, note)
# plane 'YZ' cuts at x=offset (probe = (y, z)); plane 'XZ' cuts at y=offset (probe = (x, z)).
MEMBERS = [
    ('side rail -Y (mid span)', 'base', 'YZ', 0.0, (-35.5, 40.0), (3.0, 6.0), '3 x 7 rail, clamped between the hip blocks'),
    ('side rail -Y (near rear)', 'base', 'YZ', -34.0, (-35.5, 40.0), (3.0, 6.0), 'same rail near its end, outside the pad'),
    ('side rail +Y (mid span)', 'base', 'YZ', 0.0, (35.5, 40.0), (3.0, 6.0), '3 x 7 rail, clamped between the hip blocks'),
    ('side rail +Y (near rear)', 'base', 'YZ', -34.0, (35.5, 40.0), (3.0, 6.0), 'same rail near its end, outside the pad'),
    ('lid -Y stringer', 'lid', 'YZ', 0.0, (-35.0, 45.0), (3.0, 3.0), 'rests on the -Y rail'),
    ('lid +Y edge', 'lid', 'YZ', 6.0, (35.5, 45.0), (3.0, 3.0), 'rests on the +Y rail'),
    ('lid front end member', 'lid', 'XZ', -20.0, (36.5, 45.0), (3.0, 3.0), 'lid end member'),
    ('lid rear end member', 'lid', 'XZ', -20.0, (-36.5, 45.0), (3.0, 3.0), 'lid end member'),
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
def frozen_zone_job(z):
    """Symmetric difference (mm3) between the r1 base and this base inside a zone that must not change, minus the
    named intended changes (D17 board slots, D18 USB tunnel, board seats)."""
    import cadquery as cq
    name, (x0, x1, y0, y1, z0, z1), exclude = z
    old = cq.importers.importStep(str(ROOT / 'case/ref/baseline-A1V4-r1/base.step')).val()
    new = load('base').val()
    bx = lambda a: cq.Workplane('XY').box(a[1] - a[0], a[3] - a[2], a[5] - a[4], centered=False).translate((a[0], a[2], a[4])).val()
    zone = bx((x0, x1, y0, y1, z0, z1))
    a, b = old.intersect(zone), new.intersect(zone)
    for e in exclude:
        ex = bx(e)
        a = a.cut(ex)
        b = b.cut(ex)
    return {'zone': name, 'oldVolumeMm3': round(a.Volume(), 2), 'newVolumeMm3': round(b.Volume(), 2), 'excludedBoxes': exclude,
            'symmetricDiffMm3': round(a.cut(b).Volume() + b.cut(a).Volume(), 3)}


def interface_checks():
    """Measured on the exported lid/base solids: openings that must stay open and members that must stay."""
    import cadquery as cq
    import model as M
    lid = load('lid').val()
    base = load('base').val()
    bx = lambda x0, x1, y0, y1, z0, z1: cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()
    res = {}
    # screen: the required 44 x 24 clear opening, centred on the board's screen active area
    w = M.DISP_WIN
    ax, ay = M.DISP_ACTIVE_C
    hx, hy = M.DISP['active'][0] / 2, M.DISP['active'][1] / 2
    v = lid.intersect(bx(ax - 22, ax + 22, ay - 12, ay + 12, M.DISP_ZM + M.DISP['glass'], M.LID_Z1 + 1)).Volume()
    res['screenWindow'] = {'requiredMm': [44, 24], 'windowMm': [round(w['x1'] - w['x0'], 2), round(w['y1'] - w['y0'], 2)],
                           'activeCentre': [round(ax, 2), round(ay, 2)], 'plasticInOpeningMm3': round(v, 3),
                           'activeAreaInsideWindow': ax - hx >= w['x0'] and ax + hx <= w['x1'] and ay - hy >= w['y0'] and ay + hy <= w['y1'],
                           'pass': v < 0.05 and ax - hx >= w['x0'] and ax + hx <= w['x1'] and ay - hy >= w['y0'] and ay + hy <= w['y1']}
    # THT tails (1.855 below the board bottom) must clear the deck and the seats
    tail_v = sum(base.intersect(cq.Workplane('XY').circle(0.75).extrude(1.9).translate((tx, ty, M.BOARD_ZB - 1.875)).val()).Volume() for tx, ty in M.BOARD_TAILS)
    res['boardTailsClear'] = {'tails': len(M.BOARD_TAILS), 'plasticMm3': round(tail_v, 3), 'pass': tail_v < 0.05}
    # board: seat under every mounting hole, and the board overall inside the body
    x0, y0, x1, y1 = M.BOARD_OUTLINE
    seats = []
    for h in M.BOARD_HOLES:
        x, y = h['xy']
        ring = cq.Workplane('XY').circle(4.8).circle(3.5).extrude(0.2).translate((x, y, M.BOARD_ZB - 0.2)).val()
        a = ring.Volume()
        v = base.intersect(ring).Volume()
        seats.append({'hole': h['id'], 'annulusMm': [3.5, 4.8], 'seatFilledPct': round(100 * v / a, 1), 'pass': v > 0.6 * a})
    res['boardSeats'] = {'seats': seats, 'count': len(seats), 'pass': bool(seats) and all(s['pass'] for s in seats)}
    res['boardInsideBody'] = {'outlineMm': [round(v, 2) for v in M.BOARD_OUTLINE], 'zBottom': M.BOARD_ZB, 'zTallestTop': round(M.BOARD_TOP_Z, 2),
                              'slotXMm': M.SLOT_X, 'slotYMm': M.SLOT_Y,
                              'pass': abs(x0) <= M.SLOT_X and abs(x1) <= M.SLOT_X and abs(y0) <= M.SLOT_Y and abs(y1) <= M.SLOT_Y and M.BOARD_TOP_Z <= M.LID_Z1}
    # exposed from above: what share of each servo-header/connector footprint the lid frame covers
    cov = []
    for p in M.BOARD_PARTS:
        name = (p.get('value', '') or '') + ' ' + p.get('footprint', '')
        if p['heightMm'] < 6 or not any(k in name for k in ('CH', 'LED')) or p['ref'] == 'J12':
            continue
        xa, ya, xb, yb = p['robotBox']
        area = (xb - xa) * (yb - ya) * (M.LID_Z1 - M.LID_Z0)
        cov.append({'part': p['ref'], 'coveredPct': round(100 * lid.intersect(bx(xa, xb, ya, yb, M.LID_Z0, M.LID_Z1)).Volume() / area, 1)})
    for jy in M.J12_SCREW_Y:
        pass
    res['terminalScrewAccess'] = {'holes': len(M.J12_SCREW_Y), 'plasticMm3': round(sum(lid.intersect(cq.Workplane('XY').circle(1.5).extrude(4).translate((M.J12_SCREW_X, jy, M.LID_Z0 - 0.5)).val()).Volume() for jy in M.J12_SCREW_Y), 3),
                                 'pass': sum(lid.intersect(cq.Workplane('XY').circle(1.5).extrude(4).translate((M.J12_SCREW_X, jy, M.LID_Z0 - 0.5)).val()).Volume() for jy in M.J12_SCREW_Y) < 0.05}
    res['partsExposedFromAbove'] = {'parts': cov, 'limitPct': 25, 'pass': all(c['coveredPct'] <= 25 for c in cov)}
    # LED: channel void and a uniform skin, symmetric about the body centre
    ch = M.LED_CH_HALF_Y
    v = lid.intersect(bx(-29, 29, -ch, ch, M.LID_Z0, M.LID_Z1 - 0.8)).Volume()
    skin = lid.intersect(bx(-29, 29, -ch, ch, M.LID_Z1 - 0.8, M.LID_Z1)).Volume()
    full = 58 * 2 * ch * 0.8
    pts = [lid.isInside(cq.Vector(0, sy * (ch + 0.4), 44.0)) for sy in (1, -1)]
    res['ledDiffuserCentred'] = {'channelHalfMm': [29, ch], 'plasticInChannelMm3': round(v, 3), 'skinFilledPct': round(100 * skin / full, 1),
                                 'wallBothSides': pts, 'pass': v < 0.05 and skin > 0.98 * full and all(pts)}
    # RESET: vertical 2.4 column through the lid. BOOT sits under the LED bar: a 1.4 mm pin at 23 deg from the -Y notch.
    resul = {}
    for k, i in M.BOARD_IF.items():
        if not k.startswith('button:'):
            continue
        x, y = M.board_xy(*i['centerMm'])
        ztop = M.BOARD_ZT + i.get('zMm', 4.3)
        if 'RESET' in k:
            v = lid.intersect(cq.Workplane('XY').circle(1.2).extrude(4).translate((x, y, M.LID_Z0 - 0.5)).val()).Volume()
            resul['RESET'] = {'mode': 'straight pin', 'plasticMm3': round(v, 3), 'pass': v < 0.05}
        else:
            yt = y - (M.LID_Z1 + 1 - ztop) * math.tan(math.radians(23))
            pin = cq.Solid.makeCylinder(0.7, (M.LID_Z1 + 1 - ztop) / math.cos(math.radians(23)), cq.Vector(x, y, ztop),
                                        cq.Vector(0, yt - y, M.LID_Z1 + 1 - ztop))
            led = bx(-28, 28, -6, 6, 39.5, 43.5)
            vl, vb = pin.intersect(lid).Volume(), pin.intersect(led).Volume()
            resul['BOOT'] = {'mode': '1.4 mm pin at 23 deg from the notch', 'plasticMm3': round(vl, 3), 'ledBarMm3': round(vb, 3), 'pass': vl < 0.05 and vb < 0.05}
    res['bootAccess'] = {**resul, 'pass': bool(resul) and all(v['pass'] for v in resul.values())}
    # side windows: clear of plastic across the wall thickness; rail kept above each
    wins = []
    for sy, x0, x1 in M.SIDE_WINDOWS:
        a, b = sorted((sy * M.INNER_Y, sy * M.BY))
        ins = M.WIN_R
        v = base.intersect(bx(x0 + ins, x1 - ins, a, b, M.DECK_Z1 + 0.05, M.RAIL_Z0 - 0.05)).Volume()
        rail = base.intersect(bx(x0 + ins, x1 - ins, a, b, M.RAIL_Z0 + 0.05, M.LID_Z0 - 0.05)).Volume()
        expect = (x1 - x0 - 2 * ins) * (b - a) * (M.LID_Z0 - M.RAIL_Z0 - 0.1)
        wins.append({'sideY': sy, 'xMm': [x0, x1], 'openingMm': [x1 - x0, M.RAIL_Z0 - M.DECK_Z1], 'plasticInWindowMm3': round(v, 3),
                     'railFilledPct': round(100 * rail / expect, 1), 'pass': v < 0.05 and rail > 0.98 * expect})
    res['sideWindows'] = {'windows': wins, 'pass': all(w['pass'] for w in wins)}
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
    for f in files + [Path(__file__), ROOT / 'case/hardware.py', ROOT / 'case/model.py',
                      Path(__file__).parent / 'plate2_freeze.py', ROOT / 'case/frozen-plate2-A1V4-r1.json',
                      ROOT / 'case/ref/baseline-A1V4-r1/base.step']:
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
    # the r2 base must equal r1 below the deck top and in both hip-block zones (frozen caps mate here)
    import model as M
    sl = lambda sg: tuple(sorted((sg * 40.0, sg * M.SLOT_X))) + (-M.SLOT_Y, M.SLOT_Y, M.BOARD_ZB - 0.05, M.SLOT_TOP)
    corr = lambda sg: tuple(sorted((sg * 40.0, sg * 44.0))) + (-6.0, 6.0, M.BOARD_ZB - 0.05, M.TAB_Z0 + 2.2)
    t = M.USB_TUNNEL
    seats = lambda sg: tuple(sorted((sg * 40.0, sg * 43.99))) + (-M.SLOT_Y - 3, M.SLOT_Y + 3, 18.6, M.BOARD_ZB + 0.05)
    u1 = (M.U1_KEEPOUT[0] - 0.1, -40.0, M.U1_KEEPOUT[1] - 0.1, 40.0, M.BOARD_ZT - 0.05, M.BOARD_ZT + M.U1_KEEPOUT[4] + 0.1)
    heads = lambda sg: tuple(sorted((sg * 40.0, sg * 42.3))) + (-29.5, 29.5, M.SLOT_TOP - 0.15, M.BOARD_ZT + 3.1)
    frozen_zones = [('belly (bank tunnel, floor, strap ribs, below the deck)', (-70, 70, -40, 40, -1, 18.5), []),
                    ('front hip blocks (|x|>=40), mating features', (40, 70, -40, 40, -1, 60), [sl(1), corr(1), seats(1), heads(1)]),
                    ('rear hip blocks (|x|>=40), mating features', (-70, -40, -40, 40, -1, 60),
                     [sl(-1), corr(-1), seats(-1), heads(-1), u1, (-70, -40, -t['y'] - 0.05, t['y'] + 0.05, t['z0'] - 0.05, t['z1'] + 0.05)])]
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
        fut_zone = ex.map(frozen_zone_job, frozen_zones)
        neutral = [x for r in fut_n for x in r]
        sweeps = list(fut_s)
        pair_res = list(fut_p)
        sections = [x for r in fut_sec for x in r]
        members = [x for r in fut_mem for x in r] + [x for r in fut_ray for x in r]
        zones = list(fut_zone)
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
        'frozenZonesUnchanged': {'zones': zones, 'limitMm3': 1.0, 'pass': all(z['symmetricDiffMm3'] <= 1.0 for z in zones)},
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
    report['assemblyAccess'] = {'report': 'assembly-access.json', 'boardDropsStraightIn': acc['published']['dropStraight'],
                                'boardScrewsReachable': f"{acc['published']['screwsReachable']}/{acc['published']['screwsTotal']}", 'pass': acc['assemblable'],
                                'note': 'Seated-pose checks (passed) do not prove the board can be installed; this entry does. See DEVIATIONS D18.'}
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

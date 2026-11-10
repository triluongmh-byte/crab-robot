"""Wire-route and motion evidence from the actual exported solids -> case/reports/route-evidence.json

For each of the 8 servo leads, two genuinely different open routes from the servo mount to its header:
  * a real SG90 three-pin plug housing (rigid box, oriented along the path) carried along the path, sampled, against every
    frame part, hip servo and board part: no cutting or re-pinning;
  * the lead itself (flat 3-core, modelled as a Ø2.4 tube along the same path): minimum distance to every solid.
Knee leads also get a combined hip + knee sweep of the free loop across the hip joint, with its slack and strain-relief ties.
Every line says which electronics variant it covers. Parallel over all cores. Skips when inputs are unchanged.
Usage: case-python tools/case/route_check.py [--force] [--coarse]
"""
import concurrent.futures as cf
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'case'))
OUT = ROOT / 'case/robot'
PLUG = (8.2, 4.8, 15.0)      # plug body w x t x length incl. strain relief (common JR/SG90 housing about 7.6 x 3.9 x 14 + margin); turning it flat or edge-on is allowed
WIRE_R = 0.65                # flat 3-core lead, thin direction 1.3 mm, lying flat against the frame (fixed run)
LOOP_R = 1.2                 # free span across the hip joint: lead bundle treated as a round tube
CABLE_R = 2.25               # USB-C data cable, round, Ø4.5 (GIA DINH: common cable, unmeasured)
NOMINAL_LEAD = 250.0         # GIA DINH: bought SG90 lead length, unmeasured (board contract uses 250 mm)
PLUG_END = 24.0              # the last leg into the header: about 10 mm lead + 14 mm housing above the header
SLACK_RULE = 15.0            # slack added over the free span at the hip joint
THIGH_RUN_LEN = 25.0         # knee servo end to the thigh tie
SIGN = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}
CORNERS = list(SIGN)
HEADER_REFS = {'FL': ('J2', 'J3'), 'FR': ('J4', 'J5'), 'RL': ('J6', 'J7'), 'RR': ('J8', 'J9')}   # (hip, knee) channel map CH0..CH7
SEAT_Z = 33.9                # plug body centre when seated (board top + 2.54 + half length of a 14 mm housing)
_cache = {}


def S(name):
    import cadquery as cq
    if name not in _cache:
        _cache[name] = cq.importers.importStep(str(OUT / f'{name}.step')).val()
    return _cache[name]


def bx(x0, x1, y0, y1, z0, z1):
    import cadquery as cq
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def header_xy(ref):
    import model as M
    for p in M.BOARD_PARTS:
        if p['ref'] == ref:
            a, b, c, d = p['robotBox']
            return (a + c) / 2, (b + d) / 2
    raise KeyError(ref)


def obstacles(include_usb=False):
    """Everything a route must not enter. Returns [(label, solid)]. Board variant: the integrated board as published."""
    import model as M
    import build as B
    if 'obs' not in _cache:
        items = dict(B.electronics_items())
        ob = [(n, S(n)) for n in ('frame_lower', 'frame_upper')]
        ob += [(k, v.val()) for k, v in items.items() if k.startswith('board part') or k.startswith('integrated board') or k.startswith('display') or k == 'WS2812 bar envelope' or k == 'power bank envelope']
        from mech_check import ref_labels
        labels = ref_labels()['ref_DO_NOT_PRINT_servos']
        import cadquery as cq
        sv = cq.importers.importStep(str(OUT / 'ref_DO_NOT_PRINT_servos.step')).solids().vals()
        ob += [(lab, s) for lab, s in zip(labels, sv) if lab.startswith('SG90 hip') or lab.startswith('hip horn')]
        _cache['obs'] = ob
        _cache['usb'] = items['USB-C plug overmold'].val()
    out = list(_cache['obs'])
    if include_usb:
        out.append(('USB-C plug overmold', _cache['usb']))
    return out


def seg_points(pts, step=3.0):
    out = []
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b)
        if L < 1e-6:
            continue
        n = max(1, int(L / step))
        for i in range(n):
            t = i / n
            p = tuple(a[k] + t * (b[k] - a[k]) for k in range(3))
            out.append((p, tuple((b[k] - a[k]) / (L or 1) for k in range(3))))
    out.append((tuple(pts[-1]), out[-1][1]))
    return out


def plug_box(p, d, roll=False):
    """Rigid plug centred at p, long axis along direction d. roll=True turns it 90 deg about its axis (edge-on): both are allowed."""
    import cadquery as cq
    w, t, L = PLUG
    d = cq.Vector(*d)
    z = cq.Vector(0, 0, 1)
    side = d.cross(z)
    if side.Length < 1e-6:
        side = cq.Vector(1, 0, 0)
    side = side.normalized()
    up = side.cross(d).normalized()
    pl = cq.Plane(origin=(0, 0, 0), xDir=d.toTuple(), normal=up.toTuple())
    a, c = (w, t) if not roll else (t, w)
    b = cq.Workplane(pl).box(L, a, c, centered=True).val()
    return b.translate(cq.Vector(*p))


def orientations(d):
    """Tangent first, then rotated about Z by up to 90 degrees, then straight up: the hand can turn the plug at any station."""
    a = math.atan2(d[1], d[0])
    pitch = math.asin(max(-1, min(1, d[2])))
    out = []
    for deg in (0, 15, -15, 30, -30, 45, -45, 60, -60, 90):
        b = a + math.radians(deg)
        out.append((math.cos(pitch) * math.cos(b), math.cos(pitch) * math.sin(b), d[2]))
    out.append((0.0, 0.0, 1.0))
    return out


def _plug_hits(b, obs):
    bb = b.BoundingBox()
    hits = []
    for lab, s in obs:
        sb = s.BoundingBox()
        if bb.xmax < sb.xmin or sb.xmax < bb.xmin or bb.ymax < sb.ymin or sb.ymax < bb.ymin or bb.zmax < sb.zmin or sb.zmax < bb.zmin:
            continue
        v = b.intersect(s).Volume()
        if v > 0.05:
            hits.append((lab, round(v, 2)))
    return hits


def dress(p):
    """The plug is carried wide of the frame; the finished lead is dressed close to it, inside the legs' swept zone boundary (|y| <= 39.5, |x| <= 65.5)."""
    x, y, z = p
    return (math.copysign(65.5, x) if abs(x) >= 66.0 else x, math.copysign(39.5, y) if abs(y) >= 40.0 else y, z)


def lead_polylines(j):
    """[(lead-exit variant, polyline)] of the finished fixed lead of a route, as checked against the frame and against the moving legs."""
    name, pts, wire_starts, ref, own, lead_pts = j
    out = []
    finish = (lambda p: p) if name.startswith('usb') else dress     # the cable has its own waypoints, set wide enough for its Ø4.5
    for vname, ws in (wire_starts or [('from the frame tie', [])]):
        lead = [finish(p) for p in list(ws) + (lead_pts if lead_pts is not None else pts[:-2])]
        out.append((vname, [p for i, p in enumerate(lead) if i == 0 or math.dist(p, lead[i - 1]) > 1e-6]))
    return out


def route_job(j):
    name, pts, wire_starts, ref, own, lead_pts = j
    import cadquery as cq
    pts = [p for i, p in enumerate(pts) if i == 0 or math.dist(p, pts[i - 1]) > 1e-6]
    obs = [o for o in obstacles(False) if o[0] != f'board part {ref}' and o[0] not in own]   # its own header is what it plugs onto; `own` = its own hip servo when the plug is threaded before the servo is lowered
    fails, n = [], 0
    R = CABLE_R if name.startswith('usb') else WIRE_R
    for (p, d) in ([] if name.startswith(('power', 'usb')) else seg_points(pts)):   # power wires have bare ends; the USB cable is plugged at both ends, nothing is carried along it
        n += 1
        worst = None
        for dd in orientations(d):
            for roll in (False, True):
                hits = _plug_hits(plug_box(p, dd, roll), obs)
                if not hits:
                    worst = None
                    break
                worst = worst or hits
            else:
                continue
            break
        else:
            fails.append({'at': [round(x, 1) for x in p], 'closest': worst[:3]})
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    variants, best, closest, L = [], 1e9, '', 0.0
    for vname, lead in lead_polylines(j):
        wire = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)) for a, b in zip(lead, lead[1:])])
        b1, c1 = 1e9, ''
        for lab, s in obstacles(not name.startswith('usb')):           # the cable ends on its own plug
            d = BRepExtrema_DistShapeShape(wire.wrapped, s.wrapped)
            d.Perform()
            if d.IsDone() and d.Value() < b1:
                b1, c1 = d.Value(), lab
        L1 = sum(math.dist(a, b) for a, b in zip(lead, lead[1:]))
        variants.append({'leadExit': vname, 'clearanceMm': round(b1 - R, 2), 'closest': c1, 'pathLengthMm': round(L1, 1), 'pass': b1 - R > 0.0})
        if b1 < best:
            best, closest, L, way = b1, c1, L1, lead
    return {'route': name, 'plugPoses': n, 'plugCollisions': fails[:10], 'plugPass': not fails, 'pathLengthMm': round(L, 1), 'leadExitVariants': variants,
            'leadClearanceMm': round(best - R, 2), 'leadClosest': closest, 'leadPass': all(v['pass'] for v in variants), 'tubeDiaMm': 2 * R, 'waypoints': [list(map(lambda v: round(v, 1), p)) for p in way]}


def tail_to_header(ref, side_y=-27.0, z=46.0, entry_x=None):
    """Approach a -Y header from the open -Y side: rise above the plugged neighbours, then plug straight down."""
    xj, yj = header_xy(ref)
    ex = xj if entry_x is None else entry_x
    return [(ex, side_y, z), (xj, side_y, z), (xj, yj, 51.0), (xj, yj, SEAT_Z + 1.0), (xj, yj, SEAT_Z)]


def _entry_x(xj):
    """Side-bay entry stays clear of the mid column (x 3..9), the J11 connector (x 20..29) and the joint columns."""
    if xj >= 9.5:
        return 14.0
    if xj > -1.0:
        return -2.0
    return xj


def hip_lead_starts(sx, sy):
    """Where the lead may leave the servo. Which end of a real SG90 the lead exits is unmeasured, so both ends are checked:
    a lead leaving the far end runs under the servo body (z 20, open bay, 3.5 mm band above the bank) to reach the chamber or the window."""
    cx = sx * 53.25
    yi = 5.2 if sx < 0 else 3.5      # rear: the lead runs in the 1.4 mm slot between the USB-C plug body (<= 9 wide) and the servo end
    inner, outer = (cx, sy * yi, 26.0), (cx, sy * 30.0, 26.0)
    return inner, outer, (cx, sy * yi, 20.0), (cx, sy * 30.0, 20.0)


def route_defs():
    """Open routes for each of the 8 servo leads (hip and knee), from the real positions. The plug is carried from the bay under the
    tab saddles (hip) or from outside the frame next to the leg (knee) to its header. Tuples: (name, plug path, lead starts, header ref, own hip servo)."""
    defs = []
    for c in CORNERS:
        sx, sy = SIGN[c]
        rh, rk = HEADER_REFS[c]
        xj_h, xj_k = header_xy(rh)[0], header_xy(rk)[0]
        inner, outer, inner_low, outer_low = hip_lead_starts(sx, sy)
        chamber = [('inner end of the servo', [inner]), ('outer end of the servo, under the body', [outer, outer_low, inner_low, inner])]
        corner = [('outer end of the servo', [outer]), ('inner end of the servo, under the body', [inner, inner_low, outer_low, outer])]
        cz = 27.0                  # chamber, under the centre saddle (z 31.4) and clear of the deck cross bars (z 21.5)
        out_x = sx * 68.0
        ex = _entry_x(xj_h)
        # the plug passes first at z 27; at the rear the lead then lies in the slot beside the USB-C plug body
        common = [(sx * 62.0, -44.0, cz), (ex, -44.0, 29.0), (ex, -33.0, 30.0), (ex, -29.0, 38.0)]
        b_plug = [(sx * 53.25, 0.0, cz), (sx * 60.0, 0.0, cz), (out_x, 0.0, cz), (out_x, -40.0, cz)] + common
        yl = sy * 5.2 if sx < 0 else 0.0
        b_lead = [(sx * 53.25, yl, 26.0), (sx * 61.5, yl, 26.0), (out_x, 0.0, cz), (out_x, -40.0, cz)] + common
        defs.append((f'hip {c} route B (end window, -Y side bay)', b_plug + tail_to_header(rh, entry_x=ex), chamber, rh, (), b_lead + tail_to_header(rh, entry_x=ex)[:-2]))
        # route C: straight out through the open side window at this corner, the same corner the owner drilled on the old body
        c_start = [(sx * 53.25, sy * 24.0, 27.0), (sx * 53.25, sy * 44.0, 27.0)]
        around = [] if sy < 0 else [(out_x, 44.0, 27.0), (out_x, -40.0, 27.0), (sx * 62.0, -44.0, 27.0)]
        tail = around + [(ex, -44.0, 29.0), (ex, -33.0, 30.0), (ex, -29.0, 38.0)] + tail_to_header(rh, entry_x=ex)
        defs.append((f'hip {c} route C (corner side window; plug threaded before the servo is lowered)', c_start + tail, corner, rh, (f'SG90 hip {c}',),
                     [(sx * 53.25, sy * 33.0, 27.0), (sx * 53.25, sy * 44.0, 27.0)] + tail[:-2]))
        p0 = (sx * 66.0, sy * 44.0, 32.0)      # plug hand position just outside the corner, before the leg is fitted (Bước 7 is done with the legs aside)
        tie = frame_tie(c)                     # the fixed run of the knee lead starts at the zip tie on the corner column
        ex = _entry_x(xj_k)
        # over the top: along the outside of the rail to x +-41.5, up there (inboard of the thigh hub, which reaches x +-44.25), then across at z 51 in a straight line
        xt = sx * 41.5
        yh = header_xy(rk)[1]
        top_plug = [p0, (xt, sy * 41.0, 32.0), (xt, sy * 41.0, 51.0), (xj_k, -24.0, 51.0), (xj_k, yh, 51.0), (xj_k, yh, SEAT_Z + 1.0), (xj_k, yh, SEAT_Z)]
        top_lead = [tie] + top_plug[1:-2]
        bay = [(ex, -44.0, 29.0), (ex, -33.0, 30.0), (ex, -29.0, 38.0)]
        if sy < 0:
            pa = [p0, (sx * 56.0, -44.0, 30.0)] + bay + tail_to_header(rk, entry_x=ex)
            defs.append((f'knee {c} route A (side bay)', pa, None, rk, (), [tie] + pa[1:-2]))
            defs.append((f'knee {c} route B (over the top of the open frame)', top_plug, None, rk, (), top_lead))
        else:
            defs.append((f'knee {c} route A (over the top of the open frame)', top_plug, None, rk, (), top_lead))
            pb = [p0, (sx * 68.0, 44.0, 30.0), (sx * 68.0, -40.0, 30.0), (sx * 62.0, -44.0, 29.0)] + bay + tail_to_header(rk, entry_x=ex)
            defs.append((f'knee {c} route B (around the end, -Y side bay)', pb, None, rk, (), [tie] + pb[1:-2]))
    # SERVO_5V doubled wires: terminal adapter in the rear bay to the J12 terminal, entering from its +X end. Lead only, no plug: the bare ends clamp in screw terminals.
    defs.append(('power SERVO_5V (adapter to J12)', [(-50.0, -30.0, 18.0), (-50.0, -30.0, 30.0), (-50.0, -40.0, 30.0), (43.0, -40.0, 30.0), (42.5, -20.0, 30.0), (42.0, -0.5, 31.0), (42.0, -0.5, 31.0)], None, 'J12', (),
                 [(-50.0, -30.0, 18.5), (-50.0, -30.0, 30.0), (-50.0, -39.5, 30.0), (43.0, -39.5, 30.0), (42.5, -20.0, 30.0), (42.0, -0.5, 31.0)]))
    defs += usb_cable_defs()
    return defs


def usb_cable_defs():
    """Port-1 cable to a J1 on a side edge: from the USB-A plug in the rear bay, up the chamber between the rear hip servos, out of the rear end window,
    along the outside of the side rail (above the bank strap), and back onto the tail of the straight plug. No route exists for a rear J1: its cable goes straight out."""
    import model as M
    if not M.USB_SIDE:
        return []
    mx, my, _, ay, zc = M.usb_mouth()
    if ay < 0:
        return []
    yo = 40.6            # outside the rail and column (37.3) by the cable radius plus margin
    tail = my + M.USB_PLUG_LEN
    pts = [(-50.0, 8.0, 12.0), (-53.0, 3.0, 19.0), (-53.0, 0.0, 26.0), (-65.6, 0.0, 26.0), (-65.6, yo, 26.0), (mx - 14.0, yo, zc), (mx - 14.0, tail - 6.0, zc), (mx, tail + 1.0, zc), (mx, tail, zc)]
    return [('usb cable port 1 to J1 (rear end window, along the +Y rail, onto the plug tail)', pts, None, 'J1', (), pts[:-1])]


# ----------------------------------------------------------------- knee lead across the hip joint
def leg_point(c, r, t, z, hip=0.0):
    import model as M
    a = math.radians(45)
    sx, sy = SIGN[c]
    hx, hy = sx * M.HIP_X, sy * M.HIP_Y
    x, y = r * math.cos(a) - t * math.sin(a), r * math.sin(a) + t * math.cos(a)
    x, y = sx * x, sy * y
    g = math.radians(sx * sy * hip)
    return (hx + x * math.cos(g) - y * math.sin(g), hy + x * math.sin(g) + y * math.cos(g), z)


T_TIE = (21.5, -5.5, 44.0)   # lead zip-tied around the thigh plate (leg frame): r, t, z
THIGH_RUN = [(48.5, -9.0, 49.0), (48.5, -5.5, 44.5), T_TIE]   # knee servo lead from the far end of the servo, under the body on the -t face, to the tie
BULGE_OUT, BULGE_DOWN = 8.0, 6.0


def frame_tie(c):
    import model as M
    sx, sy = SIGN[c]
    return (sx * 59.5, sy * 39.2, 32.0)


def loop_points(c, hip):
    """Free loop from the thigh tie to the frame tie at hip angle hip: outward and downward bow, away from the body."""
    a = leg_point(c, *T_TIE, hip=hip)
    b = frame_tie(c)
    sx, sy = SIGN[c]
    mx, my, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
    n = math.hypot(1, 1)
    m = (mx + sx * BULGE_OUT / n, my + sy * BULGE_OUT / n, mz - BULGE_DOWN)
    return [a, m, b]


def sweep_job(j):
    c, hips, knees = j
    import cadquery as cq
    from mech_check import leg_pose, load, ref_labels
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape as D
    labels = ref_labels()['ref_DO_NOT_PRINT_servos']
    sv = load('ref_DO_NOT_PRINT_servos').solids().vals()
    ks0 = sv[labels.index(f'SG90 knee {c} (+horn)')]
    fixed = [(n, load(n).val()) for n in ('frame_lower', 'frame_upper')]
    fixed += [(lab, s) for lab, s in zip(labels, sv) if lab.startswith('SG90 hip')]
    sx, sy = SIGN[c]
    worst, worst_at, maxlen, n = 1e9, None, 0.0, 0
    worst_run, run_at = 1e9, None
    for hip in hips:
        for knee in knees:
            n += 1
            th, ft = leg_pose(c, hip, knee)
            ks = ks0
            if hip:
                import model as M
                hx, hy = sx * M.HIP_X, sy * M.HIP_Y
                ks = ks.rotate(cq.Vector(hx, hy, 0), cq.Vector(hx, hy, 1), sx * sy * hip)
            pts = loop_points(c, hip)
            maxlen = max(maxlen, sum(math.dist(a, b) for a, b in zip(pts, pts[1:])))
            wire = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)) for a, b in zip(pts, pts[1:])])
            # the first 25 % of the free span leaves the thigh tie: it may touch the thigh by construction
            q = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*[pts[0][k] + 0.25 * (pts[1][k] - pts[0][k]) for k in range(3)]), cq.Vector(*pts[1])), cq.Edge.makeLine(cq.Vector(*pts[1]), cq.Vector(*pts[2]))])
            items = fixed + [('foot', ft), ('knee servo', ks)]
            for lab, s in items:
                d = D((q if lab == 'foot' or lab == 'knee servo' else wire).wrapped, s.wrapped)
                d.Perform()
                v = d.Value() - LOOP_R
                if v < worst:
                    worst, worst_at = v, (hip, knee, lab)
            d = D(q.wrapped, th.wrapped)
            d.Perform()
            v = d.Value() - LOOP_R
            if v < worst:
                worst, worst_at = v, (hip, knee, 'thigh')
            # the run on the thigh, from the servo end to the thigh tie, rides with the thigh: check it against the frame and the moving foot
            rp = [leg_point(c, *p, hip=hip) for p in THIGH_RUN]
            run = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)) for a, b in zip(rp, rp[1:])])
            for lab, s in fixed + [('foot', ft)]:
                d = D(run.wrapped, s.wrapped)
                d.Perform()
                v = d.Value() - WIRE_R
                if v < worst_run:
                    worst_run, run_at = v, (hip, knee, lab)
    return {'corner': c, 'poses': n, 'hipDeg': [min(hips), max(hips)], 'kneeDeg': [min(knees), max(knees)], 'minLeadClearanceMm': round(worst, 2),
            'worstAt': {'hip': worst_at[0], 'knee': worst_at[1], 'against': worst_at[2]}, 'maxFreeSpanMm': round(maxlen, 1),
            'thighRunClearanceMm': round(worst_run, 2), 'thighRunWorstAt': {'hip': run_at[0], 'knee': run_at[1], 'against': run_at[2]},
            'pass': worst > 0.0 and worst_run > 0.0}


_wires = {}


def moving_job(j):
    """One leg pose against the complete finished lead of every route: thigh, foot and knee servo of that leg (with its hip rotation) vs each lead polyline."""
    c, hip, knee, polys = j
    import cadquery as cq
    from mech_check import leg_pose, load, ref_labels
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape as D
    import model as M
    if not _wires:
        for name, vname, pl in polys:
            w = cq.Wire.assembleEdges([cq.Edge.makeLine(cq.Vector(*a), cq.Vector(*b)) for a, b in zip(pl, pl[1:])])
            _wires[(name, vname)] = (w, w.BoundingBox(), CABLE_R if name.startswith('usb') else WIRE_R)
    labels = ref_labels()['ref_DO_NOT_PRINT_servos']
    ks = load('ref_DO_NOT_PRINT_servos').solids().vals()[labels.index(f'SG90 knee {c} (+horn)')]
    sx, sy = SIGN[c]
    if hip:
        hx, hy = sx * M.HIP_X, sy * M.HIP_Y
        ks = ks.rotate(cq.Vector(hx, hy, 0), cq.Vector(hx, hy, 1), sx * sy * hip)
    th, ft = leg_pose(c, hip, knee)
    parts = [('thigh', th), ('foot', ft), ('knee servo', ks)]
    boxes = [(lab, s, s.BoundingBox()) for lab, s in parts]
    out = {}
    for key, (w, wb, tube) in _wires.items():
        best = (1e9, '')
        for lab, s, sb in boxes:
            gap = max(wb.xmin - sb.xmax, sb.xmin - wb.xmax, wb.ymin - sb.ymax, sb.ymin - wb.ymax, wb.zmin - sb.zmax, sb.zmin - wb.zmax, 0.0)
            if gap >= best[0]:
                continue
            d = D(w.wrapped, s.wrapped)
            d.Perform()
            if d.Value() < best[0]:
                best = (d.Value(), lab)
        out[key] = (round(best[0] - tube, 2), c, hip, knee, best[1])
    return out


STRAP_T = 1.5                # strap band outside the bars, z 3.5..16.5, across the open front face and the rear


def strap_job(j):
    """Bank strap band as real solids against the moving leg at every pose (the strap sits outside the frame bars)."""
    c, hips, knees = j
    import cadquery as cq
    from mech_check import leg_pose
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape as D
    t = STRAP_T
    z0, z1 = 3.5, 16.5
    band = [bx(-62.5 - t, 62.5 + t, 37.0, 37.0 + t, z0, z1), bx(-62.5 - t, 62.5 + t, -37.0 - t, -37.0, z0, z1),
            bx(62.5, 62.5 + t, -37.0, 37.0, z0, z1), bx(-62.5 - t, -62.5, -37.0, 37.0, z0, z1)]
    worst, at = 1e9, None
    for hip in hips:
        for knee in knees:
            parts = leg_pose(c, hip, knee)
            for m in parts:
                for b in band:
                    d = D(m.wrapped, b.wrapped)
                    d.Perform()
                    if d.Value() < worst:
                        worst, at = d.Value(), (hip, knee)
    return {'corner': c, 'minClearanceMm': round(worst, 2), 'worstAt': {'hip': at[0], 'knee': at[1]}, 'pass': worst > 0.0}


def main():
    coarse = '--coarse' in sys.argv
    h = hashlib.sha256()
    for f in sorted(OUT.glob('*.step')) + [Path(__file__), Path(__file__).parent / 'mech_check.py', ROOT / 'case/model.py']:
        h.update(f.read_bytes())
    key = h.hexdigest() + ('-coarse' if coarse else '')
    target = ROOT / 'case/reports/route-evidence.json'
    if target.exists() and '--force' not in sys.argv:
        old = json.loads(target.read_text())
        if old.get('inputHash') == key:
            print('route evidence up to date')
            return 0 if old.get('pass') else 1
    t0 = time.time()
    sys.path.insert(0, str(Path(__file__).parent))
    defs = route_defs()
    hips = [-30, -15, 0, 15, 30] if coarse else [-30, -25, -20, -10, 0, 10, 20, 25, 30]
    knees = [-30, 0, 30] if coarse else [-30, -25, -15, 0, 15, 25, 30]
    with cf.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        routes = list(ex.map(route_job, defs, chunksize=1))
        sweeps = list(ex.map(sweep_job, [(c, hips, knees) for c in CORNERS], chunksize=1))
        straps = list(ex.map(strap_job, [(c, hips, knees) for c in CORNERS], chunksize=1))
        polys = [(d[0], v, pl) for d in defs for v, pl in lead_polylines(d)]
        moving = list(ex.map(moving_job, [(c, h, k, polys) for c in CORNERS for h in hips for k in knees], chunksize=4))
    # complete finished lead against every moving leg part, every pose
    mv = {}
    for pose in moving:
        for rk, rec in pose.items():
            if rk not in mv or rec[0] < mv[rk][0]:
                mv[rk] = rec
    for r in routes:
        rows = [{'leadExit': v, 'minClearanceMm': mv[(r['route'], v)][0], 'worst': dict(zip(('corner', 'hip', 'knee', 'against'), mv[(r['route'], v)][1:]))} for v in [k[1] for k in mv if k[0] == r['route']]]
        r['movingLegs'] = rows
        r['movingMinClearanceMm'] = min(x['minClearanceMm'] for x in rows)
        r['movingPass'] = all(x['minClearanceMm'] > 0.0 for x in rows)
    # two genuinely different routes per lead
    free_span = max(s['maxFreeSpanMm'] for s in sweeps)
    for r in routes:
        if r['route'].startswith(('power', 'usb')):
            r['leadLengthBudgetMm'] = None
            continue
        L = max(v['pathLengthMm'] for v in r['leadExitVariants'])
        need = L + PLUG_END + (THIGH_RUN_LEN + max(free_span + SLACK_RULE, 40.0) if r['route'].startswith('knee') else 0.0)
        r['leadLengthNeededMm'] = round(need, 1)
        r['fitsNominalLead'] = need <= NOMINAL_LEAD
    per = {}
    for r in routes:
        if r['route'].startswith(('power', 'usb')):
            continue
        per.setdefault(r['route'].split(' route ')[0], []).append(r)
    leadsOk = {k: sum(1 for r in v if r['plugPass'] and r['leadPass'] and r['movingPass']) for k, v in per.items()}
    lengthOk = {k: sum(1 for r in v if r.get('fitsNominalLead') and r['plugPass'] and r['leadPass'] and r['movingPass']) for k, v in per.items()}
    power = next(r for r in routes if r['route'].startswith('power'))
    loop = 'free loop: leave at least the max free span below + 15 mm between the two ties (minimum 40 mm)'
    usb = next((r for r in routes if r['route'].startswith('usb')), None)
    usb_ok = usb is None or (usb['leadPass'] and usb['movingPass'])
    res = {'schema': 1, 'pass': all(n >= 2 for n in leadsOk.values()) and power['leadPass'] and power['movingPass'] and usb_ok and all(s['pass'] for s in sweeps) and all(s['pass'] for s in straps), 'inputHash': key,
           'bankStrapVsLegs': {'bandMm': {'thickness': STRAP_T, 'z': [3.5, 16.5]}, 'sweeps': straps},
           'checkedOn': 'exported robot-frame STEP solids of frame_lower, frame_upper, servo and board references',
           'plugEnvelopeMm': {'widthThicknessLength': PLUG, 'note': 'rigid housing, common SG90 JR plug 7.6 x 3.9 x 14 mm plus margin'},
           'plugModel': 'At every station (3 mm apart) at least one collision-free orientation must exist: tangent to the path, turned about Z up to 90 deg, flat or edge-on, or upright. Models a hand turning the plug, not a jig.',
           'movingLegCheck': {'poses': len(moving), 'hipDeg': [min(hips), max(hips)], 'kneeDeg': [min(knees), max(knees)], 'sampling': 'coarse' if coarse else 'full',
                              'method': 'Each finished fixed lead (tube, whole polyline from servo end or frame tie to above the header) against the thigh, foot and knee servo of all 4 legs at every hip x knee pose. Plug paths are carried with the legs off (Bước 7 before Bước 8).'},
           'wireModel': f'flat 3-core lead 1.3 thick (fixed run, tube Ø{2 * WIRE_R}); free span across the hip joint as a Ø{2 * LOOP_R} bundle',
           'electronicsVariants': {
               'routeThroughFrame': 'The chamber, end-window and side-bay parts of every route only depend on the frame and the SG90s, so they hold for any electronics in the frame.',
               'lastLegToHeader': 'The final leg ends at the headers J2..J9 of the integrated board (note 4), which exists only as CAD and is not manufactured.',
               'ownerCurrentWiring': 'NOT covered: the owner’s current LILYGO + PCA9685 assembly has no mount in this frame. No route here proves those wires can be installed.'},
           'routes': routes, 'routesPassingPerLead': leadsOk, 'routesWithinNominalLeadPerLead': lengthOk,
           'leadLengthModel': {'nominalMm': NOMINAL_LEAD, 'plugEndMm': PLUG_END, 'kneeAdds': f'{THIGH_RUN_LEN} mm thigh run + free span + {SLACK_RULE} mm slack (minimum 40 mm)', 'note': 'GIA DINH: SG90 lead length is unmeasured. Routes over the nominal length need a servo extension lead (BOM optional).'},
           'usbCableRoute': None if usb is None else {**{k: usb[k] for k in ('route', 'leadClearanceMm', 'leadClosest', 'leadPass', 'movingMinClearanceMm', 'movingPass', 'pathLengthMm', 'tubeDiaMm')}, 'cableLengthNeededMm': round(usb['pathLengthMm'] + 25.0, 1), 'note': 'Path plus 25 mm for the USB-A plug tail and bends; a 30 cm cable is the BOM criterion. Round Ø4.5 cable is an assumption.'},
           'powerRoute': {k: power[k] for k in ('route', 'leadClearanceMm', 'leadClosest', 'leadPass', 'movingMinClearanceMm', 'movingPass', 'pathLengthMm')}, 'requiredPerLead': 2,
           'kneeLeadCrossingHipJoint': {'tieOnThigh': 'zip tie around the thigh plate at r 21.5, on the -t face, no change to the printed thigh',
                                        'tieOnFrame': 'zip tie around the corner column of the frame (one tie per leg)',
                                        'sweeps': sweeps, 'slackRule': loop, 'sampling': 'coarse' if coarse else 'full',
                                        'note': 'discrete pose samples of the free span, not a continuous proof and not a physical wire test'},
           'runtimeS': round(time.time() - t0, 1),
           'unproven': 'Wire flexibility, how a real lead stacks in the chamber, and real tie tension can only be judged by the owner on the printed frame.'}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'pass': res['pass'], 'runtimeS': res['runtimeS'], 'perLead': leadsOk, 'withinLead': lengthOk, 'power': res['powerRoute'], 'sweeps': [(s['corner'], s['minLeadClearanceMm'], s['worstAt'], s['maxFreeSpanMm']) for s in sweeps], 'strap': [(s['corner'], s['minClearanceMm'], s['worstAt']) for s in straps]}))
    for r in routes:
        if not r['plugPass'] or not r['leadPass'] or not r['movingPass']:
            print(' ROUTE', r['route'], r['plugPass'], r['leadPass'], r['leadClearanceMm'], r['leadClosest'], r['plugCollisions'][:3], r['movingMinClearanceMm'], [x['worst'] for x in r['movingLegs']])
    return 0 if res['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())

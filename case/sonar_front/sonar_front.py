"""Front sonar head: two HC-SR04P lying flat side by side in a V, the four "eyes" in one row, on the +Y (Tiến, screen
side) face of frame_upper, just under the screen.

Seen from above the head is an isosceles triangle (owner, 2026-11-17, from his photo of a module held against the
face): the back plate along the +Y side rail is the base, the two modules are the equal sides and meet at the apex in
front of x = 0. Each module is turned `yaw_deg` outwards (right module looks right = +X, left module looks left) and
tilted `pitch_deg` up. The right-angle header is on the bottom edge, so the Dupont plugs hang down, below the head,
and the wires go back under the body; nothing rises in front of the screen.

The back plate rests on the outside face of the +Y side rail (y 34..37.05, z 34.4..39.95) and is held by two zip
ties around it (glue it as well if wanted). A centre spine ties the apex to the plate; the outer end lips join the
plate ends.

Frames:
  * robot (CAD) frame of case/model.py: +Y = the owner's front (Tiến), +X = old bank mouth, z0 = frame_lower bottom.
  * module-local (one HC-SR04P), as in ../sonar_bracket: X = s along the PCB length (centre 0), Y = v across it
    (0 = the top edge under the shelf, pcb_h = the header edge at the bottom), Z = w along the face normal
    (0 = PCB back face, 1.6 = front, 13.6 = can faces).
  * print: upside down, the top plane `z_cut` (shelves, plate and spine tops) on the bed.

Module retention: two M2x6 self-taps per module from the back, through the PCB holes on the header edge, into bosses on
the bezel front (or a drop of glue); the top edge sits under the shelf and the ends between the end lips.
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sonar_bracket'))
import sonar_bracket as SB  # noqa: E402  (module dimensions, primitives, module envelope)

M = SB.P            # HC-SR04P module numbers (GIA DINH, see ../sonar_bracket/sonar_bracket.py)
box, cyl_z, _union = SB.box, SB.cyl_z, SB._union
SIDES = (('right', 1), ('left', -1))


@dataclass(frozen=True)
class Params:
    # aim
    yaw_deg: float = 12.0         # each module turned outwards: the two 15 deg beams cover -27..+27 and overlap 6 deg
                                  # straight ahead, so both sensors see an obstacle dead ahead; > 15 opens a blind gap
    pitch_deg: float = 8.0        # can axes tilted up; the beams' lower edges reach the floor beyond AUTO_SLOW
    # module placement
    apex_x: float = 2.2           # PCB inner end (back face) off the centre line: the inner end lips stay on their side
    z_cut: float = 43.0           # shelf tops = plate top = print bed; 1.45 mm over the upper tie slot, 9 mm under the
                                  # screen's bottom edge (z 52.1)
    back_gap: float = 0.4         # module back parts to the plate front
    # body interface: +Y side rail of frame_upper (measured in case/robot/frame_upper.step)
    rail_y: tuple = (34.0, 37.05)
    rail_z: tuple = (34.4, 39.95)
    plate_y0: float = 37.25       # plate back face, 0.2 off the rail face
    plate_t: float = 2.4
    plate_z0: float = 24.0
    tie_x: tuple = (-12.0, 12.0)  # off the rim posts (x -46..-40, -1..5) that stand over the rail top; the screen-stand
                                  # snap tabs over x -12.5..-3.5 are higher (z >= 42.3) than the tie (<= 41.2)
    tie_w: float = 3.0            # slot for a 2.5 mm zip tie
    tie_h: float = 1.6            # ... <= 1.3 mm thick
    spine_half: float = 1.6
    driver_d: float = 6.0         # channels for a 5 mm screwdriver shaft where the plate is in the way


P = Params()


def validate(p: Params = P):
    assert p.z_cut <= 52.1 - 3.0, 'top would reach the screen'
    assert p.z_cut >= p.rail_z[1] + p.tie_h + 1.2, 'no material over the upper tie slot'
    assert p.plate_z0 <= p.rail_z[0] - p.tie_h - 1.2, 'plate must reach below the lower tie slot'
    tie_top = p.rail_z[1] + 1.2
    for x in p.tie_x:
        a, b = x - p.tie_w / 2, x + p.tie_w / 2
        for lo, hi in ((-46.0, -40.0), (-1.0, 5.0)):
            assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} on a rim post'
        if tie_top > 42.3 - 0.5:
            for lo, hi in ((-32.5, -23.5), (-12.5, -3.5)):
                assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} under a snap tab'
    assert 0 < p.yaw_deg <= 15.0, 'yaw > 15 opens a blind gap straight ahead between the two 15 deg beams'


# ------------------------------------------------------------------------------------------------ module frame
def axes(p: Params = P):
    """Right module: S (along the PCB, outwards), Tv (toward the header edge = down), N (face normal)."""
    y, t = math.radians(p.yaw_deg), math.radians(p.pitch_deg)
    N = np.array([math.sin(y) * math.cos(t), math.cos(y) * math.cos(t), math.sin(t)])
    up = np.array([0.0, 0.0, 1.0]) - math.sin(t) * N
    Tv = -up / np.linalg.norm(up)
    S = np.cross(Tv, N)
    if S[0] < 0:                  # keep S outwards; flip N's partner to stay right-handed
        S, Tv = -S, Tv            # (never happens for Tv = down, N forward: S = down x forward = +x)
    return S, Tv, N


def _shelf_top_v():
    return -M.shelf_t


def origin(p: Params = P):
    """Module-local origin in the robot frame. The inner end of the PCB back face sits at x = apex_x, the shelf top on
    z_cut, and y is the smallest that keeps the back parts (s <= 16, w -3) `back_gap` in front of the plate."""
    S, Tv, N = axes(p)
    L2 = M.pcb_l / 2
    o = np.zeros(3)
    o[0] = p.apex_x - (-L2) * S[0]
    # highest shelf-top corner on z_cut (shelf: v = -shelf_t, w from the 45 deg edge to the bezel front)
    zf = M.pcb_t + M.bezel_t
    zs = max((-L2 * k) * S[2] + _shelf_top_v() * Tv[2] + w * N[2] for k in (-1, 1) for w in (M.pcb_t - M.shelf_back, zf))
    o[2] = p.z_cut - zs
    yb = min(s * S[1] + v * Tv[1] + (-M.back_comp) * N[1] for s in (-16.0, 16.0) for v in (1.5, M.pcb_h - 1.5))
    o[1] = p.plate_y0 + p.plate_t + p.back_gap - yb
    return o


def to_robot_pt(s, v, w, p: Params = P, side=1):
    S, Tv, N = axes(p)
    q = origin(p) + s * S + v * Tv + w * N
    return (float(side * q[0]), float(q[1]), float(q[2]))


def place(shape, p: Params = P, side=1):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf
    S, Tv, N = axes(p)
    O = origin(p)
    t = gp_Trsf()
    t.SetValues(*[float(x) for x in (S[0], Tv[0], N[0], O[0], S[1], Tv[1], N[1], O[1], S[2], Tv[2], N[2], O[2])])
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    out = cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped, t, True).Shape())
    return out.mirror('YZ') if side < 0 else out


# ------------------------------------------------------------------------------------------------ holder (module-local)
PRINT_UP_V = 1.0          # +v (toward the header edge = robot down) is up in the upside-down print


def _can_cutter(xc, d):
    """Can hole along module Z with a truncated teardrop toward v-direction d (print up)."""
    r, yc = M.can_hole_d / 2, M.pcb_h / 2
    z0, z1 = M.pcb_t - 0.5, M.pcb_t + M.bezel_t + M.boss_h + 0.5
    hole = cyl_z(xc, yc, z0, z1, M.can_hole_d)
    k, tip = r / math.sqrt(2), r * math.sqrt(2)
    tri = (cq.Workplane('XY').polyline([(xc - k, yc + d * k), (xc, yc + d * tip), (xc + k, yc + d * k), (xc, yc)]).close()
           .extrude(z1 - z0).val().translate(cq.Vector(0, 0, z0)))
    keep = box(xc - 20, xc + 20, yc - r - 1.0, yc + r + 1.0, z0 - 1, z1 + 1)      # flat tip, 1 mm past the circle
    return hole.fuse(tri.intersect(keep))


def _boss(bx, by, zf, d):
    """M2 self-tap boss on the bezel front with a 45 deg wedge toward v-direction d (print down)."""
    r = M.boss_d / 2
    c = cyl_z(bx, by, zf - 0.01, zf + M.boss_h, M.boss_d)
    wedge = (cq.Workplane('XY').polyline([(bx - r, by), (bx, by + d * r * math.sqrt(2)), (bx + r, by)]).close()
             .extrude(M.boss_h + 0.01).val().translate(cq.Vector(0, 0, zf - 0.01)))
    return c.fuse(wedge)


def holder_local(p: Params = P):
    L2 = M.pcb_l / 2
    xe = L2 + M.end_fit + M.lip_t
    zf = M.pcb_t + M.bezel_t
    by = M.pcb_h / 2 + M.hole_dy / 2
    parts = [
        box(-xe, xe, 0.0, M.pcb_h, M.pcb_t, zf),                                   # bezel
        SB._shelf(M, xe, zf),                                                      # shelf over the PCB top edge
        box(L2 + M.end_fit, xe, -M.shelf_t, M.pcb_h, -M.lip_back, zf),             # end lips
        box(-xe, -L2 - M.end_fit, -M.shelf_t, M.pcb_h, -M.lip_back, zf),
    ] + [_boss(bx, by, zf, -PRINT_UP_V) for bx in (-M.hole_dx / 2, M.hole_dx / 2)]
    s = _union(parts)
    for xc in (M.can_pitch / 2, -M.can_pitch / 2):
        s = s.cut(_can_cutter(xc, PRINT_UP_V))
    cw = M.centre_win
    s = s.cut(box(-cw, cw, -0.01, M.pcb_h + 1, M.pcb_t - 0.01, zf + 1))           # crystal + header plastic relief
    for bx in (-M.hole_dx / 2, M.hole_dx / 2):
        s = s.cut(cyl_z(bx, by, -1.0, zf + M.boss_h + 0.5, M.pilot_d))
    return s.clean()


# ------------------------------------------------------------------------------------------------ head (robot frame)
def hull_solid(pts):
    """Convex hull of 3D points as a solid."""
    from scipy.spatial import ConvexHull
    pts = np.asarray(pts, dtype=float)
    h = ConvexHull(pts)
    ctr = pts[h.vertices].mean(axis=0)
    faces = []
    for tri in h.simplices:
        a, b, c = pts[tri]
        if np.dot(np.cross(b - a, c - a), a - ctr) < 0:
            b, c = c, b
        faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*a), cq.Vector(*b), cq.Vector(*c)], close=True)))
    return cq.Solid.makeSolid(cq.Shell.makeShell(faces)).fix().clean()


def _lip_pts(end, p: Params = P, side=1, w_back=None):
    """Robot-frame corners of an end lip (end -1 = inner, +1 = outer)."""
    L2 = M.pcb_l / 2
    xe = L2 + M.end_fit + M.lip_t
    zf = M.pcb_t + M.bezel_t
    w0 = -M.lip_back if w_back is None else w_back
    s0, s1 = sorted((end * (L2 + M.end_fit), end * xe))
    return [to_robot_pt(s, v, w, p, side) for s in (s0, s1) for v in (-M.shelf_t, M.pcb_h) for w in (w0, zf)]


def apex(p: Params = P):
    """Solid wedge joining the two inner end lips in front of x = 0."""
    return hull_solid(_lip_pts(-1, p, 1) + _lip_pts(-1, p, -1))


def plate_x(p: Params = P):
    """Plate half-width: out to the outer end lips."""
    return max(q[0] for q in _lip_pts(1, p, 1))


def corner(p: Params = P, side=1):
    """Hull joining an outer end lip to the plate behind it."""
    lp = _lip_pts(1, p, side)
    zs = [q[2] for q in lp]
    xs = [q[0] for q in lp]
    pl = [(x, p.plate_y0 + p.plate_t - 0.5, z) for x in (min(xs), max(xs)) for z in (max(min(zs), p.plate_z0), max(zs))]
    return hull_solid(lp + pl)


def spine(p: Params = P):
    """Centre rib from the plate to the apex, under the shelf tops."""
    ap = apex(p).BoundingBox()
    return box(-p.spine_half, p.spine_half, p.plate_y0 + 0.5, ap.ymin + 1.0, max(ap.zmin, p.plate_z0), p.z_cut)


def tie_slots(p: Params = P):
    return [(f'slot x{x:+.0f} {"upper" if z0 > p.rail_z[0] else "lower"}',
             box(x - p.tie_w / 2, x + p.tie_w / 2, p.plate_y0 - 1, p.plate_y0 + p.plate_t + 1, z0, z0 + p.tie_h))
            for x in p.tie_x for z0 in (p.rail_z[1], p.rail_z[0] - p.tie_h)]


def screw_axes(p: Params = P):
    by = M.pcb_h / 2 + M.hole_dy / 2
    return [(f'{lab} {"outer" if s > 0 else "inner"}', side, s, by) for lab, side in SIDES for s in (-M.hole_dx / 2, M.hole_dx / 2)]


def screwdrivers(p: Params = P, length=60.0, d=5.0):
    return [(f'screwdriver {lab}', place(cyl_z(s, v, -0.5 - length, -0.5 - 2.0, d), p, side)) for lab, side, s, v in screw_axes(p)]


def driver_channels(p: Params = P):
    return [(f'channel {lab}', place(cyl_z(s, v, -60.0, -M.lip_back - 0.2, p.driver_d), p, side)) for lab, side, s, v in screw_axes(p)]


def head_robot(p: Params = P):
    validate(p)
    h = holder_local(p)
    px = plate_x(p)
    plate = box(-px, px, p.plate_y0, p.plate_y0 + p.plate_t, p.plate_z0, p.z_cut)
    s = _union([place(h, p, 1), place(h, p, -1), apex(p), spine(p), plate, corner(p, 1), corner(p, -1)])
    for _, slot in tie_slots(p):
        s = s.cut(slot)
    for _, c in driver_channels(p):
        s = s.cut(c)
    s = s.cut(box(-90, 90, 0, 120, p.z_cut, p.z_cut + 40))
    return s.clean()


def to_print(shape, p: Params = P):
    """Robot frame -> print orientation: upside down (180 deg about X), the z_cut plane on the bed, centred."""
    s = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def modules_robot(p: Params = P):
    """Both HC-SR04P envelopes (header on the bottom edge, plug hanging down) in the robot frame: [(label, solid)]."""
    out = []
    for name, s in SB.module_dummy_local(M, 'inplane').items():
        s = s.val() if isinstance(s, cq.Workplane) else s
        for lab, side in SIDES:
            out.append((f'HC-SR04P {lab} {name}', place(s, p, side)))
    return out


def beams_robot(p: Params = P):
    """[(label, can-face centre, unit axis)] in the robot frame."""
    N = axes(p)[2]
    out = []
    for lab, side in SIDES:
        for xc, which in ((-M.can_pitch / 2, 'inner'), (M.can_pitch / 2, 'outer')):
            c = to_robot_pt(xc, M.pcb_h / 2, M.pcb_t + M.can_h, p, side)
            out.append((f'{lab} can {which}', c, (float(side * N[0]), float(N[1]), float(N[2]))))
    return out


def tie_bands(p: Params = P):
    """Zip ties (2.5 x 1.2) around the rail, through the plate slots."""
    out = []
    for x in p.tie_x:
        y0, y1 = p.rail_y[0] - 1.2, p.plate_y0 + p.plate_t + 1.2
        z0, z1 = p.rail_z[0] - 1.2, p.rail_z[1] + 1.2
        ring = box(x - 1.25, x + 1.25, y0, y1, z0, z1).cut(box(x - 2, x + 2, p.rail_y[0], p.plate_y0 + p.plate_t, p.rail_z[0], p.rail_z[1]))
        out.append((f'zip tie x{x:+.0f}', ring))
    return out


def gen_step():
    return {'shape': to_print(head_robot(P)), 'mesh_tolerance': 0.03, 'mesh_angular_tolerance': 2.0}


if __name__ == '__main__':
    h = head_robot()
    bb = h.BoundingBox()
    print('valid', h.isValid(), 'solids', len(h.Solids()), 'vol', round(h.Volume(), 1), [round(v, 1) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
    for lab, s in modules_robot():
        if ' right ' in lab:
            b = s.BoundingBox()
            print(lab, [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
    for lab, c, a in beams_robot():
        print(lab, [round(v, 1) for v in c], [round(v, 3) for v in a])

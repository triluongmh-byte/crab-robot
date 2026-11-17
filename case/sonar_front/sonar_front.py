"""Front sonar head: two HC-SR04P lying flat, one above the other, on the +Y (Tiến, screen side) face of frame_upper,
under the screen stand. The owner (2026-11-17) wanted the four "eyes" side by side like a face; a single row of four
(about 94 mm wide) hits the hip servos and the front legs, so the two modules sit in two rows of two instead:
  * upper module: looks `yaw_deg` to the LEFT (-X)  -> the left sensor  (GPIO10/11)
  * lower module: looks `yaw_deg` to the RIGHT (+X) -> the right sensor (GPIO12/13)
both tilted `pitch_deg` up. Each row is 49 mm wide, so the head stays inside the free space between the front legs.

The HC-SR04P right-angle header sits on a long edge: the upper module has it on top, the lower one at the bottom, and
the owner bends the four pins 90 deg backwards, so both Dupont plugs go back toward the body instead of up into the
screen or down onto the floor.

A back plate rests on the +Y side rail of frame_upper (y 34..37.05, z 34.4..39.95), held by two zip ties around it.
A centre spine runs forward from the plate to a middle beam, which joins the two module shelves.

Frames:
  * robot (CAD) frame of case/model.py: +Y = the owner's front (Tiến), +X = old bank mouth, z0 = frame_lower bottom.
  * module-local (one HC-SR04P), as in ../sonar_bracket: X = s along the PCB length (centre 0), Y = v across it
    (0 = the inner edge on the middle beam, pcb_h = the header edge), Z = w along the face normal
    (0 = PCB back face, 1.6 = front, 13.6 = can faces).
  * print: upside down, the top plane `z_cut` on the bed.

Module retention: two M2x6 self-taps per module from the back, through the PCB holes on the header edge, into bosses on
the bezel front; the inner edge rests on the shelf and the ends sit between the end lips. Screw the modules in on the
bench before tying the head to the rail (check_fit: screwdriver access).
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sonar_bracket'))
import sonar_bracket as SB  # noqa: E402  (module dimensions, primitives)

M = SB.P            # HC-SR04P module numbers (GIA DINH, see ../sonar_bracket/sonar_bracket.py)
box, cyl_z, _union = SB.box, SB.cyl_z, SB._union
ROWS = ('upper', 'lower')


@dataclass(frozen=True)
class Params:
    # aim
    yaw_deg: float = 15.0         # upper module turned left, lower turned right; at 20+ the beams see the own front feet
    pitch_deg: float = 10.0       # can axes tilted up; the low cans stay clear of floor echoes (check_fit floorHit)
    # module placement: PCB back face, mid-length, mid-height of each module
    y_back: float = 58.0          # 18 mm in front of the plate: room for the bent-back Dupont plugs
    z_upper: float = 40.6
    z_lower: float = 17.4          # the lower bent-back plug clears the floor in the Ngủ pose
    # bent-back header / Dupont plug envelope (module-local, beyond the header edge)
    plug_v: float = 3.6           # pins bent 90 deg right at the edge + 2.5 mm housing
    plug_back: float = 15.0       # housing 14 mm behind the PCB back + wire
    # body interface: +Y side rail of frame_upper (measured in case/robot/frame_upper.step)
    rail_y: tuple = (34.0, 37.05)
    rail_z: tuple = (34.4, 39.95)
    plate_y0: float = 37.25       # plate back face, 0.2 off the rail face
    plate_t: float = 2.4
    plate_x: float = 19.0         # half-width
    plate_z0: float = 16.0
    tie_x: tuple = (-12.0, 12.0)  # off the rim posts (x -46..-40, -1..5) that stand over the rail top; the screen-stand
                                  # snap tabs over x -12.5..-3.5 are higher (z >= 42.3) than the tie (<= 41.2)
    tie_w: float = 3.0            # slot for a 2.5 mm zip tie
    tie_h: float = 1.6            # ... <= 1.3 mm thick
    spine_x: float = 7.0          # half-width of the centre spine
    spine_slope: float = 1.27     # spine faces rise tan(52 deg) per mm back from each shelf edge in module axes: 45 deg
                                  # to the bed in print (pitch 10), and they pass under the back parts (w -3, v 1.5)
    driver_d: float = 6.0         # channels for a 5 mm screwdriver shaft where the plate is in the way
    z_cut: float = 51.0           # flat top = print bed; under the screen (front-bottom cradle edge z 52.1) and in front
                                  # of the stand (y >= 37.25 vs <= 37.02)


P = Params()


def validate(p: Params = P):
    assert p.z_cut <= 52.1 - 1.0 and p.plate_y0 >= 37.02 + 0.2, 'top would reach the screen'
    assert p.plate_z0 <= p.rail_z[0] - p.tie_h - 1.0, 'plate must reach below the lower tie slot'
    tie_top = p.rail_z[1] + 1.2
    for x in p.tie_x:
        a, b = x - p.tie_w / 2, x + p.tie_w / 2
        for lo, hi in ((-46.0, -40.0), (-1.0, 5.0)):
            assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} on a rim post'
        if tie_top > 42.3 - 0.5:
            for lo, hi in ((-32.5, -23.5), (-12.5, -3.5)):
                assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} under a snap tab'
        assert abs(x) + p.tie_w / 2 + 1.6 <= p.plate_x, 'tie slot too close to the plate edge'
    assert p.y_back - p.plug_back >= p.plate_y0 + p.plate_t + 0.3, 'bent-back plugs would hit the plate'
    assert 5.0 <= p.spine_x <= 16.0 - 1.0, 'spine: between the back parts end (s 16) and stiff enough'


# ------------------------------------------------------------------------------------------------ module frames
def axes(row, p: Params = P):
    """(S, Tv, N) of a module, right-handed: S along the length, Tv toward the header edge, N the face normal.
    upper: looks left (-X), header up; lower: looks right (+X), header down."""
    y, t = math.radians(p.yaw_deg), math.radians(p.pitch_deg)
    sx = -1.0 if row == 'upper' else 1.0
    N = np.array([sx * math.sin(y) * math.cos(t), math.cos(y) * math.cos(t), math.sin(t)])
    up = np.array([0.0, 0.0, 1.0]) - math.sin(t) * N
    up /= np.linalg.norm(up)
    Tv = up if row == 'upper' else -up
    S = np.cross(Tv, N)
    return S, Tv, N


def origin(row, p: Params = P):
    S, Tv, N = axes(row, p)
    c = np.array([0.0, p.y_back, p.z_upper if row == 'upper' else p.z_lower])
    return c - (M.pcb_h / 2) * Tv


def to_robot_pt(s, v, w, row, p: Params = P):
    S, Tv, N = axes(row, p)
    return tuple(float(c) for c in origin(row, p) + s * S + v * Tv + w * N)


def place(shape, row, p: Params = P):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf
    S, Tv, N = axes(row, p)
    O = origin(row, p)
    t = gp_Trsf()
    t.SetValues(*[float(x) for x in (S[0], Tv[0], N[0], O[0], S[1], Tv[1], N[1], O[1], S[2], Tv[2], N[2], O[2])])
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    return cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped, t, True).Shape())


def print_up_v(row):
    """Module-local v direction that points up in the print (= robot down): -v for upper, +v for lower."""
    return -1.0 if row == 'upper' else 1.0


# ------------------------------------------------------------------------------------------------ holder (module-local)
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


def holder_local(row, p: Params = P):
    L2 = M.pcb_l / 2
    xe = L2 + M.end_fit + M.lip_t
    zf = M.pcb_t + M.bezel_t
    by = M.pcb_h / 2 + M.hole_dy / 2
    up = print_up_v(row)
    parts = [
        box(-xe, xe, 0.0, M.pcb_h, M.pcb_t, zf),                                   # bezel
        SB._shelf(M, xe, zf),                                                      # beam along the inner edge
        box(L2 + M.end_fit, xe, -M.shelf_t, M.pcb_h, -M.lip_back, zf),             # end lips
        box(-xe, -L2 - M.end_fit, -M.shelf_t, M.pcb_h, -M.lip_back, zf),
    ] + [_boss(bx, by, zf, -up) for bx in (-M.hole_dx / 2, M.hole_dx / 2)]
    s = _union(parts)
    for xc in (M.can_pitch / 2, -M.can_pitch / 2):
        s = s.cut(_can_cutter(xc, up))
    cw = M.centre_win
    s = s.cut(box(-cw, cw, -0.01, M.pcb_h + 1, M.pcb_t - 0.01, zf + 1))           # crystal + header plastic relief
    for bx in (-M.hole_dx / 2, M.hole_dx / 2):
        s = s.cut(cyl_z(bx, by, -1.0, zf + M.boss_h + 0.5, M.pilot_d))
    return s.clean()


def module_local(p: Params = P):
    """HC-SR04P envelope with the header pins bent 90 deg backwards: dict name -> solid (module-local)."""
    L2, yc, hw = M.pcb_l / 2, M.pcb_h / 2, M.header_w / 2
    out = {'pcb': box(-L2, L2, 0, M.pcb_h, 0, M.pcb_t)}
    cans = None
    for xc in (M.can_pitch / 2, -M.can_pitch / 2):
        c = cyl_z(xc, yc, M.pcb_t, M.pcb_t + M.can_h, M.can_d)
        cans = c if cans is None else cans.fuse(c)
    out['cans'] = cans
    out['back parts'] = box(-16, 16, 1.5, M.pcb_h - 1.5, -M.back_comp, 0)
    out['crystal'] = box(-5.7, 5.7, 1.0, 5.7, M.pcb_t, M.pcb_t + 3.6)
    out['header'] = box(-hw, hw, M.pcb_h - 2.5, M.pcb_h, M.pcb_t, M.pcb_t + 2.54)
    out['dupont plug'] = box(-hw - 1.0, hw + 1.0, M.pcb_h - 0.5, M.pcb_h + p.plug_v, -p.plug_back, M.pcb_t + 2.6)
    return out


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


def _shelf_pts(row, p: Params = P):
    """Robot-frame corner points of a module's shelf (v -shelf_t..0, w from the 45 deg back edge to the bezel front)."""
    xe = M.pcb_l / 2 + M.end_fit + M.lip_t
    zf = M.pcb_t + M.bezel_t
    return [to_robot_pt(s, v, w, row, p) for s in (-xe, xe)
            for v, w in ((0.0, M.pcb_t), (-M.shelf_t, M.pcb_t - M.shelf_back), (-M.shelf_t, zf), (0.0, zf))]


def _region_local(poly_vw):
    """Module-local prism: a polygon in the (v, w) plane, through all s."""
    return cq.Workplane('YZ').polyline(poly_vw).close().extrude(240).val().translate(cq.Vector(-120, 0, 0))


def _above_chamfer(row, p: Params = P):
    """Module-local region the middle beam must leave free: the PCB slot (v >= 0) and everything above the 45 deg shelf
    chamfer behind it (v >= w - pcb_t), so nothing hangs over the slot in the upside-down print."""
    t = M.pcb_t
    return place(_region_local([(0.0, t), (200.0, t), (200.0, 200.0), (0.0, 200.0)]), row, p).fuse(
        place(_region_local([(-150.0, t - 150.0), (0.0, t), (200.0, t), (200.0, -200.0), (-150.0, -200.0)]), row, p))


def _in_front_of_slope(row, p: Params = P):
    """Module-local side of the spine slope plane that holds the module: v + shelf_t + k (w - w0) >= 0 with w0 the
    shelf back edge; the spine stays behind it."""
    k, w0 = p.spine_slope, M.pcb_t - M.shelf_back
    vb = lambda w: -M.shelf_t - k * (w - w0)      # noqa: E731
    # ... but only above the shelf bottom (v > -shelf_t): under it the spine may run forward into the middle beam
    return place(_region_local([(-M.shelf_t, w0), (vb(-150.0), -150.0), (300.0, -150.0), (300.0, 150.0), (-M.shelf_t, 150.0)]), row, p)


def middle_beam(p: Params = P):
    """Hull of the two shelves: the beam between the rows, trimmed to stay below each row's PCB slot and chamfer."""
    h = hull_solid(_shelf_pts('upper', p) + _shelf_pts('lower', p))
    for row in ROWS:
        h = h.cut(_above_chamfer(row, p))
    return h.clean()


def spine(p: Params = P):
    """Centre spine (|x| <= the tie strands): from the back edge of each shelf it runs back to the plate along a line
    that rises spine_slope per mm away from the other row (module axes), so it passes under the module back parts and
    its upper face prints at 45 deg; the lower side stops at the plate bottom (z plate_z0), clear of the lower plug."""
    yp = p.plate_y0 + 0.5
    pts = []
    for row in ROWS:
        S, Tv, N = axes(row, p)
        d = -N + p.spine_slope * Tv
        for s in (-p.spine_x, p.spine_x):
            e = np.array(to_robot_pt(s, -M.shelf_t, M.pcb_t - M.shelf_back, row, p))
            t = (e[1] - yp) / -d[1]
            if row == 'lower':
                t = min(t, (e[2] - p.plate_z0) / -d[2])
            q = e + t * d
            pts += [tuple(e), tuple(q), (q[0], yp, q[2]), to_robot_pt(s, -M.shelf_t, M.pcb_t, row, p)]   # 2 mm into the beam
    h = hull_solid(pts)
    for row in ROWS:
        h = h.cut(_in_front_of_slope(row, p))
    xl = min(abs(x) for x in p.tie_x) - 1.25 - 1.0              # stay off the zip ties' front strands
    return h.intersect(box(-xl, xl, 0, 120, -20, 80)).clean()


def tie_slots(p: Params = P):
    return [(f'slot x{x:+.0f} {"upper" if z0 > p.rail_z[0] else "lower"}',
             box(x - p.tie_w / 2, x + p.tie_w / 2, p.plate_y0 - 1, p.plate_y0 + p.plate_t + 1, z0, z0 + p.tie_h))
            for x in p.tie_x for z0 in (p.rail_z[1], p.rail_z[0] - p.tie_h)]


def screw_axes(p: Params = P):
    """[(label, row, s, v)] of the four M2 screws."""
    by = M.pcb_h / 2 + M.hole_dy / 2
    return [(f'{row} {"+x" if s * axes(row, p)[0][0] > 0 else "-x"}', row, s, by) for row in ROWS for s in (-M.hole_dx / 2, M.hole_dx / 2)]


def screwdrivers(p: Params = P, length=60.0, d=5.0):
    return [(f'screwdriver {lab}', place(cyl_z(s, v, -0.5 - length, -0.5 - 2.0, d), row, p)) for lab, row, s, v in screw_axes(p)]


def driver_channels(p: Params = P):
    return [(f'channel {lab}', place(cyl_z(s, v, -60.0, -M.lip_back - 0.2, p.driver_d), row, p)) for lab, row, s, v in screw_axes(p)]


def head_robot(p: Params = P):
    validate(p)
    hu, hl = place(holder_local('upper', p), 'upper', p), place(holder_local('lower', p), 'lower', p)
    plate = box(-p.plate_x, p.plate_x, p.plate_y0, p.plate_y0 + p.plate_t, p.plate_z0, p.z_cut)
    s = _union([hu, hl, middle_beam(p), spine(p), plate])
    for _, slot in tie_slots(p):
        s = s.cut(slot)
    for _, c in driver_channels(p):
        s = s.cut(c)
    s = s.cut(box(-80, 80, 0, 120, p.z_cut, p.z_cut + 40))
    return s.clean()


def to_print(shape, p: Params = P):
    """Robot frame -> print orientation: upside down (180 deg about X), the z_cut plane on the bed, centred."""
    s = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def modules_robot(p: Params = P):
    """Both HC-SR04P envelopes in the robot frame: [(label, solid)]."""
    return [(f'HC-SR04P {row} {name}', place(s, row, p)) for row in ROWS for name, s in module_local(p).items()]


def beams_robot(p: Params = P):
    """[(label, can-face centre, unit axis)] in the robot frame."""
    out = []
    for row in ROWS:
        N = axes(row, p)[2]
        for xc in (M.can_pitch / 2, -M.can_pitch / 2):
            c = to_robot_pt(xc, M.pcb_h / 2, M.pcb_t + M.can_h, row, p)
            out.append((f'{row} ({"left" if row == "upper" else "right"}) can {"+" if c[0] > 0 else "-"}x', c, tuple(float(a) for a in N)))
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
        b = s.BoundingBox()
        print(lab, [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
    for lab, c, a in beams_robot():
        print(lab, [round(v, 1) for v in c], [round(v, 3) for v in a])

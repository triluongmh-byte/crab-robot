"""Front sonar head: two HC-SR04P modules on the +Y (Tiến, screen side) face of frame_upper, under the screen stand.

The owner (2026-11-17) walks the crab toward +Y and does not want anything above the screen. The front legs sweep the
space in front of the +Y face down to |x| = 36 mm (hips +-35 deg, knees -100..+35 deg; see check_fit.py), which is
too narrow for two modules lying flat in a V (+-45 mm). So each module stands on its end, both cans one above the
other, turned `yaw_deg` outwards and tilted `pitch_deg` up. The two modules meet at the front centre line and a
centre rib ties them to a back plate. The plate rests on the +Y side rail of frame_upper (y 34..37.05,
z 34.4..39.95) and is held by two zip ties around that rail. A flat top web joins everything.

Frames:
  * robot (CAD) frame of case/model.py: +Y = the owner's front (Tiến), +X = old bank mouth, z0 = frame_lower bottom.
  * module-local (one HC-SR04P), as in ../sonar_bracket: X = s along the PCB length (centre 0), Y = v across it
    (0 = the inner edge, pcb_h = the header edge, which points outwards), Z = w along the face normal
    (0 = PCB back face, 1.6 = front, 13.6 = can faces).
  * print: upside down, the top web on the bed.

Module retention: two M2x6 self-taps per module go from the back, through the PCB holes on the header edge, into
bosses on the bezel front; the inner edge rests on the shelf and the top end sits under the top end stop. The modules are
screwed in on the bench, before the head is tied to the rail (check_fit: screwdriver access).
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sonar_bracket'))
import sonar_bracket as SB  # noqa: E402  (module dimensions, primitives and the module reference envelope)

M = SB.P            # HC-SR04P module numbers (GIA DINH, see ../sonar_bracket/sonar_bracket.py)
box, cyl_z, _union = SB.box, SB.cyl_z, SB._union


@dataclass(frozen=True)
class Params:
    # aim
    yaw_deg: float = 15.0         # outwards from straight ahead (+Y); at 20+ the beams see the own front feet at the
                                  # end of every trot step (hip 25 deg + knee lift), check_fit beamsVsLegs
    pitch_deg: float = 10.0       # can axis tilted up; the low can stays clear of floor echoes (check_fit floorHit)
    # module placement (right module; the left one is its mirror image in x)
    inner_x: float = 3.2          # PCB inner edge, back face, x (the PCB top leans 1.6 mm inwards: yaw + pitch)
    y_apex: float = 52.0          # ... y
    z_mid: float = 24.6           # PCB mid-length height: as high as the screen allows, because the built-in Ngủ pose
                                  # lifts all four knees 30 deg and drops the body 16.2 mm (check_fit: sleep pose)
    # holder (module-local)
    win_lo: float = 7.0           # bezel window under the crystal (v 1..5.7) ...
    win_hi: float = 16.5          # ... and under the header plastic (v >= 17.5); the strip between stays
    # body interface: +Y side rail of frame_upper (measured in case/robot/frame_upper.step)
    rail_y: tuple = (34.0, 37.05)
    rail_z: tuple = (34.4, 39.95)
    plate_y0: float = 37.25       # plate back face, 0.2 off the rail face
    plate_t: float = 2.4
    plate_x: float = 19.0         # half-width
    plate_z0: float = 30.5
    tie_x: tuple = (-12.0, 12.0)  # off the rim posts (x -46..-40, -1..5) that stand over the rail top; the screen-stand
                                  # snap tabs over x -12.5..-3.5 are higher (z >= 42.3) than the tie (<= 41.2)
    tie_w: float = 3.0            # slot for a 2.5 mm zip tie
    tie_h: float = 1.6            # ... <= 1.3 mm thick
    rib_half: float = 1.2
    driver_d: float = 6.0         # channel for a 5 mm screwdriver shaft to the top screws
    web_t: float = 2.5
    z_cut: float = 48.5           # flat top = print bed; under the screen stand cradle (front-bottom edge z 52.1)


P = Params()


def validate(p: Params = P):
    assert p.z_cut <= 52.1 - 3.0, 'top would reach the screen'
    assert p.plate_z0 <= p.rail_z[0] - p.tie_h - 1.0, 'plate must reach below the lower tie slot'
    tie_top = p.rail_z[1] + 1.2                                 # a zip tie is <= 1.2 thick
    for x in p.tie_x:
        a, b = x - p.tie_w / 2, x + p.tie_w / 2
        for lo, hi in ((-46.0, -40.0), (-1.0, 5.0)):
            assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} on a rim post'
        if tie_top > 42.3 - 0.5:
            for lo, hi in ((-32.5, -23.5), (-12.5, -3.5)):
                assert b <= lo - 0.5 or a >= hi + 0.5, f'tie at x {x} under a snap tab'
        assert abs(x) + p.tie_w / 2 + 1.6 <= p.plate_x, 'tie slot too close to the plate edge'
    assert p.win_lo >= 5.7 + 1.0 and p.win_hi <= M.pcb_h - 2.5 - 0.5 and p.win_hi - p.win_lo >= 6, 'bezel windows'


# ------------------------------------------------------------------------------------------------ module frame
def axes(p: Params = P):
    """Right module (x > 0): S (module X, up the PCB), Tv (module Y, outwards), N (module Z, face normal)."""
    y, t = math.radians(p.yaw_deg), math.radians(p.pitch_deg)
    N = (math.sin(y) * math.cos(t), math.cos(y) * math.cos(t), math.sin(t))
    Tv = (math.cos(y), -math.sin(y), 0.0)
    S = (Tv[1] * N[2] - Tv[2] * N[1], Tv[2] * N[0] - Tv[0] * N[2], Tv[0] * N[1] - Tv[1] * N[0])
    return S, Tv, N


def to_robot_pt(s, v, w, p: Params = P, side=1):
    S, Tv, N = axes(p)
    O = (p.inner_x, p.y_apex, p.z_mid)
    q = [O[i] + s * S[i] + v * Tv[i] + w * N[i] for i in range(3)]
    q[0] *= side
    return tuple(q)


def place(shape, p: Params = P, side=1):
    """Module-local -> robot frame; side +1 = right (x > 0), -1 = left (mirror image)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCP.gp import gp_Trsf
    S, Tv, N = axes(p)
    t = gp_Trsf()
    t.SetValues(S[0], Tv[0], N[0], p.inner_x, S[1], Tv[1], N[1], p.y_apex, S[2], Tv[2], N[2], p.z_mid)
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    out = cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped, t, True).Shape())
    return out.mirror('YZ') if side < 0 else out


# ------------------------------------------------------------------------------------------------ holder (module-local)
def _can_cutter(xc):
    """Can hole along module Z with a truncated teardrop toward -s (print up: the part prints upside down)."""
    r, yc = M.can_hole_d / 2, M.pcb_h / 2
    z0, z1 = M.pcb_t - 0.5, M.pcb_t + M.bezel_t + M.boss_h + 0.5
    hole = cyl_z(xc, yc, z0, z1, M.can_hole_d)
    k, tip = r / math.sqrt(2), r * math.sqrt(2)
    tri = (cq.Workplane('XY').polyline([(xc - k, yc - k), (xc - tip, yc), (xc - k, yc + k), (xc, yc)]).close()
           .extrude(z1 - z0).val().translate(cq.Vector(0, 0, z0)))
    tri = tri.cut(box(xc - tip - 1, xc - r - 1.0, -5, M.pcb_h + 5, z0 - 1, z1 + 1))     # flat tip, 1 mm past the circle
    return hole.fuse(tri)


def _boss(bx, by, zf):
    """M2 self-tap boss on the bezel front with a 45 deg wedge toward +s (print down), so it prints without support."""
    r = M.boss_d / 2
    c = cyl_z(bx, by, zf - 0.01, zf + M.boss_h, M.boss_d)
    wedge = (cq.Workplane('XY').polyline([(bx, by - r), (bx + r * math.sqrt(2), by), (bx, by + r)]).close()
             .extrude(M.boss_h + 0.01).val().translate(cq.Vector(0, 0, zf - 0.01)))
    return c.fuse(wedge)


def holder_local(p: Params = P):
    L2 = M.pcb_l / 2
    xe = L2 + M.end_fit + M.lip_t
    zf = M.pcb_t + M.bezel_t
    by = M.pcb_h / 2 + M.hole_dy / 2                             # the two header-edge corner holes
    parts = [
        box(-xe, xe, 0.0, M.pcb_h, M.pcb_t, zf),                                   # bezel
        SB._shelf(M, xe, zf),                                                      # beam along the inner edge
        box(L2 + M.end_fit, xe, -M.shelf_t, M.pcb_h, -M.lip_back, zf),             # top end lip
    ] + [_boss(bx, by, zf) for bx in (-M.hole_dx / 2, M.hole_dx / 2)]
    s = _union(parts)
    # nothing below the PCB bottom end: it is the lowest point of the crab when the Ngủ pose lowers the body
    s = s.cut(box(-xe - 1, -L2 - M.end_fit, -M.shelf_t - 5, M.pcb_h + 5, -M.lip_back - 5, zf + M.boss_h + 5))
    for xc in (M.can_pitch / 2, -M.can_pitch / 2):
        s = s.cut(_can_cutter(xc))
    cw = M.centre_win
    s = s.cut(box(-cw, cw, -0.01, p.win_lo, M.pcb_t - 0.01, zf + 1))               # crystal relief
    s = s.cut(box(-cw, cw, p.win_hi, M.pcb_h + 1, M.pcb_t - 0.01, zf + 1))         # header plastic relief
    for bx in (-M.hole_dx / 2, M.hole_dx / 2):
        s = s.cut(cyl_z(bx, by, -1.0, zf + M.boss_h + 0.5, M.pilot_d))
    return s.clean()


# ------------------------------------------------------------------------------------------------ head (robot frame)
def _hull(pts):
    pts = sorted(set(pts))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def web(p: Params = P):
    """Flat top web: hull of the back plate and the back edge of both top end lips (behind the PCB plane)."""
    L2, xe = M.pcb_l / 2, M.pcb_l / 2 + M.end_fit + M.lip_t
    pts = [(sx * p.plate_x, y) for sx in (1, -1) for y in (p.plate_y0, p.plate_y0 + p.plate_t)]
    for side in (1, -1):
        for s in (L2 + M.end_fit, xe):
            for v in (-M.shelf_t, M.pcb_h):
                q = to_robot_pt(s, v, -M.lip_back, p, side)
                pts.append((round(q[0], 4), round(q[1], 4)))
    poly = _hull(pts)
    return cq.Workplane('XY').polyline(poly).close().extrude(p.web_t).val().translate(cq.Vector(0, 0, p.z_cut - p.web_t))


def tie_slots(p: Params = P):
    """[(label, cutter)]: the zip-tie slots through the plate, just above and just below the rail."""
    return [(f'slot x{x:+.0f} {"upper" if z0 > p.rail_z[0] else "lower"}',
             box(x - p.tie_w / 2, x + p.tie_w / 2, p.plate_y0 - 1, p.plate_y0 + p.plate_t + 1, z0, z0 + p.tie_h))
            for x in p.tie_x for z0 in (p.rail_z[1], p.rail_z[0] - p.tie_h)]


def driver_channels(p: Params = P):
    """[(label, cutter)]: screwdriver channels through the plate to the top screws (bench assembly)."""
    by = M.pcb_h / 2 + M.hole_dy / 2
    return [(f'channel {lab}', place(cyl_z(M.hole_dx / 2, by, -60.0, -M.lip_back - 0.2, p.driver_d), p, side))
            for side, lab in ((1, 'right'), (-1, 'left'))]


def head_robot(p: Params = P):
    validate(p)
    h = holder_local(p)
    hr, hl = place(h, p, 1), place(h, p, -1)
    zb = min(hr.BoundingBox().zmin, hl.BoundingBox().zmin)
    plate = box(-p.plate_x, p.plate_x, p.plate_y0, p.plate_y0 + p.plate_t, p.plate_z0, p.z_cut)
    rib = box(-p.rib_half, p.rib_half, p.plate_y0, p.y_apex - 0.5, zb + 1.0, p.z_cut)
    s = _union([hr, hl, plate, rib, web(p)])
    for _, slot in tie_slots(p):
        s = s.cut(slot)
    for _, c in driver_channels(p):
        s = s.cut(c)
    s = s.cut(box(-80, 80, 0, 120, p.z_cut, p.z_cut + 40))
    return s.clean()


def to_print(shape, p: Params = P):
    """Robot frame -> print orientation: upside down (180 deg about X), top web on the bed, centred."""
    s = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def modules_robot(p: Params = P):
    """Both HC-SR04P reference envelopes in the robot frame: [(label, solid)]."""
    out = []
    for name, s in SB.module_dummy_local(M, 'inplane').items():
        for side, lab in ((1, 'right'), (-1, 'left')):
            out.append((f'HC-SR04P {lab} {name}', place(s, p, side)))
    return out


def beams_robot(p: Params = P):
    """[(label, can-face centre, unit axis)] in the robot frame."""
    S, Tv, N = axes(p)
    out = []
    for side, lab in ((1, 'right'), (-1, 'left')):
        for xc, which in ((M.can_pitch / 2, 'upper'), (-M.can_pitch / 2, 'lower')):
            c = to_robot_pt(xc, M.pcb_h / 2, M.pcb_t + M.can_h, p, side)
            out.append((f'{lab} {which} can', c, (side * N[0], N[1], N[2])))
    return out


def screwdrivers(p: Params = P, length=60.0, d=5.0):
    """[(label, solid)]: a 5 mm screwdriver shaft on each screw axis, from 0.5 mm behind the PCB back, going back."""
    out = []
    by = M.pcb_h / 2 + M.hole_dy / 2
    for side, lab in ((1, 'right'), (-1, 'left')):
        for bx, which in ((M.hole_dx / 2, 'top'), (-M.hole_dx / 2, 'bottom')):
            out.append((f'screwdriver {lab} {which}', place(cyl_z(bx, by, -0.5 - length, -0.5 - 2.0, d), p, side)))
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
    for lab, c, a in beams_robot():
        print(lab, [round(v, 1) for v in c], [round(v, 3) for v in a])

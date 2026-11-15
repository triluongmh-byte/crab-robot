"""Twin HC-SR04P sonar head for the A1V4-r5 open-frame crab: a V of two modules (+-25 deg yaw, 5 deg up) on a mast
that hooks over the walking-front (-X CAD end) upper end bar and is zip-tied to the deck end bar below it.

One printed part, no change to the body. Frames used here:
  * bracket-local: x_l = distance forward of the -X end face (CAD x = -63), y_l = robot left, z = CAD z.
    CAD (robot) frame: X = -63 - x_l, Y = -y_l, Z = z  (rotation 180 deg about Z + shift).
  * module-local (one HC-SR04P): X = s along the PCB (centre 0, inner end -22.5), Y = v up the PCB from its
    bottom edge, Z = w along the face normal (0 = PCB back face, 1.6 = PCB front, 13.6 = transducer face).
  * print: the part upside down, the cut plane through the bezel tops on the bed (z_print = z_cut - z).

gen_step() returns the part in PRINT orientation. robot_frame() / module_dummies_robot() are used by check_fit.py.
Every number lives in Params; GIA DINH (assumed, unmeasured) values are marked.
"""
import math
from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class Params:
    # ---- HC-SR04P module (GIA DINH: common HC-SR04 drawing values, measure yours with calipers)
    pcb_l: float = 45.0          # PCB length
    pcb_h: float = 20.0          # PCB height
    pcb_t: float = 1.6           # PCB thickness
    can_d: float = 16.0          # transducer can diameter
    can_h: float = 12.0          # can height above the PCB front face
    can_pitch: float = 26.0      # can centre spacing
    hole_dx: float = 42.0        # PCB corner-hole centre spacing along the length (GIA DINH, one forum measurement)
    hole_dy: float = 17.0        # ... across the height
    back_comp: float = 3.0       # envelope of the parts on the PCB back (ICs, transducer leads)
    header_w: float = 10.2       # 4-pin 2.54 header, centred on one long edge
    plug_len: float = 18.0       # straight female Dupont housing + bend, beyond the header edge

    # ---- aim
    yaw_deg: float = 25.0        # each module turned this far outwards from straight ahead
    pitch_deg: float = 5.0       # transducer axis tilted up (floor echo, see README)

    # ---- module holder (per module)
    end_fit: float = 0.2         # PCB end clearance to each end lip
    can_hole_d: float = 16.3     # snug on a 16.0 can; PETG holes print slightly small
    bezel_t: float = 2.0         # 5 perimeters at 0.4 mm
    shelf_t: float = 2.0         # beam under the bezel bottom edge
    shelf_back: float = 2.0      # 45 deg chamfer of the beam behind the bezel (shelf_t / shelf_back = 1)
    lip_t: float = 1.8           # end lips that locate the PCB ends
    lip_back: float = 1.2        # end lip reach behind the PCB back face
    centre_win: float = 6.2      # half-width of the open centre (crystal 11.4 wide, header 10.2 wide)
    boss_d: float = 4.6          # M2 self-tap bosses on the bezel front = the module retention (2 per module, header-edge corners)
    boss_h: float = 2.4
    pilot_d: float = 1.6         # M2 self-tapping pilot
    teardrop_floor: float = 0.3  # truncated teardrop tip (v) so the bottom border stays intact

    # ---- head placement (bracket-local)
    apex_x: float = 5.0          # PCB back planes meet at (apex_x, 0)
    apex_gap: float = 2.2        # PCB inner end sits this far off the centre line
    pcb_z0: float = 68.7         # PCB bottom edge height; leg tops reach z 62.7 in every pose
    apex_half: float = 0.8       # half-width of the solid wedge joining the two inner end lips

    # ---- body interface (CAD model.py values, -X end)
    face_x_cad: float = -63.0    # end face of frame_lower / frame_upper
    ubar_z: tuple = (34.4, 39.9)  # frame_upper outer end bar (x -63..-60)
    dbar_z: tuple = (18.5, 21.5)  # frame_lower deck end cross bar (x -63..-60, |y| < 31.3)
    bar_t: float = 3.0

    # ---- base, hook and mast (bracket-local)
    base_depth: float = 9.0
    base_half_w: float = 8.0
    base_z0: float = 13.8
    notch: tuple = ((0.0, 24.7), (0.4, 24.7), (6.5, 30.8), (6.5, 34.0), (0.0, 34.0))  # USB cable / lead channel (XZ),
                                 # 45 deg floor; the 0.4 mm flat keeps 1.6 mm over the upper tie slot
    tie_y: float = 2.4           # tie centre lines (|y|): inside the 11.8 mm gap between the rear hip servos and
                                 # clear of the USB-A plug / adapter envelopes in the rear bay (|y| >= 4)
    tie_w: float = 3.0           # slot for a 2.5 mm wide zip tie
    tie_h: float = 1.6           # slot for a <= 1.3 mm thick tie
    lip_x0: float = -3.2         # hook lip reaches 0.2 past the 3 mm bar, 0.65 short of the servo tabs
    lip_tz: float = 1.6          # hook lip thickness
    lip_half_w: float = 5.5      # hook lip / gusset half-width: inside the servo gap (|y| < 5.9)
    mast_depth: float = 9.0
    mast_half_w: float = 4.0

    @property
    def can_r(self):
        return self.can_hole_d / 2

    @property
    def z_cut(self):
        """Flat print-bed plane through the bezel tops (robot z)."""
        th = math.radians(self.pitch_deg)
        return self.pcb_z0 + self.pcb_h * math.cos(th) + 1.0 * math.sin(th)


P = Params()


def validate(p: Params = P):
    assert p.can_pitch / 2 - p.can_r > 4.0, 'can holes would merge'
    assert p.centre_win < p.can_pitch / 2 - 2.0, 'centre window eats the can rims'
    assert p.centre_win * 2 >= 11.4 + 0.8 and p.centre_win * 2 >= p.header_w + 1.6, 'centre window too narrow for crystal/header'
    assert p.pcb_l / 2 + p.end_fit + p.lip_t <= 24.6, 'lip geometry'
    assert p.tie_y + 1.25 <= 4.0 - 0.3, 'tie would touch the rear-bay USB-A plug / adapter (|y| >= 4) or a hip servo (|y| >= 5.9)'
    assert p.tie_y - p.tie_w / 2 >= 0.8, 'web between the two tie slots < 1.6 mm'
    assert p.lip_half_w < 5.9, 'hook lip would sit beside a servo body'
    assert -p.lip_x0 < p.bar_t + 0.65, 'hook lip would reach the servo tabs'
    assert p.pcb_z0 - p.shelf_t - 0.3 - 62.7 >= 3.0, 'head must stay >= 3 mm above the highest leg point (thigh top z 62.7)'
    assert p.notch[0][1] - (p.dbar_z[1] + p.tie_h) >= 1.6 - 1e-9, 'ledge between the upper tie slot and the channel < 1.6 mm'
    trim = (p.pcb_t + p.bezel_t - 1.0) * math.tan(math.radians(p.pitch_deg))   # bezel lost to the flat print face
    assert p.pcb_h / 2 - p.can_r - trim >= 1.6, 'bezel strip between a can hole and the header edge < 1.6 mm'
    assert p.bezel_t + p.boss_h >= 2 * 2.0, 'M2 self-tap engagement (bezel + boss) < 2 x screw diameter'
    assert p.bezel_t >= 1.6 and p.shelf_t >= 1.6 and p.lip_t >= 1.6 and p.mast_half_w * 2 >= 6, 'min wall 1.6 mm'


# ------------------------------------------------------------------------------------------------ frames
def _vecs(p: Params, sigma=1):
    ps, th = math.radians(sigma * p.yaw_deg), math.radians(p.pitch_deg)
    N = (math.cos(th) * math.cos(ps), math.cos(th) * math.sin(ps), math.sin(th))
    T = (-math.sin(ps), math.cos(ps), 0.0)
    V = (-math.sin(th) * math.cos(ps), -math.sin(th) * math.sin(ps), math.cos(th))
    return T, V, N


def _module_origin(p: Params):
    """Left module (sigma=+1): PCB back face, bottom edge, centre of length."""
    T, V, N = _vecs(p)
    ps = math.radians(p.yaw_deg)
    d_in = p.apex_gap / math.cos(ps)
    return (p.apex_x + (d_in + p.pcb_l / 2) * T[0], (d_in + p.pcb_l / 2) * T[1], p.pcb_z0)


def module_trsf(p: Params = P):
    from OCP.gp import gp_Trsf
    T, V, N = _vecs(p)
    O = _module_origin(p)
    t = gp_Trsf()
    t.SetValues(T[0], V[0], N[0], O[0], T[1], V[1], N[1], O[1], T[2], V[2], N[2], O[2])
    return t


def place_left(shape, p: Params = P):
    """Module-local -> bracket-local for the left module (+y side, faces 25 deg left). Rigid (rotation + shift)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    return cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped, module_trsf(p), True).Shape())


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def cyl_z(x, y, z0, z1, d):
    return cq.Solid.makeCylinder(d / 2, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def _union(items):
    out = items[0]
    for it in items[1:]:
        out = out.fuse(it)
    return out.clean()


def xz_prism(pts, y0, y1):
    """Polygon in the bracket-local XZ plane, extruded from y0 to y1."""
    w = cq.Workplane('XZ').polyline(pts).close().extrude(-(y1 - y0))
    return w.val().translate(cq.Vector(0, y0, 0))


# ------------------------------------------------------------------------------------------------ module holder
def _can_cutter(p: Params, xc):
    """Can hole along module Z with a truncated teardrop tip toward -v (print up, the part prints upside down)."""
    r, yc = p.can_r, p.pcb_h / 2
    z0, z1 = p.pcb_t - 0.5, p.pcb_t + p.bezel_t + p.boss_h + 0.5
    hole = cyl_z(xc, yc, z0, z1, p.can_hole_d)
    k = r / math.sqrt(2)
    tip = r * math.sqrt(2)
    tri = (cq.Workplane('XY').polyline([(xc - k, yc - k), (xc, yc - tip), (xc + k, yc - k), (xc, yc)]).close()
           .extrude(z1 - z0).val().translate(cq.Vector(0, 0, z0)))
    tri = tri.cut(box(xc - r, xc + r, yc - tip - 1, p.teardrop_floor, z0 - 1, z1 + 1))
    return hole.fuse(tri)


def _shelf(p: Params, xe, zf):
    """Beam under the bezel bottom edge, tying the can rings and both end lips together. It grows back from the bezel at 45 deg
    (prints without support upside down); the PCB is located by its cans, so its bottom edge only rests on the front corner line."""
    prof = cq.Workplane('YZ').polyline([(0.0, zf), (0.0, p.pcb_t), (-p.shelf_t, p.pcb_t - p.shelf_back), (-p.shelf_t, zf)]).close()
    return prof.extrude(2 * xe).val().translate(cq.Vector(-xe, 0, 0))


def holder_local(p: Params = P):
    """One module holder in module-local coordinates (X = s, Y = v, Z = w)."""
    L2 = p.pcb_l / 2
    xe = L2 + p.end_fit + p.lip_t                 # outer face of the end lips
    zf = p.pcb_t + p.bezel_t                      # bezel front
    parts = [
        box(-xe, xe, 0.0, p.pcb_h, p.pcb_t, zf),                                   # bezel plate
        _shelf(p, xe, zf),                                                         # ledge under the PCB bottom edge
        box(L2 + p.end_fit, xe, -p.shelf_t, p.pcb_h, -p.lip_back, zf),             # outer end lip
        box(-xe, -L2 - p.end_fit, -p.shelf_t, p.pcb_h, -p.lip_back, zf),           # inner end lip
    ]
    hx, hy = p.hole_dx / 2, p.hole_dy / 2
    yc = p.pcb_h / 2
    bosses = [(sx * hx, yc + hy) for sx in (1, -1)]      # header-edge corners only: they start on the print bed, no support
    for (bx, by) in bosses:
        parts.append(cyl_z(bx, by, zf - 0.01, zf + p.boss_h, p.boss_d))
    s = _union(parts)
    for xc in (p.can_pitch / 2, -p.can_pitch / 2):
        s = s.cut(_can_cutter(p, xc))
    s = s.cut(box(-p.centre_win, p.centre_win, 0.0, p.pcb_h + 1, p.pcb_t - 0.01, zf + p.boss_h + 1))   # crystal + header relief
    for (bx, by) in bosses:
        s = s.cut(cyl_z(bx, by, -1.0, zf + p.boss_h + 0.5, p.pilot_d))
    return s.clean()


# ------------------------------------------------------------------------------------------------ mast + body interface
def _tie_slot(p: Params, y0, y1, zb):
    """Tie slot through the base (along x) with a 45 deg peak under it, so its roof prints without support upside down."""
    yc, hw = (y0 + y1) / 2, (y1 - y0) / 2
    rect = box(-0.1, p.base_depth + 0.1, y0, y1, zb, zb + p.tie_h)
    peak = (cq.Workplane('YZ').polyline([(y0, zb + 0.01), (y1, zb + 0.01), (yc, zb - hw)]).close()
            .extrude(p.base_depth + 0.2).val().translate(cq.Vector(-0.1, 0, 0)))
    return rect.fuse(peak)


def base_and_mast(p: Params = P):
    hw = p.base_half_w
    zt = p.ubar_z[1] + p.lip_tz                    # hook top / base top
    base = xz_prism([(0, p.base_z0), (p.base_depth, p.base_z0), (p.base_depth, zt), (0, zt)], -hw, hw)
    base = base.cut(xz_prism(list(p.notch), -hw - 1, hw + 1).translate(cq.Vector(-0.01, 0, 0)))
    # zip-tie slots: one just over the deck bar top and one just under its bottom, per tie
    for sy in (1, -1):
        y0, y1 = sorted((sy * (p.tie_y - p.tie_w / 2), sy * (p.tie_y + p.tie_w / 2)))
        for zb in (p.dbar_z[1], p.dbar_z[0] - p.tie_h):
            base = base.cut(_tie_slot(p, y0, y1, zb))
    lw = p.lip_half_w
    lip = box(p.lip_x0, 0.01, -lw, lw, p.ubar_z[1], zt)
    gusset = xz_prism([(0.01, zt - 0.01), (p.lip_x0, zt - 0.01), (0.01, zt - p.lip_x0)], -lw, lw)   # 45 deg, prints without support
    mw = p.mast_half_w
    mast_top = p.pcb_z0 - 1.0
    mast = box(0, p.mast_depth, -mw, mw, zt - 0.01, mast_top)
    flare = cq.Workplane('YZ').polyline([(-hw, zt - 0.01), (hw, zt - 0.01), (mw, zt + (hw - mw)), (-mw, zt + (hw - mw))]).close() \
        .extrude(p.mast_depth).val()
    return _union([base, lip, gusset, mast, flare])


def bracket_local(p: Params = P):
    validate(p)
    hl = place_left(holder_local(p), p)
    hr = hl.mirror('XZ')
    zc = p.z_cut
    apex = box(p.apex_x - 2.2, p.apex_x + 4.2, -p.apex_half, p.apex_half, p.pcb_z0 - p.shelf_t - 0.3, zc + 1)
    s = _union([base_and_mast(p), hl, hr, apex])
    s = s.cut(box(-80, 80, -80, 80, zc, zc + 30))          # flat print face through the bezel tops
    return s.clean()


def to_robot(shape):
    """bracket-local -> CAD robot frame (-X walking-front end)."""
    return shape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 180).translate(cq.Vector(P.face_x_cad, 0, 0))


def to_print(shape, p: Params = P):
    """bracket-local -> print orientation: upside down, bezel tops on the bed (z = 0)."""
    s = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180).translate(cq.Vector(0, 0, p.z_cut))
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def robot_frame(p: Params = P):
    return to_robot(bracket_local(p))


# ------------------------------------------------------------------------------------------------ reference module (not printed)
def module_dummy_local(p: Params = P, header='inplane'):
    """HC-SR04P envelope in module-local coords, mounted 'inverted' (header edge at the top, v = pcb_h).
    Returns dict name -> solid: pcb, cans, back parts, header, plug envelope."""
    L2, yc = p.pcb_l / 2, p.pcb_h / 2
    out = {'pcb': box(-L2, L2, 0, p.pcb_h, 0, p.pcb_t)}
    cans = None
    for xc in (p.can_pitch / 2, -p.can_pitch / 2):
        c = cyl_z(xc, yc, p.pcb_t, p.pcb_t + p.can_h, p.can_d)
        cans = c if cans is None else cans.fuse(c)
    out['cans'] = cans
    out['back parts'] = box(-16, 16, 1.5, p.pcb_h - 1.5, -p.back_comp, 0)
    out['crystal'] = box(-5.7, 5.7, 1.0, 5.7, p.pcb_t, p.pcb_t + 3.6)
    hw = p.header_w / 2
    if header == 'inplane':      # right-angle header, plastic on the front at the top edge, pins up in the PCB plane
        out['header'] = box(-hw, hw, p.pcb_h - 2.5, p.pcb_h + 6.0, p.pcb_t, p.pcb_t + 2.54)
        out['dupont plug'] = box(-hw - 1.2, hw + 1.2, p.pcb_h, p.pcb_h + p.plug_len, p.pcb_t - 0.6, p.pcb_t + 3.2)
    else:                        # straight header, pins out of the back
        out['header'] = box(-hw, hw, p.pcb_h - 2.5, p.pcb_h, -8.5, 0)
        out['dupont plug'] = box(-hw - 1.2, hw + 1.2, p.pcb_h - 3.0, p.pcb_h + 0.6, -p.plug_len, -2.5)
    return out


def can_axes_local(p: Params = P):
    """(face centre, unit axis) of the two cans, module-local."""
    return [((xc, p.pcb_h / 2, p.pcb_t + p.can_h), (0, 0, 1)) for xc in (p.can_pitch / 2, -p.can_pitch / 2)]


def _xf(pt, M):
    T, V, N = _vecs(P)
    O = _module_origin(P)
    return tuple(O[i] + pt[0] * T[i] + pt[1] * V[i] + pt[2] * N[i] for i in range(3)) if M == 'pt' else \
        tuple(pt[0] * T[i] + pt[1] * V[i] + pt[2] * N[i] for i in range(3))


def module_dummies_robot(p: Params = P, header='inplane'):
    """Both modules in the robot frame: list of (label, solid)."""
    out = []
    for name, s in module_dummy_local(p, header).items():
        l = place_left(s, p)
        out.append((f'HC-SR04P left {name}', to_robot(l)))
        out.append((f'HC-SR04P right {name}', to_robot(l.mirror('XZ'))))
    return out


def beams_robot(p: Params = P):
    """Each transducer: (label, face centre, unit axis) in the robot frame."""
    out = []
    for i, (c, a) in enumerate(can_axes_local(p)):
        pc, ax = _xf(c, 'pt'), _xf(a, 'dir')
        for side, m in (('left', 1), ('right', -1)):
            q = (pc[0], m * pc[1], pc[2])
            d = (ax[0], m * ax[1], ax[2])
            # bracket-local -> robot: (x, y) -> (-x - 63, -y)
            out.append((f'{side} can {"outer" if i == 0 else "inner"}', (P.face_x_cad - q[0], -q[1], q[2]), (-d[0], -d[1], d[2])))
    return out


def gen_step():
    s = to_print(bracket_local(P))
    return {'shape': s, 'mesh_tolerance': 0.03, 'mesh_angular_tolerance': 2.0}

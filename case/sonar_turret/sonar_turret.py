"""Sonar turret: both HC-SR04P back to back on an SG90 (PCA CH8) that sweeps +-90 deg, so the pair sees 360 deg.

Owner, 2026-11-17: "radar sân bay ... gắn lên cái tháp xoay cho con cua để nó biết chọn đường". After the first
sketch (a bridge over both side rails) the owner asked for a short column glued with 502 (cyanoacrylate) on the orange
frame strip between the LILYGO and the tidied wire bundle. The bundle stands 45 mm over the frame top (owner's
measurement), so the head is lifted until it and the beams pass over it.

Two printed parts, no support:
  * column: glue pad + pedestal + a pocket the SG90 drops into (body on the floor, tabs screwed on the top, cable out
    of a slot at the bottom of the end away from the shaft). Printed pad down.
  * cradle: a disc with a cross recess under it for the SG90 horn (double arm or cross, glued with 502), a base plate,
    a front lip on each side and two end posts with slots that hold both module PCBs back to back, header UP so the
    Dupont plugs and wires leave from the top and loop down with slack. Printed disc down.

Frames:
  * robot (CAD) frame of case/model.py: z up, frame_upper top at z 46.5, floor about z -16; +Y = the owner's front
    (Tiến). The flat centre spine is at z 46.5, x -36..32, y -9.4..9.4 (probed from case/robot/frame_upper.step).
  * Turret angle 0 = front module looking +Y. Front module = GPIO10/11, back module = GPIO12/13.
"""
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'sonar_bracket'))
import sonar_bracket as SB  # noqa: E402  (HC-SR04P numbers, GIA DINH: common drawing values)

M = SB.P


@dataclass(frozen=True)
class Params:
    # body
    frame_top: float = 46.5
    spine_y: float = 9.4
    spine_x: tuple = (-36.0, 32.0)
    column_x: float = 0.0             # column centre on the spine (middle of the body)
    wires_h: float = 45.0             # owner's tidied wire bundle over the frame top (2026-11-17)
    wire_margin: float = 5.0          # rotating head bottom over the bundle
    # column
    pedestal: float = 18.0            # frame top to the pocket floor (pad included)
    wall: float = 2.0                 # pocket side walls (y), 5 perimeters
    fit: float = 0.3                  # SG90 body to pocket, per side
    pad_lip: float = 1.0              # glue pad beyond the column, per side
    pad_t: float = 1.2
    cable_slot: tuple = (6.0, 7.0)    # w x h from the pocket floor, in both end walls
    pilot_d: float = 1.6              # SG90 tab screws (self-tapping, come with the servo)
    chamfer: float = 0.6
    # SG90 (Tower Pro datasheet, nominal)
    sg_body: tuple = (22.8, 12.2, 22.7)
    sg_tab_len: float = 32.3
    sg_tab_z: tuple = (15.9, 18.4)    # tab bottom/top above the body bottom
    sg_hole_pitch: float = 27.8
    sg_shaft_off: float = 5.9         # shaft axis from the body end
    sg_top: float = 29.9              # spline top above the body bottom
    horn_t: float = 1.6               # arm thickness of the bundled horns
    # cradle
    horn_slot: tuple = (37.0, 6.6)    # cross recess, both ways: fits the double-arm or the cross horn
    horn_hub_d: float = 8.5
    recess: float = 1.4               # horn sinks this deep; the rest (0.2) keeps the disc off the arms' ends
    disc_d: float = 26.0
    disc_t: float = 3.2
    plate_t: float = 2.4
    screw_hole_d: float = 6.0         # screwdriver to the horn screw, before the modules go in
    back_gap: float = 3.4             # PCB back face off the centre plane: back parts are <= 3.0 (M.back_comp)
    pcb_fit: float = 0.25             # slot clearance on the PCB thickness, per side
    end_fit: float = 0.2              # PCB end clearance
    grip: float = 1.0                 # slot depth along the PCB: can edges are 1.5 mm from the PCB ends
    post_t: float = 2.2               # end posts beyond the PCB ends
    post_h: float = 15.0              # holds the lower 3/4 of the 20 mm PCB
    front_lip: float = 1.4            # along the PCB bottom, in front; the cans start 2 mm up
    lip_t: float = 1.4
    band_notch: float = 1.2           # rubber-band notch on top of each post
    # beam (drawing / checks only)
    beam_half: float = 15.0


P = Params()


def validate(p: Params = P):
    L, W, H = p.sg_body
    col_x = p.sg_tab_len + 2 * p.pad_lip
    assert p.column_x - col_x / 2 >= p.spine_x[0] and p.column_x + col_x / 2 <= p.spine_x[1], 'column off the spine'
    assert W / 2 + p.fit + p.wall + p.pad_lip <= p.spine_y, 'pad wider than the spine'
    assert head_bottom(p) >= p.frame_top + p.wires_h + p.wire_margin, 'head would sweep through the wire bundle'
    assert p.grip + p.end_fit <= (M.pcb_l - M.can_pitch - M.can_d) / 2, 'slot lip would reach a can'
    assert p.back_gap >= M.back_comp + 0.3, 'module back parts touch'
    assert p.front_lip < (M.pcb_h - M.can_d) / 2, 'front lip would reach a can'


# ------------------------------------------------------------------------------------------------ positions
def axis_x(p=P):
    """Turret axis: over the SG90 shaft. The column is centred on column_x; the body sits off-centre in the pocket."""
    return p.column_x + p.sg_body[0] / 2 - p.sg_shaft_off


def servo_bottom(p=P):
    return p.frame_top + p.pedestal


def horn_top(p=P):
    return servo_bottom(p) + p.sg_top + p.horn_t


def disc_bottom(p=P):
    return horn_top(p) - p.recess


def plate_top(p=P):
    return disc_bottom(p) + p.disc_t + p.plate_t


def head_bottom(p=P):
    """Lowest point of the part of the head that reaches beyond the column top (the base plate)."""
    return disc_bottom(p) + p.disc_t


def can_z(p=P):
    return plate_top(p) + M.pcb_h / 2


# ------------------------------------------------------------------------------------------------ parts (robot frame)
def column(p=P):
    L, W, _ = p.sg_body
    z0 = p.frame_top
    top = servo_bottom(p) + p.sg_tab_z[0]
    ox, oy = p.sg_tab_len, W + 2 * (p.fit + p.wall)
    cx = p.column_x
    pad = cq.Workplane().box(ox + 2 * p.pad_lip, oy + 2 * p.pad_lip, p.pad_t, centered=(True, True, False)).translate((cx, 0, z0))
    body = cq.Workplane().box(ox, oy, top - z0, centered=(True, True, False)).translate((cx, 0, z0))
    body = body.edges('|Z').chamfer(p.chamfer)
    col = pad.union(body)
    # pocket: the body is off-centre so the tab holes line up with the column ends
    bx = cx  # SG90 tabs are symmetric about the body centre
    col = col.cut(cq.Workplane().box(L + 2 * p.fit, W + 2 * p.fit, 60, centered=(True, True, False)).translate((bx, 0, servo_bottom(p))))
    sw, sh = p.cable_slot
    for e in (1, -1):   # both ends: the cable leaves whichever end your SG90 has it on
        col = col.cut(cq.Workplane().box(10, sw, sh, centered=(True, True, False)).translate((bx + e * (L / 2 + 3), 0, servo_bottom(p))))
    for s in (1, -1):
        col = col.cut(cq.Workplane().circle(p.pilot_d / 2).extrude(8).translate((bx + s * p.sg_hole_pitch / 2, 0, top - 8)))
    # a 1 mm chamfer on the pocket mouth helps the body drop in
    return col


def sg90(p=P):
    L, W, H = p.sg_body
    z_bot = servo_bottom(p)
    body = cq.Workplane().box(L, W, H, centered=(True, True, False)).translate((p.column_x, 0, z_bot))
    tabs = cq.Workplane().box(p.sg_tab_len, W, p.sg_tab_z[1] - p.sg_tab_z[0], centered=(True, True, False)).translate((p.column_x, 0, z_bot + p.sg_tab_z[0]))
    ax = axis_x(p)
    dome = cq.Workplane().circle(W / 2).extrude(p.sg_top - H - 1.5).translate((ax, 0, z_bot + H))
    spline = cq.Workplane().circle(2.4).extrude(1.5).translate((ax, 0, z_bot + p.sg_top - 1.5))
    horn = (cq.Workplane().box(34.0, 5.5, p.horn_t, centered=(True, True, False))
            .union(cq.Workplane().box(5.5, 34.0, p.horn_t, centered=(True, True, False)))
            .union(cq.Workplane().circle(3.6).extrude(p.horn_t))).translate((ax, 0, z_bot + p.sg_top))
    return body.union(tabs).union(dome).union(spline), horn


def cradle(p=P, angle=0.0):
    ax = axis_x(p)
    z0 = disc_bottom(p)
    disc = cq.Workplane().circle(p.disc_d / 2).extrude(p.disc_t).translate((ax, 0, z0))
    half_x = M.pcb_l / 2 + p.end_fit + p.post_t
    yb, yf = p.back_gap, p.back_gap + M.pcb_t
    half_y = yf + p.pcb_fit + p.lip_t
    zp = z0 + p.disc_t
    plate = cq.Workplane().box(2 * half_x, 2 * half_y, p.plate_t, centered=(True, True, False)).translate((ax, 0, zp))
    body = disc.union(plate)
    zt = zp + p.plate_t
    for s in (1, -1):
        lip = cq.Workplane().box(2 * half_x, p.lip_t, p.front_lip, centered=(True, True, False)).translate((ax, s * (half_y - p.lip_t / 2), zt))
        body = body.union(lip)
    for e in (1, -1):
        post = cq.Workplane().box(p.post_t + p.grip + p.end_fit, 2 * half_y, p.post_h, centered=(True, True, False)).translate(
            (ax + e * (half_x - (p.post_t + p.grip + p.end_fit) / 2), 0, zt))
        body = body.union(post)
        for s in (1, -1):   # PCB slots
            slot = cq.Workplane().box(p.grip + p.end_fit, M.pcb_t + 2 * p.pcb_fit, 40, centered=(True, True, False)).translate(
                (ax + e * (M.pcb_l / 2 + p.end_fit - (p.grip + p.end_fit) / 2), s * (yb + M.pcb_t / 2), zt))
            body = body.cut(slot)
        notch = cq.Workplane().box(p.post_t + 2, 2 * half_y + 2, p.band_notch, centered=(True, True, False)).translate(
            (ax + e * (half_x - p.post_t / 2), 0, zt + p.post_h - 3.0))
        body = body.cut(notch.cut(cq.Workplane().box(p.post_t + 2, 2 * half_y - 2 * 0.8, 10, centered=(True, True, True)).translate(
            (ax + e * (half_x - p.post_t / 2), 0, zt + p.post_h - 3.0))))
    # horn recess (cross) + hub, and the screwdriver hole
    rx, ry = p.horn_slot
    rec = (cq.Workplane().box(rx, ry, p.recess, centered=(True, True, False))
           .union(cq.Workplane().box(ry, rx, p.recess, centered=(True, True, False)))
           .union(cq.Workplane().circle(p.horn_hub_d / 2).extrude(p.recess))).translate((ax, 0, z0))
    body = body.cut(rec)
    body = body.cut(cq.Workplane().circle(p.screw_hole_d / 2).extrude(40).translate((ax, 0, z0)))
    return body.rotate((ax, 0, 0), (ax, 0, 1), angle)


def modules(p=P, angle=0.0):
    """Module dummies (PCB + cans + header + plugs) and beams. Returns [(name, solid)], [(name, apex, axis)]."""
    ax = axis_x(p)
    zt = plate_top(p)
    out, beams = [], []
    for s, lab in ((1, 'front GPIO10/11'), (-1, 'back GPIO12/13')):
        y0 = s * p.back_gap
        pcb = cq.Workplane().box(M.pcb_l, M.pcb_t, M.pcb_h, centered=(True, False, False)).translate((ax, 0 if s > 0 else -M.pcb_t, zt))
        pcb = pcb.translate((0, y0, 0))
        yf = s * (p.back_gap + M.pcb_t)
        cans = None
        for dx in (-M.can_pitch / 2, M.can_pitch / 2):
            c = cq.Workplane('XZ').circle(M.can_d / 2).extrude(-s * M.can_h).translate((ax + dx, yf, can_z(p)))
            cans = c if cans is None else cans.union(c)
        hdr = cq.Workplane().box(M.header_w, 2.5, 8.5, centered=(True, True, False)).translate((ax, s * (p.back_gap + M.pcb_t / 2), zt + M.pcb_h))
        plug = cq.Workplane().box(M.header_w, 2.6, 14.0, centered=(True, True, False)).translate((ax, s * (p.back_gap + M.pcb_t / 2), zt + M.pcb_h + 2.5))
        rot = lambda w: w.rotate((ax, 0, 0), (ax, 0, 1), angle).val()  # noqa: E731
        out += [(f'HC-SR04P {lab}', rot(pcb.union(cans).union(hdr))), (f'Dupont plugs {lab}', rot(plug))]
        a = math.radians(angle)
        dirv = (-s * math.sin(a), s * math.cos(a), 0.0)
        r = s * (p.back_gap + M.pcb_t + M.can_h)
        apex = (ax - r * math.sin(a), r * math.cos(a), can_z(p))
        beams.append((lab, apex, dirv))
    return out, beams


# ------------------------------------------------------------------------------------------------ print orientation
def column_print(p=P):
    return column(p).translate((-p.column_x, 0, -p.frame_top))


def cradle_print(p=P):
    return cradle(p).translate((-axis_x(p), 0, -disc_bottom(p)))


def gen_step():
    validate()
    a = cq.Assembly(name='sonar_turret_print')
    a.add(column_print(), name='column', color=cq.Color(0.9, 0.15, 0.1))
    a.add(cradle_print().translate((0, 30, 0)), name='cradle', color=cq.Color(0.9, 0.15, 0.1))
    return a


if __name__ == '__main__':
    validate()
    print(f'axis x {axis_x():.2f}; pocket floor z {servo_bottom():.1f}; head bottom z {head_bottom():.1f} '
          f'(+{head_bottom() - P.frame_top:.1f} over the frame, bundle {P.wires_h}); can centres z {can_z():.1f} '
          f'= {can_z() - P.frame_top:.1f} over the frame top, {can_z() + 16:.0f} over the floor')

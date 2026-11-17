"""Screen stand: holds the bare LILYGO T-Display-S3 board upright on the frame_upper display rim.

Robot frame of the case model: +X is the old bank mouth end, +Y left, z0 at the frame_lower bottom.
The owner's front is +Y (2026-11-16, marked on a render): the stand snaps over the outer wall of the raised
display rim on the +Y side (y 33.46..37.02, z 43.5..46.52, x -46.5..11.5) and holds the screen in landscape,
facing +Y and leaning back `tilt` degrees.

Geometry is built in a mount-local frame (bar along local Y, outward local +X) and turned onto the robot by
`mount()`: local +X -> robot +Y, local +Y -> robot -X, then shifted to x = cx. The case is gripped only at its two
short ends, so both header rows and their Dupont housings on the back stay free, and both end faces
(USB-C, buttons) are open. A rubber band over the two back posts keeps it from lifting out.

Print: standing on a flat end face with tree supports (see make_3mf.py).
"""
import math
from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class Params:
    # Bare LILYGO T-Display-S3, no shell: owner's ruler 56 x 26 x 7 (2026-11-17). Matches the vendor STEP body
    # (56.2 x 25.5 without the USB-C overhang).
    case_l: float = 56.0          # along Y (landscape)
    case_h: float = 26.0          # screen height
    case_t: float = 7.0           # thickness front glass to back of board (pins excluded)
    fit_t: float = 1.0            # total clearance across the thickness (ruler reading, so generous)
    fit_l: float = 1.0            # total clearance along the length
    tilt: float = 15.0            # lean back, degrees
    wall: float = 2.0
    # frame_upper +Y display rim outer wall, in the mount-local frame (measured from case/robot/frame_upper.step)
    bar_x: tuple = (33.46, 37.02)
    bar_z: tuple = (43.5, 46.52)
    cx: float = -10.0             # robot x of the screen centre (rim spans x -46.5..11.5)
    # rim posts under the wall (robot x); the snap tabs must stay off them
    posts_x: tuple = ((-46.0, -39.98), (-1.0, 5.02))
    gap: float = 0.2              # clip clearance to the rim wall
    leg_t: float = 1.8            # inner clip leg
    barb: float = 0.5             # snap barb under the rim wall
    tab_w: float = 9.0            # flexing barb tabs
    tab_y: tuple = (-2.0, 18.0)   # mount-local; robot x = cx - y -> -8 and -28
    # cradle placement: local origin = front-bottom edge of the screen, at x0, z0
    x0: float = 34.3              # front-bottom of the cradle flush with the rim outer face
    z0: float = 54.5              # end shelves clear the rim corner wall (top z 46.52) and the -X hip servo
    shelf_t: float = 3.0          # under the case
    beam_back: float = 5.0        # how far the full-length beam reaches behind the front face
    lip_l: float = 2.0            # front/back lips overlap of the board ends (vendor STEP: back parts start 2.1 in)
    back_lip_w: tuple = (7.0, 19.0)   # back lip height band: clear of both header rows (long edges)
    post_over: float = 3.0        # back posts stand above the case top for the band
    band_notch: float = 1.6
    window_margin: float = 0.3    # end window inset from the board faces (7 mm USB-C overmould must pass)


P = Params()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def mount(w: cq.Workplane, p: Params = P) -> cq.Workplane:
    """Mount-local -> robot frame."""
    return w.rotate((0, 0, 0), (0, 0, 1), 90).translate((p.cx, 0, 0))


def place(w: cq.Workplane, p: Params = P) -> cq.Workplane:
    """Cradle-local (u out of the screen, v along it, w up the screen) -> robot frame."""
    return w.rotate((0, 0, 0), (0, 1, 0), -p.tilt).translate((p.x0, 0, p.z0))


def to_robot(u, w, p: Params = P):
    a = math.radians(p.tilt)
    return p.x0 + u * math.cos(a) - w * math.sin(a), p.z0 + u * math.sin(a) + w * math.cos(a)


def slot_t(p: Params = P):
    return p.case_t + p.fit_t


def half_l(p: Params = P):
    return (p.case_l + p.fit_l) / 2


def cradle(p: Params = P) -> cq.Workplane:
    t, hl, W = slot_t(p), half_l(p), p.wall
    ub = -t - W                                      # back of the back posts
    out = box(-p.beam_back, W, -hl - W, hl + W, -p.shelf_t, 0)          # full-length beam under the front
    for s in (1, -1):
        def yb(a, b):
            return (min(s * a, s * b), max(s * a, s * b))
        y_in, y_end = yb(hl - p.lip_l, hl), yb(hl, hl + W)
        y_all = yb(hl - p.lip_l, hl + W)
        out = out.union(box(ub, W, *y_all, -p.shelf_t, 0))                                    # end shelf
        out = out.union(box(ub, W, *y_end, 0, p.case_h + p.post_over))                        # end wall
        out = out.union(box(0, W, *y_in, 0, p.case_h - 2))                                    # front lip
        out = out.union(box(ub, -t, *y_in, *p.back_lip_w))                                    # back lip
        out = out.union(box(ub, -t, *y_end, 0, p.case_h + p.post_over))                       # back post
        # end window: USB-C plug / buttons, open to the top
        out = out.cut(box(-t + p.window_margin, -p.window_margin, *(yb(hl - 0.1, hl + W + 1)), 3.0, p.case_h + 10))
        # rubber-band notch across the top of the back post
        out = out.cut(box(ub - 1, -t + 0.01, *(yb(hl + W / 2 - p.band_notch / 2, hl + W / 2 + p.band_notch / 2)),
                          p.case_h + p.post_over - p.band_notch, p.case_h + p.post_over + 1))
    return out


def clip(p: Params = P) -> cq.Workplane:
    hl, W = half_l(p), p.wall
    ylen = (-hl - W, hl + W)
    xi = p.bar_x[0] - p.gap - p.leg_t
    cap_z = p.bar_z[1] + p.gap
    # cap + riser up into the cradle beam; the outer face stays flush with the rim wall
    _, zb = to_robot(W, -p.shelf_t, p)
    xr, zr = to_robot(-p.beam_back, -p.shelf_t, p)
    out = box(xi, p.bar_x[1], *ylen, cap_z, max(zb, zr) + 1.0)
    # two snap tabs down the inner face of the rim wall, placed off the rim posts (validate);
    # no full-length leg, so the posts under the wall stay clear
    for y in p.tab_y:
        out = out.union(box(xi, p.bar_x[0] - p.gap, y - p.tab_w / 2, y + p.tab_w / 2, p.bar_z[0] - 1.2, cap_z))
        prof = [(p.bar_x[0] - p.gap - 0.01, p.bar_z[0] - p.gap), (p.bar_x[0] + p.barb, p.bar_z[0] - p.gap),
                (p.bar_x[0] - p.gap - 0.01, p.bar_z[0] - 1.2)]
        out = out.union(cq.Workplane('XZ').polyline(prof).close().extrude(p.tab_w / 2).translate((0, y, 0))
                        .union(cq.Workplane('XZ').polyline(prof).close().extrude(-p.tab_w / 2).translate((0, y, 0))))
    return out


def stand_local(p: Params = P) -> cq.Workplane:
    """The stand in its mount-local frame (flat end faces normal to local Y), used for print orientation."""
    validate(p)
    return clip(p).union(place(cradle(p), p))


def stand(p: Params = P) -> cq.Workplane:
    return mount(stand_local(p), p)


def screen_envelope(p: Params = P) -> cq.Workplane:
    """The board in its slot (nominal size), robot frame."""
    t = p.case_t
    return mount(place(box(-p.fit_t / 2 - t, -p.fit_t / 2, -p.case_l / 2, p.case_l / 2, 0.0, p.case_h), p), p)


def plug_envelopes(p: Params = P):
    """USB-C plug path at either end (GIA DINH: overmould 12.5 along the height x 7 thick, 25 long)."""
    t = slot_t(p)
    out = []
    for s in (1, -1):
        y0 = s * (p.case_l / 2)
        y1 = s * (p.case_l / 2 + 25)
        out.append(mount(place(box(-t / 2 - 3.5, -t / 2 + 3.5, min(y0, y1), max(y0, y1), p.case_h / 2 - 6.25, p.case_h / 2 + 6.25), p), p))
    return out


def header_envelopes(p: Params = P):
    """Dupont housings on both header rows (GIA DINH: rows 2.5 mm in from each long edge, housings 2.5 wide
    and 14 long straight out of the back, along the case length minus 3 mm at each end)."""
    t = slot_t(p)
    return [mount(place(box(-t - 14.0, -t, -p.case_l / 2 + 3, p.case_l / 2 - 3, wc - 1.25, wc + 1.25), p), p)
            for wc in (2.5, p.case_h - 2.5)]


def validate(p: Params = P):
    t = slot_t(p)
    assert p.back_lip_w[0] >= 5.0 and p.back_lip_w[1] <= p.case_h - 5.0, 'back lip reaches a header row'
    assert -t + p.window_margin < -p.window_margin - 5, 'end window too narrow for a USB-C plug'
    fx, fz = to_robot(p.wall, -p.shelf_t, p)
    assert fx <= p.bar_x[1] + 0.05, f'cradle front {fx:.2f} past the rim face'
    for y in p.tab_y:
        x0, x1 = p.cx - y - p.tab_w / 2, p.cx - y + p.tab_w / 2
        assert -46.5 + 0.5 <= x0 and x1 <= 11.5 - 0.5, 'snap tab off the rim wall'
        for a, b in p.posts_x:
            assert x1 <= a - 0.5 or x0 >= b + 0.5, 'snap tab on a rim post'
    assert p.leg_t >= 1.6 and p.barb <= 0.6, 'snap tab too stiff / barb too deep for PETG'


def gen_step():
    return stand(P)


if __name__ == '__main__':
    s = stand(P).val()
    bb = s.BoundingBox()
    print('ok', s.isValid(), round(s.Volume(), 1), [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)])
    print('front-bottom', [round(v, 2) for v in to_robot(P.wall, -P.shelf_t)], 'back-bottom', [round(v, 2) for v in to_robot(-slot_t() - P.wall, -P.shelf_t)])

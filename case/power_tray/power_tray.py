"""Drop-in power tray for the A1V4-r5 frame_lower bay, plus a zip-tie switch holder.

The tray rests on frame_lower's floor bars (top z = 3) between the two inner deck
bars, so neither frame is reprinted and the ground clearance does not change.
It holds, in robot-frame mm (+X = old bank mouth = walking rear, +Y left):
  - the 1x18650 holder along X near the centreline (two zip ties),
  - the 1S charge/boost module with its USB-C facing +X out of the old bank mouth
    (snug 3-wall pocket, double-sided tape),
  - the LILYGO's 3.7 V LiPo standing on edge (one zip tie).
The switch is not in the tray: it goes on the separate switch holder, which
zip-ties flat against any 3 mm frame bar where the owner wants it.

Owner measurements (2026-11-16, ruler, not calipers): holder 79 x 21 x 25,
module 25 x 20 x 25, switch body 20 x 14 x 22, LiPo 30 x 26 x 8. The capacitor
sits on the PCA screw terminal and needs no mount.
"""
from dataclasses import dataclass

import cadquery as cq


@dataclass(frozen=True)
class Params:
    # ---- bought parts (owner, ruler; GIA DINH where marked)
    holder: tuple = (79.0, 21.0, 25.0)      # 18650 holder L (X) x W (Y) x H
    module: tuple = (25.0, 20.0, 25.0)      # charge/boost module L (X) x W (Y) x H; USB-C on the +X end (GIA DINH)
    lipo: tuple = (30.0, 8.0, 26.0)         # LiPo 30 x 26 x 8 standing on edge: L (X) x thickness (Y) x H
    switch: tuple = (20.0, 14.0, 22.0)      # switch body through the panel: W x H, depth behind it
    # ---- fits (FDM, hand assembly)
    fit: float = 0.6                         # total clearance per pocket dimension (0.3 per side)
    switch_fit: float = 0.3                  # total clearance on the snap-in switch cut-out
    # ---- tray
    floor_z: float = 3.0                     # top of frame_lower's floor bars
    floor_t: float = 2.4                     # 1.0 mm left over the under-side tie grooves
    wall: float = 1.6                        # 4 perimeters at 0.4 mm
    holder_y0: float = -19.0                 # holder pocket -Y edge
    holder_wall_h: float = 10.0
    plus_wall_y0: float = 7.0                # first wall of the +Y band (holder side)
    module_x0: float = 6.4                   # module pocket -X edge (its +X end stays open)
    module_wall_h: float = 6.0
    lipo_x0: float = -31.5
    lipo_wall_h: float = 12.0
    band_x: float = 33.5                     # |x| of the main plate (seats at |x| >= 34 above the deck)
    end_x: float = 41.8                      # |x| of the holder end walls (inner deck bars at |x| 42..46)
    plate_y: tuple = (-24.3, 30.9)           # main plate Y span (deck rails from |y| 31.3)
    # ---- zip ties (2.5 mm ties)
    tie_w: float = 4.0                       # slot length along the tie width
    tie_t: float = 2.0                       # slot width across the tie
    groove_d: float = 1.4                    # under-side groove depth where a tie runs under the plate
    groove_w: float = 5.4                    # groove width at the bed; 45 deg sides leave 2.6 at the top
    holder_tie_x: tuple = (-12.0, 12.0)
    lipo_tie_x: float = -21.5
    tiedown_x: float = 5.5                   # tray-to-frame ties straddle the floor bar at x 0 (7 wide)
    tiedown_slot_y: float = 2.8              # slot length along Y for a 2.5 mm tie
    wire_notch: tuple = (6.0, 5.0)           # W x depth of the wire notches at the top of the holder end walls
    # ---- switch holder (separate part)
    sw_plate: tuple = (40.0, 24.0, 2.0)      # X x Y x thickness; rocker snaps behind a 1.5-2 mm panel
    sw_tie_x: float = 15.5                   # tie slots this far each side of the cut-out centre


P = Params()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


# ------------------------------------------------------------------------------- derived layout
def pockets(p: Params = P):
    """Inner pocket boxes (x0, x1, y0, y1) for holder, module and LiPo."""
    hl, hw, _ = p.holder
    ml, mw, _ = p.module
    ll, lt, _ = p.lipo
    h = (-(hl + p.fit) / 2, (hl + p.fit) / 2, p.holder_y0, p.holder_y0 + hw + p.fit)
    y = p.plus_wall_y0 + p.wall
    m = (p.module_x0, p.module_x0 + ml + p.fit, y, y + mw + p.fit)
    l = (p.lipo_x0, p.lipo_x0 + ll + p.fit, y, y + lt + p.fit)
    return {'holder': h, 'module': m, 'lipo': l}


def tie_paths(p: Params = P):
    """Each tie: x centre, slot y centres (two), and the under-side groove y span."""
    h = pockets(p)['holder']
    l = pockets(p)['lipo']
    s_minus = h[2] - p.wall - p.tie_t / 2 - 0.5          # outside the holder -Y wall
    s_gap = (h[3] + p.wall + p.plus_wall_y0) / 2          # strip between the holder and the +Y band walls
    s_lipo = l[3] + p.wall + p.tie_t / 2 + 0.5            # outside the LiPo +Y wall
    out = [(x, (s_minus, s_gap)) for x in p.holder_tie_x]
    out.append((p.lipo_tie_x, (s_gap, s_lipo)))
    return out


def tiedown_slots(p: Params = P):
    """Two ties hold the tray to frame_lower: each goes down one slot, under the floor bar at x 0, up the other."""
    h = pockets(p)['holder']
    ys = (h[2] - p.wall - p.tie_t / 2 - 0.5 - 0.2, (h[3] + p.wall + p.plus_wall_y0) / 2)
    return [(sx * p.tiedown_x, y) for y in ys for sx in (1, -1)]


def validate(p: Params = P):
    pk = pockets(p)
    h, m, l = pk['holder'], pk['module'], pk['lipo']
    assert p.end_x - p.wall >= h[1] - 0.01, 'holder longer than the end walls allow'
    assert p.end_x <= 41.9, 'end walls would hit the inner deck bars (|x| 42..46)'
    assert h[3] + p.wall <= p.plus_wall_y0 - p.tie_t - 0.2, 'no room for the tie slots between holder and +Y band'
    assert l[1] + p.wall <= m[0] - p.wall + 0.01, 'LiPo and module pockets overlap'
    assert m[1] <= p.band_x - 0.5, 'module pocket runs past the plate'
    assert m[3] + p.wall <= p.plate_y[1] + 0.01 and p.plate_y[1] <= 31.0, '+Y wall past the plate / deck rail line'
    for x, (ya, yb) in tie_paths(p):
        assert p.plate_y[0] + 0.5 <= ya - p.tie_t / 2 and yb + p.tie_t / 2 <= p.plate_y[1] - 0.5, f'tie at x {x} off the plate'
        for bar in (0.0, 28.0, -28.0):                    # the slot must not sit on a floor bar (7 wide)
            assert abs(x - bar) >= 3.5 + p.tie_w / 2 + 0.3, f'tie slot at x {x} sits on the floor bar at {bar}'
    assert p.floor_t - p.groove_d >= 0.8, 'floor too thin over the tie grooves'
    assert p.tiedown_x - p.tie_t / 2 >= 3.5 + 0.5, 'tie-down slot over the floor bar at x 0'
    assert h[3] + p.wall <= p.plus_wall_y0 - p.tiedown_slot_y + 0.01, 'tie-down slot does not fit between holder and +Y band'
    for x, y in tiedown_slots(p):
        assert y - p.tiedown_slot_y / 2 >= p.plate_y[0] + 0.25, 'tie-down slot off the plate'
        for tx, _ in tie_paths(p):
            assert abs(x - tx) >= p.tie_t / 2 + p.tie_w / 2 + 1.0, 'tie-down slot runs into a holder tie slot'
    assert p.groove_w - 2 * p.groove_d >= 2.5, 'groove top narrower than a 2.5 mm tie'
    assert p.groove_w / 2 <= 3.5 + min(abs(x) for x in p.holder_tie_x) - 0.0, 'groove reaches the floor bar slot rule'
    sw, sh, _ = p.switch
    assert p.sw_plate[0] >= sw + 2 * (p.tie_w + 3), 'switch plate too short for the tie slots'
    assert p.sw_tie_x - p.tie_t / 2 >= (sw + p.switch_fit) / 2 + 2.0, 'tie slots too close to the switch cut-out'


# ------------------------------------------------------------------------------- tray (robot frame)
def plate(p: Params = P):
    z0, z1 = p.floor_z, p.floor_z + p.floor_t
    h = pockets(p)['holder']
    s = box(-p.band_x, p.band_x, p.plate_y[0], p.plate_y[1], z0, z1)
    # end extensions under the holder ends, inside the free shaft at |x| 33.5..42
    s = s.union(box(-p.end_x, p.end_x, h[2] - p.wall, h[3] + p.wall, z0, z1))
    return s


def holder_cradle(p: Params = P):
    h = pockets(p)['holder']
    z0, z1 = p.floor_z + p.floor_t - 0.01, p.floor_z + p.floor_t + p.holder_wall_h
    out = []
    for y0, y1 in ((h[2] - p.wall, h[2]), (h[3], h[3] + p.wall)):
        out.append(box(-p.end_x, p.end_x, y0, y1, z0, z1))
    for sx in (1, -1):
        x0, x1 = sorted((sx * h[1], sx * p.end_x))
        wall = box(x0, x1, h[2] - p.wall, h[3] + p.wall, z0, z1)
        nw, nd = p.wire_notch
        yc = (h[2] + h[3]) / 2
        out.append(wall.cut(box(x0 - 1, x1 + 1, yc - nw / 2, yc + nw / 2, z1 - nd, z1 + 1)))
    return out


def module_pocket(p: Params = P):
    m = pockets(p)['module']
    z0, z1 = p.floor_z + p.floor_t - 0.01, p.floor_z + p.floor_t + p.module_wall_h
    return [box(m[0], m[1], m[2] - p.wall, m[2], z0, z1),          # -Y wall (shared band wall)
            box(m[0], m[1], m[3], m[3] + p.wall, z0, z1),          # +Y wall
            box(m[0] - p.wall, m[0], m[2] - p.wall, m[3] + p.wall, z0, z1)]   # -X wall; +X open for the USB-C plug


def lipo_pocket(p: Params = P):
    l = pockets(p)['lipo']
    z0, z1 = p.floor_z + p.floor_t - 0.01, p.floor_z + p.floor_t + p.lipo_wall_h
    return [box(l[0] - p.wall, l[1] + p.wall, l[2] - p.wall, l[2], z0, z1),
            box(l[0] - p.wall, l[1] + p.wall, l[3], l[3] + p.wall, z0, z1),
            box(l[0] - p.wall, l[0], l[2], l[3], z0, z1),
            box(l[1], l[1] + p.wall, l[2], l[3], z0, z1)]


def tie_cuts(p: Params = P):
    z0, z1 = p.floor_z, p.floor_z + p.floor_t
    out = []
    for x, (ya, yb) in tie_paths(p):
        for yc in (ya, yb):
            out.append(box(x - p.tie_w / 2, x + p.tie_w / 2, yc - p.tie_t / 2, yc + p.tie_t / 2, z0 - 1, z1 + 1))
        # the tie runs under the plate between its slots, across floor bars and the X brace: a 45 deg
        # trapezoid groove (prints without support), wide enough for a 2.5 x 1.2 tie at full depth
        hb = p.groove_w / 2
        prof = [(x - hb - 1, z0 - 1), (x + hb + 1, z0 - 1), (x + hb, z0), (x + hb - p.groove_d, z0 + p.groove_d),
                (x - hb + p.groove_d, z0 + p.groove_d), (x - hb, z0)]
        y0, y1 = ya - p.tie_t / 2, yb + p.tie_t / 2
        out.append(cq.Workplane('XZ').polyline(prof).close().extrude(-(y1 - y0)).translate((0, y0, 0)))
    for x, y in tiedown_slots(p):
        out.append(box(x - p.tie_t / 2, x + p.tie_t / 2, y - p.tiedown_slot_y / 2, y + p.tiedown_slot_y / 2, z0 - 1, z1 + 1))
    return out


def tray(p: Params = P):
    validate(p)
    s = plate(p)
    for part in holder_cradle(p) + module_pocket(p) + lipo_pocket(p):
        s = s.union(part)
    for c in tie_cuts(p):
        s = s.cut(c)
    return s.clean()


def components(p: Params = P):
    """Bought-part envelopes in the robot frame, seated in their pockets (for the fit check and preview)."""
    pk = pockets(p)
    zb = p.floor_z + p.floor_t
    out = []
    for name, dims in (('holder', p.holder), ('module', p.module), ('lipo', p.lipo)):
        x0, x1, y0, y1 = pk[name]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        L, W, H = dims
        out.append((name, box(cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, zb, zb + H)))
    return out


# ------------------------------------------------------------------------------- switch holder (print frame)
def switch_holder(p: Params = P):
    validate(p)
    X, Y, T = p.sw_plate
    sw, sh, _ = p.switch
    s = cq.Workplane('XY').box(X, Y, T, centered=(True, True, False)).edges('|Z').fillet(3.0)
    s = s.cut(box(-(sw + p.switch_fit) / 2, (sw + p.switch_fit) / 2, -(sh + p.switch_fit) / 2, (sh + p.switch_fit) / 2, -1, T + 1))
    for sx in (1, -1):
        for sy in (1, -1):
            yc = sy * (Y / 2 - 5.0)
            s = s.cut(box(sx * p.sw_tie_x - p.tie_t / 2, sx * p.sw_tie_x + p.tie_t / 2, yc - p.tie_w / 2, yc + p.tie_w / 2, -1, T + 1))
    return s.clean()


def gen_step():
    """The tray, in print orientation (= robot orientation, floor on the bed)."""
    return tray(P).translate((0, 0, -P.floor_z))


if __name__ == '__main__':
    validate(P)
    print('ok')

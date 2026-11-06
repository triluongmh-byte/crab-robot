"""Crab robot A1 V4 - case geometry in the sealed contract body frame (mm).

+X front, +Y left, +Z up; origin = centre of the 126 x 75 body footprint, z=0 under the bottom.
Every solid is built ASSEMBLED in this frame. Print rotations live in PARTS[...]['printRotateDeg'].
"""
import math
import cadquery as cq

# ---------------------------------------------------------------- contract numbers
BODY_X, BODY_Y, BODY_Z = 126.0, 75.0, 47.0
HX, HY = 63.0, 37.5                     # half footprint
FLOOR = 3.0                             # floor z 0..3
SHELF_Z0, SHELF_Z1 = 18.0, 21.0         # shelf above the power bank
LID_Z0, LID_Z1 = 44.0, 47.0             # lid 3 mm
PACK = dict(c=(13.0, 0.0, 10.5), s=(100.0, 65.0, 15.0))
LILY = dict(c=(0.0, 19.0, 32.5), s=(66.0, 28.0, 23.0))
PCA = dict(c=(0.0, -21.0, 32.0), s=(63.0, 26.0, 22.0))
LED = dict(c=(0.0, -2.0, 41.0), s=(52.0, 10.5, 3.5))
WIN = dict(c=(2.0, 19.0), s=(44.0, 24.0))          # lid screen window (x, y)
POKE = [(-29.0, 10.0), (-29.0, 28.0)]               # BOOT/KEY poke holes, d3
# SG90 nominal (contract): body 22.8 L x 12.2 W x 22.7 H, tabs span 32.2, shaft 5.5 off centre,
# tab underside 15.9 above base, tab 2.5 thick, gear boss d11.8 to 26.7, shaft tip 31.
SG = dict(L=22.8, W=12.2, H=22.7, TAB=32.2, OFF=5.5, TAB_Z=15.9, TAB_T=2.5, BOSS_D=11.8, BOSS_H=26.7, TIP=31.0)
HIP_X, HIP_Y = 53.9, 18.4               # hip servo body centres (+-)
SHAFT_Y = 23.9                          # hip shaft |y|
SERVO_Z0 = SHELF_Z1                     # hip servo base on the shelf
TAB_Z0 = SERVO_Z0 + SG['TAB_Z']         # 36.9 tab underside
TAB_Z1 = TAB_Z0 + SG['TAB_T']           # 39.4 tab top = clamp bar underside
BAR_Z1 = 43.4                           # clamp bar top (0.6 under the lid)
WALL = 3.0
SIDE_IN_LOW = 33.0                      # tunnel half width (pack 65 + 1 mm)
SIDE_IN_HIGH = 34.5                     # inner wall face above the shelf (3 mm wall)
INNER_X0, INNER_X1 = 40.6, 47.6         # |x| of the hip pocket inner wall / bar spine
SCREW_X = 44.1                          # |x| of all M3 bar/lid screws
BAR_SCREW_Y = 8.0                       # M3x12 bar screws at (+-44.1, +-8)
LID_SCREW_Y = 30.0                      # M3x20 lid+bar screws at (+-44.1, +-30)
LID_HEAD_Z = LID_Z0                     # M3x20 head seats in a lid counterbore at z 44 -> head top 47.0 (body limit)
LID_BOSS_Z0 = 41.4                      # lid boss under each M3x20 drops into a pocket in the clamp bar
LID_BOSS_D = 7.0
LID_BOSS_BOX = (37.5, 47.6, 25.5, 33.0)  # |x0|,|x1|,|y0|,|y1| of the lid boss block, fused over its whole top to the lid
LID_POCKET = 1.8                        # lid underside pocket over LILYGO and PCA (skin 1.2): LILYGO rides 1.8 higher
LILY_Z0, LILY_Z1 = 21.0 + LID_POCKET, 44.0 + LID_POCKET   # 22.8 .. 45.8 (contract box 21..44 shifted, D4)
LILY_BODY_Z0 = 37.5                     # GIA DINH: clear-shell underside (vendor STEP glass->PCB back 6.4 + shell)
HEADER_ROWS = ((5.0, 9.5), (28.5, 33.0)) # y bands of the two LILYGO header rows + Dupont housings
TRENCH_Y = ((4.5, 10.5), (28.0, 33.0))  # shelf trenches under the header rows, open to the pack top (z 18)
NUT_Z = 34.0                            # nut slot centre: M3x12 tip 31.4 and M3x20 tip 27 pass through
CABLE_GAP_Y = (12.0, 26.0)              # |y| range where the inner wall is cut for cables

# ------------------------------------------------------------- leg (case-owned)
LEG_R_KNEE = 30.0                       # knee servo centre radius from hip shaft (contract target)
KNEE_Z = 40.0                           # knee servo body centre z
KNEE_AXIS_Z = KNEE_Z + SG['OFF']        # shaft 5.5 above body centre -> 45.5
HORN_TOP_Z = SERVO_Z0 + SG['TIP'] + 0.5 # hip horn flat top 52.5
GROOVE = 2.2                            # horn groove depth
FEMUR_Z0 = HORN_TOP_Z - GROOVE          # 50.3
FEMUR_Z1 = FEMUR_Z0 + 8.0               # 58.3
# knee servo local: s = shaft axis (along leg tangential t), base at t = -H/2
KNEE_T_BASE = -SG['H'] / 2
KNEE_T_TAB0 = KNEE_T_BASE + SG['TAB_Z']             # 4.55 pocket face
KNEE_HORN_T = KNEE_T_BASE + SG['TIP'] + 0.5         # 20.15 knee horn flat face
TIBIA_T0 = KNEE_HORN_T - GROOVE                     # 17.95
TIBIA_T1 = TIBIA_T0 + 8.0                           # 25.95
FOOT_R, FOOT_Z = 58.0, -20.0                        # neutral foot centre (leg frame r, z)

LEGS = {  # name: (sx, sy, hip shaft xy, radial angle deg, PCA hip ch, knee ch)
    'FL': (+1, +1, (HIP_X, SHAFT_Y), 45.0, 0, 1),
    'FR': (+1, -1, (HIP_X, -SHAFT_Y), -45.0, 2, 3),
    'RL': (-1, +1, (-HIP_X, SHAFT_Y), 135.0, 4, 5),
    'RR': (-1, -1, (-HIP_X, -SHAFT_Y), -135.0, 6, 7),
}


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cbox(c, s):
    return box(c[0] - s[0] / 2, c[0] + s[0] / 2, c[1] - s[1] / 2, c[1] + s[1] / 2, c[2] - s[2] / 2, c[2] + s[2] / 2)


def rbox(x0, x1, y0, y1, z0, z1, r):
    """Box with vertical edges rounded (r >= 2 mm fillets on load paths)."""
    b = box(x0, x1, y0, y1, z0, z1)
    return b.edges('|Z').fillet(r) if r > 0 else b


def cyl(x, y, z0, z1, d):
    return cq.Workplane('XY').circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def mirror_x(w):
    return w.mirror('YZ')


def mirror_y(w):
    return w.mirror('XZ')


def quad(w, sx, sy):
    """Copy a +X+Y feature into the quadrant (sx, sy) by mirroring."""
    if sx < 0:
        w = mirror_x(w)
    if sy < 0:
        w = mirror_y(w)
    return w


def nut_slot(x, y, z, toward_center=True):
    """Horizontal M3 nut slot (5.9 AF, 2.8 tall) entered from the inboard (-|x|) face."""
    sx = 1 if x > 0 else -1
    # slot runs from the nut centre to the inboard wall face
    x_face = sx * INNER_X0
    xa, xb = sorted((x, x_face - sx * 1.0))
    slot = box(xa, xb, y - 2.95, y + 2.95, z - 1.4, z + 1.4)
    hexn = cq.Workplane('XY').polygon(6, 6.6).extrude(2.8).translate((x, y, z - 1.4))
    return slot.union(hexn)


# ------------------------------------------------------------------- servo envelopes
def sg90_hip(sx, sy):
    """Hip SG90 envelope (reference, not printed): body + tabs + gear boss + shaft."""
    cx, cy = sx * HIP_X, sy * HIP_Y
    body = cbox((cx, cy, SERVO_Z0 + SG['H'] / 2), (SG['W'], SG['L'], SG['H']))
    tabs = cbox((cx, cy, TAB_Z0 + SG['TAB_T'] / 2), (SG['W'], SG['TAB'], SG['TAB_T']))
    boss = cyl(cx, sy * SHAFT_Y, SERVO_Z0 + SG['H'], SERVO_Z0 + SG['BOSS_H'], SG['BOSS_D'])
    shaft = cyl(cx, sy * SHAFT_Y, SERVO_Z0 + SG['BOSS_H'], SERVO_Z0 + SG['TIP'], 4.8)
    return body.union(tabs).union(boss).union(shaft)


def horn_outline(depth, clear=0.2):
    """SG90 single-arm horn outline in its own frame: hub at origin, arm along +X, z 0..depth."""
    hub = cq.Workplane('XY').circle(3.8 + clear).extrude(depth)
    arm = (cq.Workplane('XY').polyline([(0, -3.0 - clear), (17.5, -2.1 - clear), (17.5, 2.1 + clear), (0, 3.0 + clear)])
           .close().extrude(depth))
    tip = cq.Workplane('XY').circle(2.1 + clear).extrude(depth).translate((17.5, 0, 0))
    return hub.union(arm).union(tip)


def horn_solid():
    """Reference horn body (hub boss + arm), frame: flat top at z=0, hub boss downward."""
    arm = horn_outline(1.8, clear=0).translate((0, 0, -1.8))
    hubb = cq.Workplane('XY').circle(3.5).extrude(4.2).translate((0, 0, -4.2))
    return arm.union(hubb)


# ----------------------------------------------------------------------- legs
def _leg_world(w, leg):
    sx, sy, (hx, hy), ang, _, _ = LEGS['FL']
    w = w.rotate((0, 0, 0), (0, 0, 1), ang).translate((hx, hy, 0))
    lsx, lsy = LEGS[leg][0], LEGS[leg][1]
    return quad(w, lsx, lsy)


def femur_local():
    """Leg part 1 (dui): hip horn plate + knee SG90 box, one solid. Local frame (r, t, z)."""
    t0, t1 = KNEE_T_BASE - WALL, KNEE_T_TAB0          # -14.35 .. 4.55
    r0, r1 = LEG_R_KNEE - SG['W'] / 2 - WALL, LEG_R_KNEE + SG['W'] / 2 + WALL  # 20.9 .. 39.1
    plate = rbox(-12.0, r1, t0, t1, FEMUR_Z0, FEMUR_Z1, 4.0).union(cyl(0, 0, FEMUR_Z0, FEMUR_Z1, 26.0))
    kz0 = KNEE_Z - SG['TAB'] / 2 - 0.5                 # 23.4
    kbox = rbox(r0, r1, t0, t1, kz0, FEMUR_Z1, 3.0)
    f = plate.union(kbox)
    # knee servo cavity, open toward +t (insert from the horn side), 0.3 mm clearance per side
    cav = box(LEG_R_KNEE - SG['W'] / 2 - 0.3, LEG_R_KNEE + SG['W'] / 2 + 0.3,
              KNEE_T_BASE - 0.3, t1 + 1.0, KNEE_Z - SG['L'] / 2 - 0.3, KNEE_Z + SG['L'] / 2 + 0.3)
    f = f.cut(cav)
    # cable exit through the bottom end wall (cable leaves the servo at its lower end)
    f = f.cut(box(LEG_R_KNEE - 4.0, LEG_R_KNEE + 4.0, KNEE_T_BASE - 0.3, KNEE_T_BASE + 6.0, kz0 - 1, KNEE_Z))
    # SG90 bag tab-screw pilots (d1.8, 8 deep) into the +t pocket face
    for dz in (-13.9, 13.9):
        pil = cq.Workplane('XZ').circle(0.9).extrude(8.0).translate((LEG_R_KNEE, t1, KNEE_Z + dz))
        f = f.cut(pil)
    # hip horn groove on the underside, arm pointing outward (+r); centre screw access d6
    f = f.cut(horn_outline(GROOVE).translate((0, 0, FEMUR_Z0)))
    f = f.cut(cyl(0, 0, FEMUR_Z0, FEMUR_Z1 + 1, 6.0))
    for r in (10.0, 15.0):
        f = f.cut(cyl(r, 0, FEMUR_Z0, FEMUR_Z0 + 6.0, 1.6))
    return f


def _tibia_pre():
    """Tibia in the pre-frame (x = r, y = z, z = -t)."""
    ax, az = LEG_R_KNEE, KNEE_AXIS_Z
    dx, dz = FOOT_R - ax, FOOT_Z - az
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    nx, nz = -uz, ux
    pts = [(ax + nx * 10, az + nz * 10), (FOOT_R + nx * 7, FOOT_Z + nz * 7),
           (FOOT_R - nx * 7, FOOT_Z - nz * 7), (ax - nx * 10, az - nz * 10)]
    zt0, zt1 = -TIBIA_T1, -TIBIA_T0
    th = zt1 - zt0
    beam = cq.Workplane('XY').polyline(pts).close().extrude(th)
    hub = cq.Workplane('XY').circle(12.0).extrude(th).translate((ax, az, 0))
    foot = cq.Workplane('XY').circle(7.0).extrude(th).translate((FOOT_R, FOOT_Z, 0))
    t = beam.union(hub).union(foot).translate((0, 0, zt0))
    ang = math.degrees(math.atan2(dz, dx))
    g = horn_outline(GROOVE).rotate((0, 0, 0), (0, 0, 1), ang).translate((ax, az, zt1 - GROOVE))
    t = t.cut(g)
    t = t.cut(cq.Workplane('XY').circle(3.0).extrude(th + 2).translate((ax, az, zt0 - 1)))
    for d in (10.0, 15.0):
        t = t.cut(cq.Workplane('XY').circle(0.8).extrude(6.0).translate((ax + ux * d, az + uz * d, zt1 - 6.0)))
    return t


def tibia_local():
    return _tibia_pre().rotate((0, 0, 0), (1, 0, 0), 90)


def knee_servo_local():
    """Reference knee SG90 in leg frame: long axis vertical, shaft along +t at z 45.5."""
    r, z = LEG_R_KNEE, KNEE_Z
    b = KNEE_T_BASE
    body = box(r - SG['W'] / 2, r + SG['W'] / 2, b, b + SG['H'], z - SG['L'] / 2, z + SG['L'] / 2)
    tabs = box(r - SG['W'] / 2, r + SG['W'] / 2, b + SG['TAB_Z'], b + SG['TAB_Z'] + SG['TAB_T'],
               z - SG['TAB'] / 2, z + SG['TAB'] / 2)
    boss = cq.Workplane('XZ').circle(SG['BOSS_D'] / 2).extrude(-(SG['BOSS_H'] - SG['H'])).translate((r, b + SG['H'], KNEE_AXIS_Z))
    shaft = cq.Workplane('XZ').circle(2.4).extrude(-(SG['TIP'] - SG['BOSS_H'])).translate((r, b + SG['BOSS_H'], KNEE_AXIS_Z))
    return body.union(tabs).union(boss).union(shaft)


def femur(leg):
    return _leg_world(femur_local(), leg)


def tibia(leg, knee_deg=0.0, hip_deg=0.0):
    t = tibia_local()
    if knee_deg:
        t = t.rotate((LEG_R_KNEE, 0, KNEE_AXIS_Z), (LEG_R_KNEE, 1, KNEE_AXIS_Z), knee_deg)
    if hip_deg:
        t = t.rotate((0, 0, 0), (0, 0, 1), hip_deg)
    return _leg_world(t, leg)


def leg_posed(local, leg, hip_deg=0.0):
    if hip_deg:
        local = local.rotate((0, 0, 0), (0, 0, 1), hip_deg)
    return _leg_world(local, leg)


# ------------------------------------------------------------------ body parts
def _hip_pocket_quadrant():
    """+X+Y hip pocket block (walls on the shelf), built for FL and mirrored to the others."""
    yb0, yb1 = HIP_Y - SG['L'] / 2 - 0.3, HIP_Y + SG['L'] / 2 + 0.3    # cavity y 6.7 .. 30.1
    xb0 = HIP_X - SG['W'] / 2 - 0.3                                      # cavity x 47.5
    z0 = SHELF_Z1
    # Y end walls carry the tabs (tab underside z 36.9); inner end wall runs to the centre line
    inner_end = box(INNER_X0, HX, 0.0, yb0, z0, TAB_Z0)
    outer_end = box(INNER_X0, HX, yb1, HY, z0, TAB_Z0)
    inner_wall = box(INNER_X0, xb0, 0.0, HY, z0, TAB_Z1)                 # spine support 6.9 wide
    q = inner_end.union(outer_end).union(inner_wall)
    # between the tabs (|y| < 2.3) raise the centre block to the bar underside
    q = q.union(box(INNER_X0, HX, 0.0, HIP_Y - SG['TAB'] / 2 - 0.3, z0, TAB_Z1))
    # cable gap through the inner wall (USB L-cable at the rear, servo/power cables)
    q = q.cut(box(INNER_X0 - 1, xb0 + 0.01, CABLE_GAP_Y[0], CABLE_GAP_Y[1], z0 - 0.1, TAB_Z1 + 1))
    # hip servo cable exit: notch in the inner end wall bottom (cable leaves at the inner end)
    q = q.cut(box(xb0, HIP_X + 3.0, 2.0, yb0 + 0.1, z0 - 0.1, z0 + 6.0))
    # screw holes d3.4 and nut slots for M3x12 (y=8) and M3x20 (y=30)
    for y in (BAR_SCREW_Y, LID_SCREW_Y):
        q = q.cut(cyl(SCREW_X, y, NUT_Z - 11.5, TAB_Z1 + 1, 3.4))     # M3x20 tip reaches z 24
        q = q.cut(nut_slot(SCREW_X, y, NUT_Z))
    return q


def bottom():
    """P01 day: floor, side/end walls, pack tunnel, shelf, hip pockets, cradles, LED bridge."""
    b = rbox(-HX, HX, -HY, HY, 0, FLOOR, 5.0)
    # side walls: 4.5 thick beside the pack, 3.0 above the shelf
    for s in (1, -1):
        lo = box(-HX, HX, min(s * SIDE_IN_LOW, s * HY), max(s * SIDE_IN_LOW, s * HY), 0, SHELF_Z1)
        hi = box(-INNER_X0 - 0.01, INNER_X0 + 0.01, min(s * SIDE_IN_HIGH, s * HY), max(s * SIDE_IN_HIGH, s * HY), SHELF_Z1 - 0.01, LID_Z0)
        b = b.union(lo).union(hi)
    # rear end wall (-X), full height, with the finger window over the plug zone
    b = b.union(box(-HX, -HX + WALL, -HY, HY, 0, TAB_Z1))          # top = tab level, bar fingers rest on it
    b = b.cut(box(-HX - 1, -HX + WALL + 1, -24.0, 24.0, FLOOR + 2.0, SHELF_Z0 - 1.0))
    # shelf over the pack (z 18..21), from the end wall to the front
    b = b.union(box(-HX + WALL - 0.01, HX, -HY, HY, SHELF_Z0, SHELF_Z1))
    # cable holes through the shelf down into the plug zone (L-cable +Y, power cable -Y)
    for s in (1, -1):
        b = b.cut(box(-47.0, -40.6, min(s * 12.0, s * 26.0), max(s * 12.0, s * 26.0), SHELF_Z0 - 1, SHELF_Z1 + 1))
    # hip pockets, 4 quadrants (mirrored copies keep the body symmetric)
    q = _hip_pocket_quadrant()
    for sx in (1, -1):
        for sy in (1, -1):
            b = b.union(quad(q, sx, sy))
    # pack stops on the floor at the port end (x -40..-37), outside the port area
    for s in (1, -1):
        b = b.union(box(-40.5, -37.5, min(s * 24.0, s * 32.9), max(s * 24.0, s * 32.9), FLOOR - 0.01, FLOOR + 3.0))
    # pack strap: 2 floor slots (4 x 2.5) at x 52, beside the pack; groove under the shelf
    for s in (1, -1):
        b = b.cut(box(50.0, 54.0, min(s * 33.1, s * 35.6), max(s * 33.1, s * 35.6), -1, SHELF_Z0 - 0.0))
    b = b.cut(box(50.0, 54.0, -33.2, 33.2, SHELF_Z0 - 0.01, SHELF_Z0 + 1.2))
    # LILYGO cradle: central box rib under the board (y 15..23) + end stops beside the USB
    lz0 = LILY['c'][2] - LILY['s'][2] / 2                # 21
    rib = rbox(-24.0, 31.0, 15.0, 23.0, SHELF_Z1 - 0.01, LILY_BODY_Z0, 2.0)   # box rib, board rests on it
    b = b.union(rib)
    lx1 = LILY['c'][0] + LILY['s'][0] / 2
    # +X end stop 7.2 x 9.5, clear of the nut slot paths (|y| 5.05..10.95, 27.05..32.95), merged into
    # the hip pocket inner wall which is closed again at y 12..21 on this quadrant only
    b = b.union(box(INNER_X0 - 0.01, HIP_X - SG['W'] / 2 - 0.3, CABLE_GAP_Y[0] - 0.01, 21.0, SHELF_Z1 - 0.01, TAB_Z1))
    b = b.union(box(lx1 + 0.4, INNER_X0 + 0.01, 11.5, 21.0, SHELF_Z1 - 0.01, TAB_Z1))
    b = b.union(box(lx1 + 0.4, INNER_X0 - 0.4, 11.5, 21.0, TAB_Z1 - 0.01, 42.0))   # clears the bar spine
    # trenches under the LILYGO header rows: Dupont wires leave the housings downward and bend here
    for y0, y1 in TRENCH_Y:
        b = b.cut(box(-31.5, 31.5, y0, y1, SHELF_Z0 - 0.01, SHELF_Z1 + 0.01))
    # PCA9685 rim pocket (3 sides; the -Y side is the body wall) + 2 SG90-screw pads
    px0, px1 = PCA['c'][0] - PCA['s'][0] / 2 - 0.4, PCA['c'][0] + PCA['s'][0] / 2 + 0.4
    py1 = PCA['c'][1] + PCA['s'][1] / 2 + 0.3            # -7.7
    for x0, x1 in ((px0 - 3.0, px0), (px1, px1 + 3.0)):
        b = b.union(box(x0, x1, -SIDE_IN_HIGH, -20.0, SHELF_Z1 - 0.01, SHELF_Z1 + 4.0))
    # LED bridge: two pillars 8 x 10.5 (<= 3x smallest side) + top beam, LED in a 0.6 recess
    ly0, ly1 = LED['c'][1] - LED['s'][1] / 2, LED['c'][1] + LED['s'][1] / 2
    lz = LED['c'][2] - LED['s'][2] / 2                   # 39.25
    by0, by1 = ly0 - 0.2 + 0.0, ly1 + 0.2
    by0 = max(by0, py1 + 0.3)
    for x0 in (-30.0, 22.0):
        b = b.union(rbox(x0, x0 + 8.0, by0, by1, SHELF_Z1 - 0.01, lz, 2.0))
    for x0 in (-30.0, 22.0):
        b = b.union(box(x0, x0 + 8.0, by0, by1, lz - 1.0, lz + 0.6))
    beam = box(-30.0, 30.0, by0, by1, lz - 3.4, lz + 0.6)                        # 4 mm beam
    beam = beam.cut(box(-26.4, 26.4, ly0 - 0.2, ly1 + 0.2, lz, lz + 1))          # LED recess 0.6
    beam = beam.cut(box(-1.5, 1.5, by0 - 1, by1 + 1, lz - 2.8, lz - 0.8))       # zip-tie hole
    b = b.union(beam)
    b = b.cut(box(-26.4, 26.4, ly0 - 0.2, ly1 + 0.2, lz, lz + 4.0))             # LED bar seat
    # wire notches in the side walls for knee cables (z 38..44) near the hips
    for sx in (1, -1):
        for sy in (1, -1):
            x0, x1 = sorted((sx * 33.0, sx * 39.0))
            b = b.cut(box(x0, x1, min(sy * 33.0, sy * 38.0), max(sy * 33.0, sy * 38.0), 38.0, LID_Z0 + 1))
    return b


def clamp_bar(sx):
    """P03/P04 thanh de: one bar over both hip servos of an axle, spine + fingers over the tabs."""
    z0, z1 = TAB_Z1, BAR_Z1
    yb0 = HIP_Y - SG['L'] / 2 - 0.3
    yb1 = HIP_Y + SG['L'] / 2 + 0.3
    bar = rbox(INNER_X0, INNER_X1, -HY + 0.6, HY - 0.6, z0, z1, 2.0)           # spine 7 wide
    bar = bar.union(rbox(INNER_X0, HX - 0.4, -yb0, yb0, z0, z1, 2.0))         # centre finger
    for s in (1, -1):
        y0, y1 = sorted((s * yb1, s * (HY - 0.6)))
        bar = bar.union(rbox(INNER_X0, HX - 0.4, y0, y1, z0, z1, 2.0))        # outer fingers
    for y in (BAR_SCREW_Y, -BAR_SCREW_Y, LID_SCREW_Y, -LID_SCREW_Y):
        bar = bar.cut(cyl(SCREW_X, y, z0 - 1, z1 + 1, 3.4))
    for y in (LID_SCREW_Y, -LID_SCREW_Y):     # pocket for the lid boss (bar keeps 2 mm under it)
        s_ = 1 if y > 0 else -1
        y0, y1 = sorted((s_ * (LID_BOSS_BOX[2] - 0.3), s_ * (LID_BOSS_BOX[3] + 0.3)))
        bar = bar.cut(box(LID_BOSS_BOX[0] - 0.3, LID_BOSS_BOX[1] + 0.3, y0, y1, LID_BOSS_Z0 - 0.1, z1 + 1))
    return bar if sx > 0 else mirror_x(bar)


def lid():
    """P02 nap: 3 mm plate; screen window, BOOT poke holes, LED diffuser skin 0.8, servo holes."""
    l = rbox(-HX, HX, -HY, HY, LID_Z0, LID_Z1, 5.0)
    wx, wy = WIN['c']
    l = l.cut(box(wx - WIN['s'][0] / 2, wx + WIN['s'][0] / 2, wy - WIN['s'][1] / 2, wy + WIN['s'][1] / 2, LID_Z0 - 1, LID_Z1 + 1))
    for x, y in POKE:
        l = l.cut(cyl(x, y, LID_Z0 - 1, LID_Z1 + 1, 3.0))
    ly0, ly1 = LED['c'][1] - LED['s'][1] / 2, LED['c'][1] + LED['s'][1] / 2
    l = l.cut(box(-27.0, 27.0, ly0 - 0.3, ly1 + 0.3, LID_Z0 - 1, LID_Z1 - 0.8))   # 0.8 skin
    for sx in (1, -1):
        for sy in (1, -1):
            # servo top (body top 43.7, gear boss d11.8): clearance d13 + body slot
            l = l.cut(cyl(sx * HIP_X, sy * SHAFT_Y, LID_Z0 - 1, LID_Z1 + 1, 13.0))
            # M3x20: boss under the lid (into the bar pocket), counterbore so the head ends at z 47
            bx0, bx1 = sorted((sx * LID_BOSS_BOX[0], sx * LID_BOSS_BOX[1]))
            by0, by1 = sorted((sy * LID_BOSS_BOX[2], sy * LID_BOSS_BOX[3]))
            l = l.union(rbox(bx0, bx1, by0, by1, LID_BOSS_Z0, LID_Z0 + 0.01, 1.0))
            l = l.cut(cyl(sx * SCREW_X, sy * LID_SCREW_Y, LID_HEAD_Z, LID_Z1 + 1, 6.4))
            l = l.cut(cyl(sx * SCREW_X, sy * LID_SCREW_Y, LID_BOSS_Z0 - 1, LID_Z1 + 1, 3.4))
            l = l.cut(cyl(sx * SCREW_X, sy * BAR_SCREW_Y, LID_Z0 - 1, LID_Z1 + 1, 7.0))   # bar screw head
    # underside pockets (skin 1.2): LILYGO seat (locates and clamps the board) and PCA plug/lead room
    lc, ls = LILY['c'], LILY['s']
    l = l.cut(box(lc[0] - ls[0] / 2 - 0.5, lc[0] + ls[0] / 2 + 0.5, lc[1] - ls[1] / 2 - 0.5, lc[1] + ls[1] / 2 + 0.5,
                  LID_Z0 - 1, LID_Z0 + LID_POCKET))
    pc, ps = PCA['c'], PCA['s']
    l = l.cut(box(pc[0] - ps[0] / 2 - 0.5, pc[0] + ps[0] / 2 + 0.5, -SIDE_IN_HIGH + 0.1, -9.0, LID_Z0 - 1, LID_Z0 + LID_POCKET))
    return l


# ------------------------------------------------------- reference envelopes (not printed)
def lilygo_ref():
    """GIA DINH: shell+PCB+screen z 33..44 full footprint; Dupont housings in 4 mm strips below."""
    c, s = LILY['c'], LILY['s']
    x0, x1, y0, y1 = c[0] - s[0] / 2, c[0] + s[0] / 2, c[1] - s[1] / 2, c[1] + s[1] / 2
    top = box(x0, x1, y0, y1, LILY_BODY_Z0, LILY_Z1)
    strips = [box(x0 + 2, x1 - 2, a, b_, LILY_Z0, LILY_BODY_Z0) for a, b_ in HEADER_ROWS]
    return top.union(strips[0]).union(strips[1])


def modules_ref():
    out = {'POWER_BANK': cbox(PACK['c'], PACK['s']), 'LILYGO_TDISPLAY_S3': lilygo_ref(),
           'PCA9685': cbox(PCA['c'], PCA['s']), 'LED_BAR_WS2812_KK10': cbox(LED['c'], LED['s'])}
    return out


def keepouts():
    """Plug and cable zones that printed parts must leave free (contract + case GIA DINH)."""
    return {
        'plug_zone_pack_ports': box(-60.0, -37.0, -24.0, 24.0, 3.0, 18.0),
        'usb_c_L_plug_head': box(-40.0, -33.0, 14.0, 24.0, 32.0, 40.0),
        'usb_c_L_cable_down': box(-47.0, -40.6, 15.0, 23.0, 18.0, 39.0),
        'power_cable_up': box(-47.0, -40.6, -23.0, -15.0, 18.0, 39.0),
        'lilygo_dupont_wires_row1': box(-31.0, 31.0, HEADER_ROWS[0][0] + 0.3, HEADER_ROWS[0][1], SHELF_Z0, LILY_Z0),
        'lilygo_dupont_wires_row2': box(-31.0, 31.0, HEADER_ROWS[1][0], HEADER_ROWS[1][1] - 0.3, SHELF_Z0, LILY_Z0),
        'pca_lead_bend_room': box(-31.0, 31.0, -33.5, -10.0, 43.0, LID_Z0 + LID_POCKET - 0.05),
        'pca_terminal_wires': box(-6.0, 6.0, -7.6, 2.0, 22.0, 30.0),
        'screen_view': box(WIN['c'][0] - WIN['s'][0] / 2, WIN['c'][0] + WIN['s'][0] / 2,
                           WIN['c'][1] - WIN['s'][1] / 2, WIN['c'][1] + WIN['s'][1] / 2, 44.0, 60.0),
        'boot_poke_1': cyl(POKE[0][0], POKE[0][1], 44.0, 60.0, 2.6),
        'boot_poke_2': cyl(POKE[1][0], POKE[1][1], 44.0, 60.0, 2.6),
    }


def screw(x, y, z_head_bottom, length, down=True, head_d=5.5, head_h=3.0, d=3.0):
    """Socket-head M3 screw: head on top of z_head_bottom, shank pointing down."""
    head = cyl(x, y, z_head_bottom, z_head_bottom + head_h, head_d)
    shank = cyl(x, y, z_head_bottom - length, z_head_bottom, d)
    return head.union(shank)


def nut(x, y, z):
    return cq.Workplane('XY').polygon(6, 6.35).extrude(2.4).translate((x, y, z - 1.2))


def fasteners():
    """Instance map: id -> dict(kind, x, y, head z, length, nut z, parts, step)."""
    items = []
    n = 1
    for sx, end in ((1, 'truoc'), (-1, 'sau')):
        for sy in (1, -1):
            items.append(dict(id=f'S{n:02d}', size='M3x12', x=sx * SCREW_X, y=sy * BAR_SCREW_Y, zhead=BAR_Z1, L=12.0,
                              nut=NUT_Z, parts=[f'P0{3 if sx > 0 else 4}_thanh_de_{end}', 'P01_day'], step=3,
                              entry='từ trên xuống (−Z)', tool='lục giác 2.5 mm', note='kẹp 2 servo hông'))
            n += 1
    for sx, end in ((1, 'truoc'), (-1, 'sau')):
        for sy in (1, -1):
            items.append(dict(id=f'S{n:02d}', size='M3x20', x=sx * SCREW_X, y=sy * LID_SCREW_Y, zhead=LID_HEAD_Z, L=20.0,
                              nut=NUT_Z, parts=['P02_nap', f'P0{3 if sx > 0 else 4}_thanh_de_{end}', 'P01_day'], step=6,
                              entry='từ trên xuống (−Z)', tool='lục giác 2.5 mm', note='giữ nắp + thanh đè'))
            n += 1
    return items

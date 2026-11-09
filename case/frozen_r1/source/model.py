"""Robot Cua A1 V4 - printed mechanics (CadQuery), all parts ASSEMBLED in the contract robot frame.

Frame (PILOT_CONTRACT.json coordinateFrame): mm, origin = body footprint centre on the base
bottom face, +X forward (bank slides out the front), +Y left, +Z up.
Every number here is a case-owned nominal or a GIA DINH reference size (see case/DEVIATIONS.md).
"""
import math
import cadquery as cq

# ----------------------------------------------------------------------------- body layout
BX, BY = 62.5, 37.0          # half length / half width of the body shell (125 x 74)
CORNER_R = 5.0               # vertical edge round of the body plan
FLOOR_T = 3.0                # base floor 0..3
WALL_T = 3.0                 # load-bearing walls
TUN_Z0, TUN_Z1 = 3.0, 18.5   # power-bank tunnel (bank 15 + 0.5)
DECK_Z0, DECK_Z1 = 18.5, 21.5
LID_Z0, LID_Z1 = 43.5, 46.5  # lid plate
CAP_X0 = 40.0                # |x| >= CAP_X0 belongs to the clamp caps
TAB_Z0, TAB_Z1 = 37.4, 39.9  # SG90 hip tab underside/top (servo bottom on deck z=21.5)
INNER_Y = BY - WALL_T        # 34.0, inside face of the side walls
BANK = dict(x0=-37.5, x1=62.5, y=33.0, z0=3.0, z1=18.0)
BAY_X0 = -BX + WALL_T        # -59.5 rear bay inner face

# hip servos (contract): shaft axes at (+-53.25, +-22.8), bottom on the deck
HIP_X, HIP_Y = 53.25, 22.8
SERVO_Z0 = DECK_Z1           # 21.5

# LILYGO T-Display-S3 placed from the vendor STEP (t-display-s3-full.stp, LilyGO GitHub, sha256 d33dc105...).
# STEP frame: board long axis +Y (USB-C end at y=0), screen/buttons/USB-C on the -Z face, PCB z -1.2..0.
# Robot placement (DEVIATION D1/D2): robot = (step_y + LX_A, step_x + LCY, -step_z + LZ0)
LX_A = -24.78                # PCB USB-end edge x
LCY = 20.5                   # board centre y
LZ0 = 39.32                  # PCB back face z (screen glass top at LZ0 + 6.38 = 45.70)
L_PCB_LEN, L_HALF_W = 60.78, 12.75
L_DISP = (4.58, 60.78)       # display module y_step span (frame), top at +6.35
L_GLASS = (6.66, 56.53, 12.97)
L_USB = dict(x0=-1.2, x1=6.3, w0=-4.61, w1=4.34, top=4.36)
L_BUTTONS = [(2.3, -9.3), (2.2, 8.8)]   # (y_step, x_step) of the two screen-side push buttons
L_HEADER_X = 11.43           # header rows at step x = +-11.43, pins y_step 24.1 .. 52.0
L_HEADER_Y = (24.1, 52.0)
DUPONT_DROP = 16.5           # header spacer 2.5 + female Dupont housing 14 below the PCB
LILY = dict(cx=LX_A + L_PCB_LEN / 2, cy=LCY, cz=LZ0 + 1.6, sx=64.0, sy=28.0, sz=12.0)
PCA = dict(cx=0.0, cy=-20.0, cz=31.5, sx=64.0, sy=27.0, sz=23.0)
LED = dict(cx=0.0, cy=0.0, cz=41.5, sx=56.0, sy=12.0, sz=4.0)

# fasteners (owned set only): (id, x, y, z_head_seat, length, kind)
CAP_SCREW_XY = [(43.5, 31.0), (43.5, -31.0)]
LID_SCREW_XY = [(36.0, 0.0), (-36.0, 0.0)]
NUT_AF, NUT_T = 5.5, 2.4     # M3 nut across flats / thickness
NUT_SLOT_W, NUT_SLOT_H = 5.9, 2.8
M3_CLEAR = 3.4

# SG90 reference (GIA DINH from the common drawing; coupon proves the fit)
SG = dict(L=22.8, W=12.2, H=22.7, shaft_off=5.9, tab_span=32.2, tab_z0=15.9, tab_t=2.5,
          tower_d=11.8, tower_h=4.0, spline_d=4.8, spline_top=30.0, bump_d=5.5, bump_h=1.5)
HORN = dict(hub_d=7.0, hub_h=3.8, hub_z0=26.9, arm_len=15.5, arm_w0=5.5, arm_w1=3.8, arm_t=1.6,
            hole_r=11.0)
FIT = 0.15                    # per-side press/locating clearance (coupon tunes it)

# legs (leg frame: r outward at 45 deg, t = r rotated +90 deg, z absolute)
R_KNEE = 30.0
Z_KNEE = 52.6
T_SERVO_B = -13.6             # knee servo bottom face (t); tabs at t -13.6+15.9 = 2.3
THIGH_Z0, THIGH_Z1 = 48.6, 56.6
THIGH_TOP = Z_KNEE + 10.1        # flat print face (printed upside down)
FOOT_T0, FOOT_T1 = 13.5, 21.5
FOOT_TIP = (45.0, -12.0)      # (r, z) foot tip centre at neutral
GROUND_Z = FOOT_TIP[1] - 4.5  # tip radius 4.5 -> ground plane


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane('XY').circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def hexprism_z(x, y, z0, z1, af):
    return cq.Workplane('XY').polygon(6, af / math.cos(math.pi / 6)).extrude(z1 - z0).translate((x, y, z0))


def plan_outline(z0, z1, x0=-BX, x1=BX, y0=-BY, y1=BY, r=CORNER_R, round_x=(True, True)):
    s = box(x0, x1, y0, y1, z0, z1)
    sel = []
    if round_x[0] and round_x[1]:
        return s.edges('|Z').fillet(r)
    if round_x[1]:
        return s.edges('|Z and >X').fillet(r)
    if round_x[0]:
        return s.edges('|Z and <X').fillet(r)
    return s


def mirror_x(wp):
    return wp.mirror('YZ')


def both_ends(fn):
    """fn(sign) builds a front feature for sign=+1; returns union of front and rear copies."""
    return fn(1).union(fn(-1))


# ----------------------------------------------------------------------------- SG90 reference
def sg90_local(with_horn=True, horn_angle_deg=0.0):
    """SG90 in its own frame: shaft axis = +Z at (0,0); bottom face z=0; long axis +X (body from
    -shaft_off to L-shaft_off); width along Y."""
    L, W, H = SG['L'], SG['W'], SG['H']
    x0 = -SG['shaft_off']
    body = box(x0, x0 + L, -W / 2, W / 2, 0, H)
    cx = x0 + L / 2
    tabs = box(cx - SG['tab_span'] / 2, cx + SG['tab_span'] / 2, -W / 2 + 0.2, W / 2 - 0.2,
               SG['tab_z0'], SG['tab_z0'] + SG['tab_t'])
    tower = cyl(0, 0, H, H + SG['tower_h'], SG['tower_d'])
    bump = cyl(8.0, 0, H, H + SG['bump_h'], SG['bump_d'])
    spline = cyl(0, 0, H + SG['tower_h'], SG['spline_top'], SG['spline_d'])
    s = body.union(tabs).union(tower).union(bump).union(spline)
    if with_horn:
        s = s.union(horn_local(horn_angle_deg))
    return s


def horn_profile(clear=0.0):
    """2-D single-arm horn outline (XY) with the arm along +X."""
    r0 = HORN['hub_d'] / 2 + clear
    w0, w1 = HORN['arm_w0'] / 2 + clear, HORN['arm_w1'] / 2 + clear
    L = HORN['arm_len']
    hub = cq.Workplane('XY').circle(r0)
    arm = (cq.Workplane('XY').moveTo(0, -w0).lineTo(L, -w1).threePointArc((L + w1, 0), (L, w1))
           .lineTo(0, w0).close())
    return hub, arm


def horn_local(angle_deg=0.0, clear=0.0, z_extra=0.0):
    z0 = HORN['hub_z0']
    hub_h = HORN['hub_h'] + z_extra
    hub, arm = horn_profile(clear)
    h = hub.extrude(hub_h).translate((0, 0, z0 - z_extra / 2 if False else z0))
    a = arm.extrude(HORN['arm_t'] + z_extra).translate((0, 0, z0 + HORN['hub_h'] - HORN['arm_t']))
    return h.union(a).rotate((0, 0, 0), (0, 0, 1), angle_deg)


# placement helpers ------------------------------------------------------------
def hip_servo_FL_place(shape):
    """Map SG90 local -> FL hip: shaft at (HIP_X, HIP_Y), bottom on the deck, body toward -Y."""
    return shape.rotate((0, 0, 0), (0, 0, 1), -90).translate((HIP_X, HIP_Y, SERVO_Z0))


def corner_place(shape, corner):
    """FL geometry -> other corner by true mirror (printed parts) - FR mirror XZ, RL mirror YZ."""
    if corner == 'FL':
        return shape
    if corner == 'FR':
        return shape.mirror('XZ')
    if corner == 'RL':
        return shape.mirror('YZ')
    if corner == 'RR':
        return shape.mirror('XZ').mirror('YZ')
    raise ValueError(corner)


def corner_rigid(shape, corner):
    """Bought SG90 for another corner. The SG90 model is symmetric across its width plane, so the
    mirror image equals the real rigid placement (hips: FR = FL turned 180 deg about Z; knees: the
    mirrored leg's servo is the FL servo turned 180 deg about its long axis). Never a mirrored servo."""
    return corner_place(shape, corner)


# ----------------------------------------------------------------------------- base
def base():
    top = LID_Z0
    s = plan_outline(0, top)
    # cap zone is lower: caps sit on z = TAB_Z1 for |x| >= CAP_X0
    for sg in (1, -1):
        x0, x1 = (CAP_X0, BX + 1) if sg > 0 else (-BX - 1, -CAP_X0)
        s = s.cut(box(x0, x1, -BY - 1, BY + 1, TAB_Z1, top + 1))
    # interior cavities
    s = s.cut(box(BANK['x0'], BX + 1, -INNER_Y, INNER_Y, TUN_Z0, TUN_Z1))      # bank tunnel, open front
    s = s.cut(box(BAY_X0, BANK['x0'] + 0.01, -INNER_Y, INNER_Y, TUN_Z0, TUN_Z1))  # rear bay
    s = s.cut(box(-BX - 1, BAY_X0 + 0.01, -26.0, 26.0, TUN_Z0, TUN_Z1))     # rear service opening
    s = s.cut(box(-BX + WALL_T, BX - WALL_T, -INNER_Y, INNER_Y, DECK_Z1, top + 1))  # electronics zone
    s = s.union(internal_structures())
    s = s.cut(internal_cuts())
    s = s.union(strap_ribs())
    return s.clean()


def internal_structures():
    parts = []
    for sg in (1, -1):
        X = lambda a, b: (min(sg * a, sg * b), max(sg * a, sg * b))
        # central block between the two hip servos of one end (tab seat for the inner tabs)
        x0, x1 = X(41.0, BX - WALL_T)
        parts.append(box(x0, x1, -5.8, 5.8, DECK_Z1, TAB_Z0))
        # inner pocket wall (3 mm) up to the cap seat
        x0, x1 = X(44.0, 47.0)
        parts.append(box(x0, x1, -INNER_Y, INNER_Y, DECK_Z1, TAB_Z1))
        # outer tab seats against the side walls
        x0, x1 = X(47.0, BX - WALL_T)
        for sy in (1, -1):
            y0, y1 = sorted((sy * 29.0, sy * INNER_Y))
            parts.append(box(x0, x1, y0, y1, DECK_Z1, TAB_Z0))
        # cap-screw corner blocks
        x0, x1 = X(40.0, 47.0)
        for sy in (1, -1):
            y0, y1 = sorted((sy * 26.5, sy * INNER_Y))
            parts.append(box(x0, x1, y0, y1, DECK_Z1, TAB_Z1))
        # lid-screw boss on the spine
        x0, x1 = X(31.0, CAP_X0 - 0.2)
        parts.append(box(x0, x1, -4.0, 4.0, DECK_Z1, LID_Z0))
    # central spine (box-section stiffener + LED bar seat), joins both central blocks
    parts.append(box(-44.0, 44.0, -3.0, 3.0, DECK_Z1, LED['cz'] - LED['sz'] / 2))
    # LILYGO end saddles (DEVIATION D2): far end full width (component-free), USB end only on the
    # component-free strip step_x 4.5..12.75; locating lips; the lid holds it down (window lip + USB pocket)
    y_lo, y_hi = LCY - L_HALF_W, LCY + L_HALF_W
    lip_y0 = y_lo - 6.3                       # 6 mm wide locating ridge sits ON the far saddle (no free posts)
    fx0, fx1 = LX_A + 54.0, LX_A + L_PCB_LEN
    parts.append(box(fx0, fx1 + 3.3, lip_y0, INNER_Y, DECK_Z1, LZ0))
    parts.append(box(fx1 + 0.3, CAP_X0 - 0.2, lip_y0, INNER_Y, LZ0 - 0.01, LZ0 + 3.0))   # far-end x stop lip
    # USB end: back-side parts reach 3.5 mm below the PCB; the STEP height map leaves a free band at
    # y_step 5.6..7.9 / x_step -7.5..5.5 -> a 2.3 mm support rib (3.7 mm tall) on a block under them
    ux0, ux1 = LX_A + 1.0, LX_A + 7.9
    parts.append(box(ux0, ux1, y_lo, INNER_Y, DECK_Z1, LZ0 - 3.7))
    parts.append(box(LX_A + 5.6, ux1, LCY - 7.5, LCY + 5.1, LZ0 - 3.71, LZ0))
    parts.append(box(fx0, fx1 + 3.3, lip_y0, y_lo - 0.3, DECK_Z1, LZ0 + 3.0))          # y ridge (far end only)
    # bank rear corner stops (below the USB port height)
    for sy in (1, -1):
        y0, y1 = sorted((sy * 28.0, sy * INNER_Y))
        parts.append(box(BANK['x0'] - 3.0, BANK['x0'], y0, y1, TUN_Z0, 6.5))
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def internal_cuts():
    cuts = []
    for sg in (1, -1):
        X = lambda a, b: (min(sg * a, sg * b), max(sg * a, sg * b))
        # hip servo cable channels under the inner end of each servo, out to the electronics zone
        for sy in (1, -1):
            y0, y1 = sorted((sy * 2.6, sy * 5.9))
            x0, x1 = X(40.5, 59.0)
            cuts.append(box(x0, x1, y0, y1, DECK_Z1 - 0.01, DECK_Z1 + 4.5))
        # cap screw holes + side-entry nut slots from the outer wall
        for (cx, cy) in CAP_SCREW_XY:
            x, y = sg * cx, cy
            cuts.append(cyl(x, y, DECK_Z1 - 0.01, TAB_Z1 + 1, M3_CLEAR))
            nz0 = 28.0
            ys = sorted((y - NUT_SLOT_W / 2 * (1 if y > 0 else -1) * 0 + (0 if y > 0 else 0), 0))
            y_in = y - (NUT_AF / math.sqrt(3) + 0.3) if y > 0 else y + (NUT_AF / math.sqrt(3) + 0.3)
            y_out = BY + 1 if y > 0 else -BY - 1
            a, b = sorted((y_in, y_out))
            cuts.append(box(x - NUT_SLOT_W / 2, x + NUT_SLOT_W / 2, a, b, nz0, nz0 + NUT_SLOT_H))
        # lid screw holes + nut slot entering from the +Y face of the boss
        for (cx, cy) in LID_SCREW_XY:
            if (cx > 0) != (sg > 0):
                continue
            cuts.append(cyl(cx, cy, DECK_Z1 + 2, LID_Z0 + 1, M3_CLEAR))
            nz0 = 36.2      # nut enters from the -Y (PCA-side) face of the boss
            cuts.append(box(cx - NUT_SLOT_W / 2, cx + NUT_SLOT_W / 2, -4.5, NUT_AF / math.sqrt(3) + 0.3, nz0, nz0 + NUT_SLOT_H))
        # knee-servo wire windows in the side-wall tops (closed by the lid)
        for sy in (1, -1):
            y0, y1 = sorted((sy * (INNER_Y - 0.5), sy * (BY + 1)))
            x0, x1 = X(28.0, 36.0)
            cuts.append(box(x0, x1, y0, y1, LID_Z0 - 5.0, LID_Z0 + 0.01))
    # deck slots: port-1 USB cable riser and port-2 power wires
    cuts.append(box(-43.5, -36.0, 6.0, 24.0, DECK_Z0 - 0.01, DECK_Z1 + 0.01))
    cuts.append(box(-39.5, -33.5, -24.0, -8.0, DECK_Z0 - 0.01, DECK_Z1 + 0.01))
    # PCA9685 locating recess = its contract envelope footprint + 0.2, floor at the envelope bottom z=20
    cuts.append(box(PCA['cx'] - 32.2, PCA['cx'] + 32.2, PCA['cy'] - 13.7, PCA['cy'] + 13.7, 20.0, DECK_Z1 + 0.01))
    # wire-bend wells under the LILYGO header rows (Dupont housings end ~2 mm above the deck)
    for sx in (-1, 1):
        yc = LCY + sx * L_HEADER_X
        cuts.append(box(LX_A + L_HEADER_Y[0] - 2.5, LX_A + L_HEADER_Y[1] + 2.5, max(yc - 2.2, LCY - L_HALF_W - 0.7),
                        min(yc + 2.2, INNER_Y), 19.5, DECK_Z1 + 0.01))
    out = cuts[0]
    for c in cuts[1:]:
        out = out.union(c)
    return out


def strap_ribs():
    """0.5 mm strap guide ribs on the outer side walls (belt around the bank front, body <= 75 wide)."""
    parts = []
    for sy in (1, -1):
        for z0 in (2.0, 16.5):
            y0, y1 = sorted((sy * (BY - 0.5), sy * (BY + 0.5)))
            parts.append(box(-50.0, 50.0, y0, y1, z0, z0 + 1.5))
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


# ----------------------------------------------------------------------------- lid
def lid():
    s = box(-CAP_X0 + 0.2, CAP_X0 - 0.2, -BY, BY, LID_Z0, LID_Z1)
    # LED diffuser channel from below: 0.8 mm skin over the bar, centred on the body
    s = s.cut(box(-29.0, 29.0, -6.6, 6.6, LID_Z0 - 0.01, LID_Z1 - 0.8))
    # stepped screen window: display module passes up to z 45.7, a 0.8 mm lip over the module's
    # frame ends holds the board down; the glass (active area inside it) is fully open
    c = 0.3
    s = s.cut(box(LX_A + L_DISP[0] - c, LX_A + L_DISP[1] + c, LCY - L_HALF_W - c, LCY + L_HALF_W + c,
                  LID_Z0 - 0.01, LZ0 + 6.38 + 0.01))
    s = s.cut(box(LX_A + L_GLASS[0] - 0.2, LX_A + L_GLASS[1] + 0.2, LCY - L_GLASS[2] - 0.2, LCY + L_GLASS[2] + 0.2,
                  LID_Z0, LID_Z1 + 0.01))
    # pocket over the USB-C receptacle end (shell bears here: USB end cannot lift > 0.2 mm)
    s = s.cut(box(LX_A - 1.5, LX_A + L_DISP[0], LCY - L_HALF_W - c, LCY + L_HALF_W + c, LID_Z0 - 0.01, LZ0 + L_USB['top'] + 0.2))
    # opening for the USB-C plug overmold (its top reaches above the lid underside)
    s = s.cut(box(-CAP_X0 - 1.0, LX_A - 1.2, LCY - 7.5, LCY + 7.5, LID_Z0 - 0.01, LID_Z1 + 0.01))   # open notch
    # pin holes over the two screen-side buttons (BOOT = GPIO0; the other is GPIO14)
    for (ys, xs) in L_BUTTONS:
        s = s.cut(cyl(LX_A + ys, LCY + xs, LID_Z0 - 1, LID_Z1 + 1, 3.0))
    # screws
    for (x, y) in LID_SCREW_XY:
        s = s.cut(cyl(x, y, LID_Z0 - 1, LID_Z1 + 1, M3_CLEAR))
    # locating keys that drop beside the spine bosses (stop lateral slip of the lid)
    return s.clean()


# ----------------------------------------------------------------------------- caps (shared clamp bars)
def cap(sign=1):
    x0, x1 = CAP_X0, BX
    s = box(x0, x1, -BY, BY, TAB_Z1, LID_Z1)
    s = s.edges('|Z and >X').fillet(CORNER_R)
    # windows around the servo bodies above the tabs (gear tower passes through)
    for sy in (1, -1):
        y0, y1 = sorted((sy * 5.8, sy * 29.0))
        s = s.cut(box(47.0, BX - WALL_T, y0, y1, TAB_Z1 - 0.01, LID_Z1 + 0.01))
    for (cx, cy) in CAP_SCREW_XY:
        s = s.cut(cyl(cx, cy, TAB_Z1 - 1, LID_Z1 + 1, M3_CLEAR))
    if sign < 0:
        s = s.mirror('YZ')
    return s.clean()


# ----------------------------------------------------------------------------- legs (FL master)
def leg_to_global(shape):
    return shape.rotate((0, 0, 0), (0, 0, 1), 45).translate((HIP_X, HIP_Y, 0))


def knee_servo_leg():
    """Knee SG90 in the FL leg frame (r,t,z): long axis +r from the shaft at R_KNEE, shaft along +t."""
    s = sg90_local(with_horn=True, horn_angle_deg=90)  # horn arm points down (-z after mapping)
    # local: x long, y width, z height(shaft) -> leg: x->r, y->z, z->t
    s = s.rotate((0, 0, 0), (1, 0, 0), -90)   # local z -> -y? we want local z -> +t(Y), local y -> z
    # after rotate -90 about X: (x,y,z)->(x, z, -y)  => local z->+Y(t), local y -> -Z
    return s.translate((R_KNEE, T_SERVO_B, Z_KNEE))


def hip_horn_leg():
    """Hip horn in the leg frame: on the hip shaft (r=t=0), arm along +r."""
    return horn_local(0.0).translate((0, 0, SERVO_Z0))


def thigh_leg():
    hub = cyl(0, 0, THIGH_Z0, THIGH_TOP, 18.0)
    slab = box(0, 23.9, -9.0, 2.3, THIGH_Z0, THIGH_TOP)
    plate = box(8.0, 55.0, -3.7, 2.3, Z_KNEE - 10.1, THIGH_TOP)
    plate = plate.cut(box(7.0, 19.5, -5.0, 3.0, Z_KNEE - 11.0, THIGH_Z0))    # stay above the body near the hip
    s = hub.union(slab).union(plate)
    s = s.edges('|Y').fillet(2.0) if False else s
    # knee servo window through the plate (body + FIT)
    xs0 = R_KNEE - SG['shaft_off'] - FIT
    xs1 = R_KNEE - SG['shaft_off'] + SG['L'] + FIT
    s = s.cut(box(xs0, xs1, -10.0, 10.0, Z_KNEE - SG['W'] / 2 - FIT, Z_KNEE + SG['W'] / 2 + FIT))
    # tab screw pilots (SG90 bag screws), through the plate along -t
    cxs = R_KNEE - SG['shaft_off'] + SG['L'] / 2
    for rx in (cxs - SG['tab_span'] / 2 + 2.3, cxs + SG['tab_span'] / 2 - 2.3):
        s = s.cut(cq.Workplane('XZ').circle(0.8).extrude(-12).translate((rx, -6.0, Z_KNEE)))
    # hip horn press-fit slot from below + horn arm screw pilot + centre-screw access
    hub2d, arm2d = horn_profile(FIT * 0.6)
    depth = HORN['hub_h'] + 0.2
    s = s.cut(hub2d.extrude(depth).translate((0, 0, THIGH_Z0 - 0.01)))
    s = s.cut(arm2d.extrude(depth).translate((0, 0, THIGH_Z0 - 0.01)))
    s = s.cut(cyl(HORN['hole_r'], 0, THIGH_Z0, THIGH_Z0 + depth + 5.0, 1.5))
    s = s.cut(cyl(0, 0, THIGH_Z0, THIGH_TOP + 1, 6.0))
    # recess so the thigh clears the gear tower top under the hub
    return s.clean()


def foot_leg():
    tr, tz = FOOT_TIP
    t0, t1 = FOOT_T0, FOOT_T1
    # side profile in the r-z plane (sketch on XZ, extrude along +t)
    # outward "C": the shank leaves the knee outward, so at body height it stays >= 18 mm from the hip
    # axis even with the knee turned 30 deg inward (mech_check sweeps it)
    pts = [(R_KNEE - 8.0, Z_KNEE), (R_KNEE - 8.0, Z_KNEE - 8.0), (R_KNEE + 10.0, Z_KNEE - 26.0),
           (tr - 5.0, tz + 14.0), (tr - 4.5, tz), (tr + 4.5, tz), (tr + 7.0, tz + 16.0),
           (R_KNEE + 20.0, Z_KNEE - 20.0), (R_KNEE + 13.0, Z_KNEE)]
    prof = cq.Workplane('XZ').polyline(pts).close().extrude(-(t1 - t0)).translate((0, t0, 0))
    hub = cq.Workplane('XZ').circle(9.0).extrude(-(t1 - t0)).translate((R_KNEE, t0, Z_KNEE))
    s = prof.union(hub)
    tip = cq.Workplane('XZ').circle(4.5).extrude(-(t1 - t0)).translate((tr, t0, tz))
    s = s.union(tip)
    try:
        s = s.edges('|Y').fillet(2.0)
    except Exception:
        pass
    # knee horn slot (arm pointing down) from the -t face, arm screw pilot, centre-screw access
    hub2d, arm2d = horn_profile(FIT * 0.6)
    depth = HORN['hub_h'] + 0.2
    rot = lambda w: (w.rotate((0, 0, 0), (0, 0, 1), 90).rotate((0, 0, 0), (1, 0, 0), -90)
                     .translate((R_KNEE, t0 - 0.01, Z_KNEE)))
    s = s.cut(rot(hub2d.extrude(depth))).cut(rot(arm2d.extrude(depth)))
    s = s.cut(cq.Workplane('XZ').circle(0.75).extrude(-(t1 - t0 - 1.0)).translate((R_KNEE, t0, Z_KNEE - HORN['hole_r'])))  # blind pilot
    s = s.cut(cq.Workplane('XZ').circle(3.0).extrude(-(t1 - t0 + 2)).translate((R_KNEE, t0 - 1, Z_KNEE)))
    return s.clean()


def knee_horn_leg():
    h = horn_local(90.0).rotate((0, 0, 0), (1, 0, 0), -90)   # (x,y,z)->(x,z,-y): shaft +t, arm -z
    return h.translate((R_KNEE, T_SERVO_B, Z_KNEE))


def leg_parts(corner, hip_deg=0.0, knee_deg=0.0):
    """Return (thigh, foot) solids for a corner in the assembled frame at joint angles (deg).
    hip_deg: CCW about +Z seen from above for FL; mirrored legs get the mirrored motion."""
    th = thigh_leg()
    ft = foot_leg()
    if knee_deg:
        ft = ft.rotate((R_KNEE, 0, Z_KNEE), (R_KNEE, 1, Z_KNEE), knee_deg)
    th = leg_to_global(th)
    ft = leg_to_global(ft)
    if hip_deg:
        ax = ((HIP_X, HIP_Y, 0), (HIP_X, HIP_Y, 1))
        th = th.rotate(*ax, hip_deg)
        ft = ft.rotate(*ax, hip_deg)
    return corner_place(th, corner), corner_place(ft, corner)

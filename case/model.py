"""Robot Cua A1 V4 - printed mechanics (CadQuery), all parts ASSEMBLED in the contract robot frame.

Frame (PILOT_CONTRACT.json coordinateFrame): mm, origin = body footprint centre on the base
bottom face, +X forward (bank slides out the front), +Y left, +Z up.
Every number here is a case-owned nominal or a GIA DINH reference size (see case/DEVIATIONS.md).
"""
import json
import math
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent

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

# A1V4-r2 skeleton (release note 2): the side walls above the deck become windows under sturdy rails.
# Belly (z <= DECK_Z1) and the hip blocks (|x| >= CAP_X0) are unchanged: mech_check diffs them against r1.
RAIL_Z0 = 36.5               # side rail z RAIL_Z0..LID_Z0 = 7 tall x 3 wide, clamped at both ends
WIN_R = 3.0                  # window corner radius (>= 2 mm fillet rule at every rail/pier root)
WIN_END_X = 37.0             # windows stop here: the wall from here to CAP_X0 ties the rail to the hip block
# (side y sign, x0, x1) of each window bay (A1V4-r3: both sides are one long bay; the integrated board sits inside)
SIDE_WINDOWS = [(-1, -WIN_END_X, WIN_END_X), (1, -WIN_END_X, WIN_END_X)]
LED_CH_HALF_Y = 6.4          # diffuser channel half-width (bar +-6.0); centred on the body
LED_TIE_X = (-14.0, 14.0)    # zip-tie stations, between LEDs (at +-10.5 / +-17.5)
LID_OPEN_X = 36.0            # half length of the big -Y opening (3.8 mm end members stay)
LED = dict(cx=0.0, cy=0.0, cz=41.5, sx=56.0, sy=12.0, sz=4.0)

# ----------------------------------------------------------------------------- integrated board (release note 4)
# Everything about the board comes from one enclosure-contract JSON (KiCad frame) + a case-owned placement.
# Board-frame -> robot-frame: rotate about Z by rotDeg, translate (dx, dy), PCB bottom face at z = zBottomMm.
_PLACE = json.loads((HERE / 'board_placement.json').read_text())
_EC = json.loads((HERE / _PLACE['source']).read_text())
BOARD_STATUS = 'DRAFT' if _EC.get('draft') else 'PUBLISHED'
BOARD_T = float(_EC['board']['thicknessMm'])
BOARD_ZB = float(_PLACE['zBottomMm'])
BOARD_ZT = BOARD_ZB + BOARD_T
_rot = math.radians(_PLACE.get('rotDeg', 0))
_c, _s = math.cos(_rot), math.sin(_rot)


def board_xy(x, y):
    """Board-local (KiCad frame, +x right / +y up from the top, origin at the outline centre) -> robot XY."""
    return (x * _c - y * _s + _PLACE['dxMm'], x * _s + y * _c + _PLACE['dyMm'])


def board_box(box4):
    """Board-local [x0, y0, x1, y1] -> robot-frame axis-aligned (x0, y0, x1, y1)."""
    pts = [board_xy(box4[i], box4[j]) for i, j in ((0, 1), (2, 1), (2, 3), (0, 3))]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


_W, _H = _EC['board']['widthMm'], _EC['board']['heightMm']
_CX, _CY = _EC['board'].get('centerMm', [0, 0])
BOARD_OUTLINE = board_box([_CX - _W / 2, _CY - _H / 2, _CX + _W / 2, _CY + _H / 2])
BOARD_HOLES = [dict(id=h.get('name', f'H{i + 1}'), xy=board_xy(h['xMm'], h['yMm'])) for i, h in enumerate(_EC.get('mountingHoles', []))]
_H_OVR = _PLACE.get('heightOverridesMm', {})
_BOX_OVR = _PLACE.get('boxOverridesMm', {})
_PLUG_H = float(_PLACE.get('plugHeightAboveBoardMm', 16.5))


def _is_plug_header(p):
    name = (p.get('value', '') or '') + ' ' + p.get('footprint', '')
    return any(k in name for k in ('CH', 'PinHeader', 'LED ', 'Waveshare')) and p.get('heightMm', 0) >= 8.0


def _top_h(p):
    if p['ref'] in _H_OVR:
        return float(_H_OVR[p['ref']]['h'])
    if p['ref'] in _BOX_OVR:
        return float(_BOX_OVR[p['ref']]['h'])
    return _PLUG_H if _is_plug_header(p) else p['heightMm']


def _part_box(p):
    return _BOX_OVR[p['ref']]['box'] if p['ref'] in _BOX_OVR else p['boxMm']


BOARD_PARTS = [dict(p, robotBox=board_box(_part_box(p)), heightMm=_top_h(p)) for p in _EC.get('parts', []) if p.get('heightMm', 0) > 0]
USB_PLUG_REAL = tuple(_PLACE.get('usbPlugRealMm', (11.4, 7.0)))
# Board-end slots in the hip blocks (D17): the 88 mm board reaches x +-44. They sit below the frozen nut seats (z 28).
SLOT_TOP = 26.3
SLOT_X = 44.25              # end clearance 0.25 (wall 2.75 mm locally for 2.3 mm of height)
SLOT_Y = 31.25
# Native contract box for U1 (courtyard + antenna keepout, overhangs the board): cut from the base so the final contract passes (D19).
U1_KEEPOUT = next((list(p['boxMm']) + [p['heightMm']] for p in _EC.get('parts', []) if p['ref'] == 'U1'), None)
# THT tails (board-interface.json, drill > 0.3): clearance wells in the deck; hip-lead grooves (D19)
_BI = json.loads((HERE / _PLACE['interfaceSource']).read_text()) if _PLACE.get('interfaceSource') else {}
BOARD_TAILS = [board_xy(pad['at'][0], -pad['at'][1]) for c in _BI.get('connectors', []) for pad in c.get('pads', [])
               if max(pad.get('drillMm', [0])) > 0.3]
TAIL_WELL_Z = 20.6          # deck well floor under the THT tails
GROOVE_Z = 20.5             # hip-lead grooves under the board
# Rear USB-C tunnel through the rear central block, along -X (D18). Its width (+-6.3) keeps the native plug corridor open.
USB_TUNNEL = dict(y=6.3, z0=BOARD_ZT + 1.65 - 4.0, z1=BOARD_ZT + 1.65 + 4.0)
J12_SCREW_X, J12_SCREW_Y = 36.0, (-3.0, 2.08)      # J12 pin column (board-interface.json local coords; screw holes above it)
BOARD_IF = {i['kind'] if i['kind'] != 'button' else f"button:{i.get('name', '')}": i for i in _EC.get('interfaces', [])}
BOARD_TOP_Z = max([BOARD_ZT + p['heightMm'] for p in BOARD_PARTS] + [BOARD_ZT])


# Display module (release note 4 V0): Waveshare 1.9in on a harness, turned 180 deg about Z, PCB top against a lid ledge.
_D = _PLACE['display']
DISP = dict(cx=_D['cxMm'], cy=_D['cyMm'], z_ledge=_D['ledgeZMm'], step=HERE / _D['step'],
            L=51.2, W=27.3, pcb_top=1.19, pcb_bot=-0.41, glass=3.09, active=(42.72, 22.7), panel_x=(0.3, 50.46), panel_y=(0.75, 26.56))
DISP_ZM = DISP['z_ledge'] - DISP['pcb_top']    # STEP z=0 plane in robot z
DISP_X0 = DISP['cx'] - DISP['L'] / 2
DISP_X1 = DISP['cx'] + DISP['L'] / 2
DISP_Y0 = DISP['cy'] - DISP['W'] / 2
DISP_Y1 = DISP['cy'] + DISP['W'] / 2


def disp_xy(xs, ys):
    """Waveshare STEP (x, y) -> robot XY with the module turned 180 deg about Z."""
    return (DISP_X1 - xs, DISP_Y1 - ys)


_px = sorted(disp_xy(v, DISP['panel_y'][0])[0] for v in DISP['panel_x'])
_py = sorted(disp_xy(DISP['panel_x'][0], v)[1] for v in DISP['panel_y'])
DISP_WIN = dict(x0=_px[0] - 0.2, x1=_px[1] + 0.2, y0=_py[0] - 0.2, y1=_py[1] + 0.2)      # panel through-window
DISP_ACTIVE_C = disp_xy(sum(DISP['panel_x']) / 2, sum(DISP['panel_y']) / 2)
DISP_TIE_Y = [DISP_Y1 - 2.8, DISP_Y1 - 24.5]   # tie stations (STEP y 2.8 and 24.5, clear of the back connector y 6.3..21)


def disp_back_boxes():
    """Module envelope from the STEP, in robot frame: (label, x0, x1, y0, y1, z0, z1)."""
    z = DISP_ZM
    out = [('PCB', 0.0, 51.2, 0.0, 27.3, DISP['pcb_bot'], DISP['pcb_top']), ('panel', *DISP['panel_x'], *DISP['panel_y'], DISP['pcb_top'], DISP['glass']),
           ('connector', 12.52, 16.72, 6.28, 21.03, -3.91, DISP['pcb_bot']), ('chip', 36.29, 42.79, 5.75, 21.85, -2.41, DISP['pcb_bot'])]
    for cx, cy in ((2.8, 2.8), (48.4, 2.8), (2.8, 24.5), (48.4, 24.5)):
        out.append(('pillar', cx - 1.75, cx + 1.75, cy - 1.75, cy + 1.75, -2.91, DISP['pcb_bot']))
    rows = []
    for lab, x0s, x1s, y0s, y1s, z0, z1 in out:
        xa, ya = disp_xy(x0s, y0s)
        xb, yb = disp_xy(x1s, y1s)
        rows.append((lab, min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z + z0, z + z1))
    return rows


def iface_xy(kind):
    i = BOARD_IF.get(kind)
    return board_xy(*i['centerMm']) if i else None


# Plug tops (vertical 3-pin headers + servo plug) must stay under the lid plane; the wire bends may pass through its open frame.
LID_PAD_Y0 = BY - 5.7        # inner face of a pad: outside the board plan (|y| > 31.25), merged into the 3 mm wall
LID_PAD_X = (31.5, 39.99)    # |x| range of each pad, tied into the 3 mm wall at x 37-40 (does not enter the frozen |x| >= 40 zone)
LID_SCREWS = [(36.0, BY - 4.0), (36.0, -(BY - 4.0)), (-36.0, -(BY - 4.0))]   # 3 corners: the rear +Y corner is under the display module
LID_PILOT = 2.7              # M3x8 self-taps into this pilot (no nut fits in the 5.7 mm pad)

# fasteners (owned set only): (id, x, y, z_head_seat, length, kind)
CAP_SCREW_XY = [(43.5, 31.0), (43.5, -31.0)]
NUT_AF, NUT_T = 5.5, 2.4     # M3 nut across flats / thickness
NUT_SLOT_W, NUT_SLOT_H = 5.9, 2.8
M3_CLEAR = 3.4
NUT_WELL_D = 2.65            # drop-in hex well depth (2.4 nut + 0.25 relief under the board)

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
    s = s.cut(side_windows())
    s = s.union(strap_ribs())
    return s.clean()


def side_windows():
    """Cutters for the large side windows above the deck: wall only, rounded corners, rail left on top."""
    out = None
    for sy, x0, x1 in SIDE_WINDOWS:
        y0, y1 = sorted((sy * (INNER_Y - 0.01), sy * (BY + 1)))
        c = box(x0, x1, y0, y1, DECK_Z1, RAIL_Z0).edges('|Y').fillet(WIN_R)
        out = c if out is None else out.union(c)
    return out


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
    parts += board_blocks() + lid_pads()
    for sg in (1, -1):        # 4 mm stub of the old spine inside the hip-block zone (frozen geometry, tied to the central block)
        x0, x1 = sorted((sg * 40.0, sg * 44.0))
        parts.append(box(x0, x1, -3.0, 3.0, DECK_Z1, LED['cz'] - LED['sz'] / 2))
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
    cuts += board_screw_cuts() + lid_pad_cuts()
    cuts.append(box(40.0, 40.5, 3.2, 16.0, DECK_Z1, 28.0))   # sliver of the r1 FL-hip wire tunnel inside the frozen hip-block zone
    # board-end slots and the servo-lead / J12 wire corridor in the hip blocks, below the frozen nut seats (D17)
    for sg in (1, -1):
        x0, x1 = sorted((sg * 40.0, sg * SLOT_X))
        cuts.append(box(x0, x1, -SLOT_Y, SLOT_Y, BOARD_ZB, SLOT_TOP))
        x0, x1 = sorted((sg * 40.0, sg * 44.0))
        cuts.append(box(x0, x1, -6.0, 6.0, BOARD_ZB, TAB_Z0 + 2.2))
    # U1 contract box (D19): z top copper .. +3
    if U1_KEEPOUT:
        ux0, uy0, ux1, uy1 = board_box(U1_KEEPOUT[:4])
        cuts.append(box(ux0 - 0.05, ux1 + 0.05, uy0 - 0.05, uy1 + 0.05, BOARD_ZT - 0.01, BOARD_ZT + U1_KEEPOUT[4] + 0.05))
    # deck wells under the THT tails and hip-lead grooves under the board
    for (tx, ty) in BOARD_TAILS:
        cuts.append(box(tx - 1.4, tx + 1.4, ty - 1.4, ty + 1.4, TAIL_WELL_Z, DECK_Z1 + 0.01))
    for sg in (1, -1):
        xa, xb = sorted((sg * 26.0, sg * 41.0))
        for sy in (1, -1):
            ya, yb = sorted((sy * 1.5, sy * 7.5))
            cuts.append(box(xa, xb, ya, yb, GROOVE_Z, DECK_Z1 + 0.01))
        xa, xb = sorted((sg * 26.0, sg * 31.0))
        cuts.append(box(xa, xb, -SLOT_Y, SLOT_Y, GROOVE_Z, DECK_Z1 + 0.01))
    # USB-C tunnel through the rear central block and the rear wall (D18)
    t = USB_TUNNEL
    cuts.append(box(-BX - 1, -40.0, -t['y'], t['y'], t['z0'], t['z1']))
    # deck slots: port-1 USB cable riser and port-2 power wires
    cuts.append(box(-43.5, -36.0, 6.0, 24.0, DECK_Z0 - 0.01, DECK_Z1 + 0.01))
    cuts.append(box(-39.5, -33.5, -24.0, -8.0, DECK_Z0 - 0.01, DECK_Z1 + 0.01))
    out = cuts[0]
    for c in cuts[1:]:
        out = out.union(c)
    return out


def _root_strip(length, r=2.0):
    """Concave fillet cross-section (corner at the origin, leg r along +x and +z), extruded along +Y from the XZ plane."""
    k = r * (1 - math.sqrt(0.5))
    return (cq.Workplane('XZ').moveTo(0, 0).lineTo(r, 0).threePointArc((k, k), (0, r)).close().extrude(-length))


def _seat_r():
    return min(2.0, BOARD_ZB - DECK_Z1 - 0.05)


def _seat_block(x, y, sy):
    """One seat at the board height: 10 wide, root r 2. Runs to the side wall for holes near it, else to the free faces."""
    y0, y1 = sorted((y - sy * 5.0, sy * (INNER_Y + 0.5) if abs(y) >= 18.0 else y + sy * 5.0))
    x0, x1 = max(x - 5.0, -43.99), min(x + 5.0, 43.99)
    block = box(x0, x1, y0, y1, DECK_Z1, BOARD_ZB)
    free_y = ['<Y' if sy > 0 else '>Y'] if abs(y) >= 18.0 else ['<Y', '>Y']
    for sel in free_y:
        block = block.edges('|Z').edges(sel).fillet(2.0) if False else block
    try:
        for sel in free_y:
            block = block.edges('|Z').edges(sel).fillet(1.2)
    except Exception:
        pass
    e = 0.02
    tail_near = lambda xa, xb: any(xa - 1.0 < tx < xb + 1.0 and y0 - 1.0 < ty < y1 + 1.0 for tx, ty in BOARD_TAILS)
    if x1 < 43.5 and not tail_near(x1, x1 + _seat_r()):
        block = block.union(_root_strip(y1 - y0, _seat_r()).translate((x1 - e, y0, DECK_Z1 - e)))
    if x0 > -43.5 and not tail_near(x0 - _seat_r(), x0):
        block = block.union(_root_strip(y1 - y0, _seat_r()).mirror('YZ').translate((x0 + e, y0, DECK_Z1 - e)))
    return block


def board_blocks():
    """Board seat blocks at each mounting hole: deck-rooted, solid to the side wall (never a free post)."""
    return [_seat_block(h['xy'][0], h['xy'][1], 1 if h['xy'][1] > 0 else -1) for h in BOARD_HOLES]


def lid_pads():
    """Lid screw pads: blocks level with the rail, at the rail's end where the 3 mm wall runs from the deck to the lid."""
    out = []
    for (x, y) in LID_SCREWS:
        y0, y1 = sorted((math.copysign(LID_PAD_Y0, y), math.copysign(INNER_Y + 0.5, y)))
        x0, x1 = sorted((math.copysign(LID_PAD_X[0], x), math.copysign(LID_PAD_X[1], x)))
        out.append(box(x0, x1, y0, y1, RAIL_Z0, LID_Z0))
    return out


def board_screw_cuts():
    """M3x6 from the board top: M3 nut dropped into a hex well in the seat, tip clearance in the deck."""
    out = []
    for h in BOARD_HOLES:
        x, y = h['xy']
        out.append(cyl(x, y, BOARD_ZT - 6.0 - 0.2, BOARD_ZB + 0.01, M3_CLEAR))
        out.append(hexprism_z(0, 0, BOARD_ZB - NUT_WELL_D, BOARD_ZB + 0.01, NUT_AF + 0.3).rotate((0, 0, 0), (0, 0, 1), 30).translate((x, y, 0)))
        out.append(cyl(x, y, SLOT_TOP - 0.1, BOARD_ZT + 3.05, 6.4))   # screw-head relief in the hip-block underside (stays below the C nut seat)
    return out


def lid_pad_cuts():
    """M3x8 self-tapping into a Ø2.7 pilot in the rail-end pad (the pad is 5.7 mm deep: no room for a captive nut)."""
    return [cyl(x, y, LID_Z0 - 6.2, LID_Z0 + 0.01, LID_PILOT) for (x, y) in LID_SCREWS]


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
    """A1V4-r3 frame: holds the centred LED diffuser, opens over the screen, the servo headers and the buttons."""
    s = box(-CAP_X0 + 0.2, CAP_X0 - 0.2, -BY, BY, LID_Z0, LID_Z1)
    # LED diffuser channel from below: 0.8 mm skin over the bar, centred on the body
    s = s.cut(box(-29.0, 29.0, -LED_CH_HALF_Y, LED_CH_HALF_Y, LID_Z0 - 0.01, LID_Z1 - 0.8))
    # LED bar: one tie along the back of the bar, anchored around lid webs beyond each end of the channel
    for sx in (1, -1):
        for k in (0, 1):
            x0, x1 = sorted((sx * (29.5 + k * 2.6), sx * (31.0 + k * 2.6)))
            s = s.cut(box(x0, x1, -1.8, 1.8, LID_Z0 - 1, LID_Z1 + 1))
    # opening over everything on the -Y side: servo headers, connectors, wiring reachable with the frame on
    y1 = -LED_CH_HALF_Y - 5.0
    op = box(-LID_OPEN_X, LID_OPEN_X, -27.0, y1, LID_Z0 - 1, LID_Z1 + 1).edges('|Z').fillet(2.0)   # headers, terminal, connectors
    s = s.cut(op).cut(box(-30.0, 30.0, -BY + 3.5, -26.9, LID_Z0 - 1, LID_Z1 + 1).edges('|Z').fillet(2.0))   # clear of the corner lid screws
    # screen: a 0.5 deep pocket for the PCB rim, the panel in a through window. Glass stays below the lid top.
    s = s.cut(box(DISP_X0 - 0.3, DISP_X1 + 0.3, DISP_Y0 - 0.3, DISP_Y1 + 0.3, LID_Z0 - 0.01, DISP['z_ledge']))
    w = DISP_WIN
    s = s.cut(box(w['x0'], w['x1'], w['y0'], w['y1'], LID_Z0 - 1, LID_Z1 + 1))
    # display ties: at each module end a lid web between two slots; the tie runs along the module back (STEP y 2.8, 24.5)
    for ty in DISP_TIE_Y:
        for ex, sx in ((DISP_X0 - 0.8, -1), (DISP_X1 + 0.8, 1)):
            for k in (0, 1):
                x0, x1 = sorted((ex + sx * k * 2.4, ex + sx * (1.3 + k * 2.4)))
                s = s.cut(box(x0, x1, ty - 1.8, ty + 1.8, LID_Z0 - 1, LID_Z1 + 1))
    # RESET and BOOT: a notch in the -Y rim next to the opening. RESET is under the notch; BOOT sits under the LED bar and
    # is reached with a pin from the notch at about 23 deg (mech_check bootAccess measures that path).
    btns = [board_xy(*i['centerMm']) for k, i in BOARD_IF.items() if k.startswith('button:')]
    if btns:
        bx0, bx1 = min(b[0] for b in btns) - 3.0, max(b[0] for b in btns) + 3.0
        s = s.cut(box(bx0, bx1, -LED_CH_HALF_Y - 5.2, -LED_CH_HALF_Y - 1.1, LID_Z0 - 1, LID_Z1 + 1))
    for (x, y) in LID_SCREWS:
        s = s.cut(cyl(x, y, LID_Z0 - 1, LID_Z1 + 1, M3_CLEAR))
    # screwdriver holes over the J12 terminal screws (wired before the lid closes; holes let the owner re-tighten them)
    for jy in J12_SCREW_Y:
        s = s.cut(cyl(J12_SCREW_X, jy, LID_Z0 - 1, LID_Z1 + 1, 4.0))
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

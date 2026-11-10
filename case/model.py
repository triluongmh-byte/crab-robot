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
BX, BY = 63.0, 37.0          # half length / half width of the frame (126 x 74)
CORNER_R = 5.0               # vertical edge round of the body plan
FLOOR_T = 3.0                # base floor 0..3
WALL_T = 3.0                 # load-bearing walls
TUN_Z0, TUN_Z1 = 3.0, 18.5   # power-bank tunnel (bank 15 + 0.5)
DECK_Z0, DECK_Z1 = 18.5, 21.5
LID_Z0, LID_Z1 = 43.5, 46.5  # lid plate
TAB_Z0, TAB_Z1 = 37.4, 39.9  # SG90 hip tab underside/top (servo bottom on deck z=21.5)
INNER_Y = BY - WALL_T        # 34.0, inside face of the side walls
BANK = dict(x0=-37.5, x1=62.5, y=33.0, z0=3.0, z1=18.0)
BAY_X0 = -BX + WALL_T        # -59.5 rear bay inner face

# hip servos (contract): shaft axes at (+-53.25, +-22.8), bottom on the deck
HIP_X, HIP_Y = 53.25, 22.8
SERVO_Z0 = DECK_Z1           # 21.5

LED_CH_HALF_Y = 6.4          # diffuser channel half-width (bar +-6.0); centred on the body
LED_TIE_X = (-14.0, 14.0)    # zip-tie stations, between LEDs (at +-10.5 / +-17.5)
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
# THT tails (board-interface.json, drill > 0.3): clearance wells in the deck; hip-lead grooves (D19)
_BI = json.loads((HERE / _PLACE['interfaceSource']).read_text()) if _PLACE.get('interfaceSource') else {}
BOARD_TAILS = [board_xy(pad['at'][0], -pad['at'][1]) for c in _BI.get('connectors', []) for pad in c.get('pads', [])
               if max(pad.get('drillMm', [0])) > 0.3]
J12_SCREW_X, J12_SCREW_Y = 36.0, (-3.0, 2.08)      # J12 pin column (board-interface.json local coords; screw holes above it)
BOARD_IF = {i['kind'] if i['kind'] != 'button' else f"button:{i.get('name', '')}": i for i in _EC.get('interfaces', [])}
BOARD_TOP_Z = max([BOARD_ZT + p['heightMm'] for p in BOARD_PARTS] + [BOARD_ZT])
USB_ORDINARY_MM = (12.5, 7.0, 25.0)  # ordinary USB-C overmold: width (the board contract's own plugMm), thickness, rigid length (note 9)
USB_SHELL_MID_Z = 1.65                # plug centre above top copper: mid of the 3.3 mm shell (contract zMm). The STEP envelope (-0.8..3.3) is also tested, see USB_PLUG_Z_MIDS
USB_PLUG_Z_MIDS = (1.25, 1.65)        # plug centre heights above top copper checked on real solids: STEP envelope mid, shell mid


def usb_mouth():
    """J1 as published, in the robot frame: (mouth x, mouth y, access ax, access ay, plug centre z). The mouth face comes from the J1 body
    measured in the published STEP (board_placement.json jStepJ1, written by board_import.py); the contract centre is the fallback."""
    u = BOARD_IF['usb']
    ux, uy = board_xy(*u['centerMm'])
    a0, b0 = u.get('access', [-1, 0, 0])[:2]
    ax, ay = a0 * _c - b0 * _s, a0 * _s + b0 * _c
    centre = ux * ax + uy * ay
    st = _PLACE.get('stepJ1')
    if st and abs(ay) > 0.5:                 # side edge: the mouth is the J1 body's far Y face, plug centred on the body
        xa, ya, xb, yb = board_box([st['xMm'][0], st['yMm'][0], st['xMm'][1], st['yMm'][1]])
        return (xa + xb) / 2, (yb if ay > 0 else ya), ax, ay, BOARD_ZT + USB_SHELL_MID_Z
    reach = centre + u.get('sizeMm', [9.5, 10.7])[0] / 2
    for p in BOARD_PARTS:
        if p['ref'] == 'J1':
            xa, ya, xb, yb = p['robotBox']
            reach = max([reach] + [x * ax + y * ay for x in (xa, xb) for y in (ya, yb)])
    d = reach - centre
    return ux + ax * d, uy + ay * d, ax, ay, BOARD_ZT + u.get('zMm', 3.3) / 2


# J1 on a side edge (note 9) takes an ordinary cable through the side window; on the rear edge only the slim limit of D23 is modelled.
USB_SIDE = abs(usb_mouth()[3]) > 0.5
USB_PLUG_REAL = USB_ORDINARY_MM[:2] if USB_SIDE else tuple(_PLACE.get('usbPlugRealMm', (11.4, 7.0)))
USB_PLUG_LEN = USB_ORDINARY_MM[2] if USB_SIDE else 15.0


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
DISP_TIE_X = (-41.5, -36.0)                     # two zip ties across the module back, along Y, rear of the LED channel (D27)
DISP_GH_MOUTH_X = DISP_X1 - 12.52               # GH1.25 back socket, side entry, mouth faces +X (vendor STEP x 12.52..16.72)
DISP_GH_Y = (DISP_Y1 - 21.03, DISP_Y1 - 6.28)   # socket extent in Y
DISP_GH_Z = (DISP_ZM - 3.91, DISP_ZM - 0.41)    # socket extent in Z


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


# fasteners (owned set only): (id, x, y, z_head_seat, length, kind)
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


# ----------------------------------------------------------------------------- A1V4-r5 open bar skeleton (release notes 6, 7, 8)
# Two parts replace base + lid, no walls anywhere. Every bar is >= 3 mm on every side and tied at both ends.
#   frame_lower: bank cradle (floor bars, bottom rails, side trusses, deck rails), board seats, columns.
#   frame_upper: hip tab saddles (each servo held by its own two tabs, screwed directly), side rails, open screen/LED bridge.
# The board drops straight into frame_lower before frame_upper goes on, and the hip servos drop through the finished frame.
# No clamp bars (owner removed them for interference, notes 7 and 8): nothing presses on or sits over a servo body or gear boss.
BAR = 3.0                    # minimum bar side (note 6)
RAIL_Y0, RAIL_Y1 = 33.5, 37.0  # bottom rail / truss band outside the bank (+-33 + 0.5)
BOT_RAIL_Z = 6.0             # bottom rail z 0..6
FLOOR_Z = 3.0                # bank rests on floor bars at z 3
FLOOR_BAR_X = (56.5, 28.0, 0.0, -28.0, -49.0)   # centre x of the floor cross bars
FLOOR_BAR_W = 7.0
DECK_RAIL_Y0 = 31.3          # deck rails stop 0.3 outside the board plan (y +-31)
COL_Y0, COL_Y1 = 31.3, 37.3  # 6 x 6 columns outside the board plan (body stays inside +-37.5)
COL_TOP = 34.4               # joint and mid columns carry frame_upper here
SADDLE_Z0 = 31.4             # underside of the tab saddles (6 mm of plastic for the bag screw); corner columns land here
OUTER_COL_X = (57.0, 63.0)   # corner columns, outside the side window at each hip
JOINT_XS = (33.9, 39.9)      # bolted joint columns; rear +Y has none (D22: U1 contract box)
JOINT_SCREWS = [(36.9, 34.3), (36.9, -34.3), (-36.9, -34.3)]
JOINT_PILOT = 2.7            # M3x12 self-taps into this pilot in the joint column
MID_COL_X = (3.0, 9.0)       # one mid column per side, carries the long side rails
INNER_DECK_X = (43.0, 46.0)  # inner deck cross bar, inboard of the servo body
UPPER_RAIL_Z0 = 34.4         # side rails and cross bars of frame_upper: z 34.4..TAB_Z1
# hip servo clearances. The SG90 envelope is unmeasured and a tight fit already failed (note 8): no printed face is closer than this.
SERVO_HALF_W = SG_W_HALF = 6.1
SERVO_Y0, SERVO_Y1 = 5.9, 28.7     # body extent along Y (FL)
INNER_BAR_X = (43.0, 46.15)        # 1.0 mm from the body
OUTER_BAR_X = (60.0, 63.0)         # 0.65 mm from the body: the 126 mm envelope and the 3 mm bar rule leave no more
CENTRE_SADDLE_Y = 5.2              # 0.7 mm from the body inner end
OUTER_SADDLE_Y0 = 29.4             # 0.7 mm from the body outer end
TAB_HOLE_Y = (3.5, 31.1)           # SG90 tab holes (FL), nominal; the tab hole itself is larger than the bag screw
TAB_PILOT = 1.6                    # bag screw pilot, same as the knee tab pilots on the printed thighs
STRIP_END_X = 33.9           # end of the LED/screen strip (keeps the J12 terminal screws open from above)
LED_BEAM_Y = (6.4, 9.4)      # the two parallel beams carrying the LED strip to the hip blocks
SEAT_W = 8.0
TAB_PILOTS = [(sx * HIP_X, sy * yy) for sx in (1, -1) for sy in (1, -1) for yy in TAB_HOLE_Y]


def _bar_xz(pts, y0, y1):
    """Bar with a polygon profile in XZ, extruded across y0..y1."""
    return cq.Workplane('XZ').polyline(pts).close().extrude(-(y1 - y0)).translate((0, y0, 0))


def _strut(x0, z0, x1, z1, w, y0, y1):
    """Straight bar of width w between two points in the XZ plane."""
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    nx, nz = -dz / L * w / 2, dx / L * w / 2
    return _bar_xz([(x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)], y0, y1)


def _union(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.union(p)
    return out


def _both_y(fn):
    return [fn(1), fn(-1)]


def _sy_box(x0, x1, y0, y1, z0, z1, sy):
    a, b = sorted((sy * y0, sy * y1))
    return box(x0, x1, a, b, z0, z1)


def _fillet_ring(x0, x1, y0, y1, z, r=2.0):
    """Concave root fillet on the two X faces of a column foot sitting on the plane z (column goes up). Stays inside the body."""
    k = r * (1 - math.sqrt(0.5))
    strip = lambda: cq.Workplane('XZ').moveTo(0, 0).lineTo(r, 0).threePointArc((k, k), (0, r)).close().extrude(-(y1 - y0))
    out = None
    if x1 + r <= BX + 0.01:
        out = strip().translate((x1 - 0.02, y0, z - 0.02))
    if x0 - r >= -BX - 0.01:
        b = strip().mirror('YZ').translate((x0 + 0.02, y0, z - 0.02))
        out = b if out is None else out.union(b)
    return out


def frame_lower():
    p = []
    # bottom rails and deck rails along X
    for sy in (1, -1):
        p.append(_sy_box(-BX, BX, RAIL_Y0, RAIL_Y1, 0, BOT_RAIL_Z, sy))
        p.append(_sy_box(-BX, BX, DECK_RAIL_Y0, RAIL_Y1, DECK_Z0, DECK_Z1, sy))
    # floor cross bars (bank rests on them), plus an X brace so the cradle carries torsion alone
    for xc in FLOOR_BAR_X:
        p.append(box(xc - FLOOR_BAR_W / 2, xc + FLOOR_BAR_W / 2, -RAIL_Y0 - 0.01, RAIL_Y0 + 0.01, 0, FLOOR_Z))
    for sy in (1, -1):
        L = math.hypot(2 * (BX - 4), 2 * RAIL_Y0)
        ang = math.degrees(math.atan2(sy * 2 * RAIL_Y0, 2 * (BX - 4)))
        p.append(cq.Workplane('XY').box(L, 5.0, FLOOR_Z, centered=(True, True, False)).rotate((0, 0, 0), (0, 0, 1), ang))
    # side trusses between the rails: verticals + diagonals, mirrored front/rear
    verts = (0.0, 30.0, 59.5)
    for sy in (1, -1):
        y0, y1 = sorted((sy * RAIL_Y0, sy * RAIL_Y1))
        for sx in (1, -1):
            for xc in verts:
                if xc == 0.0 and sx < 0:
                    continue
                w = 6.0
                x0 = sx * xc - w / 2 if abs(xc) < 59 else (sx * BX - (w if sx > 0 else 0))
                x1 = x0 + w
                p.append(box(x0, x1, y0, y1, BOT_RAIL_Z - 0.01, DECK_Z0 + 0.01))
            a, b = (sx * 3.0, BOT_RAIL_Z - 1.0), (sx * 29.0, DECK_Z0 + 1.0)
            c, d = (sx * 33.0, BOT_RAIL_Z - 1.0), (sx * 58.0, DECK_Z0 + 1.0)
            p.append(_strut(a[0], a[1], b[0], b[1], 4.5, y0, y1))
            p.append(_strut(c[0], c[1], d[0], d[1], 4.5, y0, y1))
    # deck end cross bars only, none under a servo body: the whole bay under each hip servo pair stays open
    for sx in (1, -1):
        p.append(box(*sorted((sx * OUTER_BAR_X[0], sx * BX)), -DECK_RAIL_Y0 - 0.01, DECK_RAIL_Y0 + 0.01, DECK_Z0, DECK_Z1))
        p.append(box(*sorted((sx * INNER_DECK_X[0], sx * INNER_DECK_X[1])), -DECK_RAIL_Y0 - 0.01, DECK_RAIL_Y0 + 0.01, DECK_Z0, DECK_Z1))
    # bank rear corner stops, below the USB ports
    for sy in (1, -1):
        p.append(_sy_box(BANK['x0'] - 3.0, BANK['x0'], 28.0, RAIL_Y0 + 0.01, 0, 6.5, sy))
    # columns: one corner column per hip, bolted joint columns toward the middle (D22), one mid column per side
    for sx in (1, -1):
        for sy in (1, -1):
            x0, x1 = sorted((sx * OUTER_COL_X[0], sx * OUTER_COL_X[1]))
            y0, y1 = sorted((sy * COL_Y0, sy * COL_Y1))
            p.append(box(x0, x1, y0, y1, DECK_Z0, SADDLE_Z0))
            p.append(_fillet_ring(x0, x1, y0, y1, DECK_Z1))
            if not (sx < 0 and sy > 0):      # U1 contract box: no joint column at the rear +Y
                x0, x1 = sorted((sx * JOINT_XS[0], sx * JOINT_XS[1]))
                p.append(box(x0, x1, y0, y1, DECK_Z0, COL_TOP))
                p.append(_fillet_ring(x0, x1, y0, y1, DECK_Z1))
    for sy in (1, -1):
        y0, y1 = sorted((sy * COL_Y0, sy * COL_Y1))
        p.append(box(MID_COL_X[0], MID_COL_X[1], y0, y1, DECK_Z0, COL_TOP))
        p.append(_fillet_ring(MID_COL_X[0], MID_COL_X[1], y0, y1, DECK_Z1))
    p += board_seats()
    s = _union(p)
    # bank void (front slide-out), kept clear of every bar above the floor
    s = s.cut(box(BANK['x0'], BX + 1, -RAIL_Y0, RAIL_Y0, FLOOR_Z, DECK_Z0))
    s = s.cut(board_seat_cuts())
    for (x, y) in JOINT_SCREWS:
        s = s.cut(cyl(x, y, COL_TOP - 6.9, COL_TOP + 0.01, JOINT_PILOT))
    # outer corner chamfers only: extra margin for the foot sweeping past the frame corners
    for sx in (1, -1):
        for sy in (1, -1):
            corner = (cq.Workplane('XY').polyline([(sx * (BX + 0.01), sy * (COL_Y1 + 0.01)), (sx * (BX - 3.0), sy * (COL_Y1 + 0.01)), (sx * (BX + 0.01), sy * (COL_Y1 - 3.0))]).close().extrude(COL_TOP + 1).translate((0, 0, -0.5)))
            s = s.cut(corner)
    return s.clean()


def board_seats():
    """Seat under every board hole: an open saddle tied into the deck rail or the rear cross bar, top at the board bottom."""
    out = []
    for h in BOARD_HOLES:
        x, y = h['xy']
        sy = 1 if y > 0 else -1
        w = SEAT_W / 2
        x0, x1 = max(x - w, -46.0), min(x + w, 46.0)
        if abs(y) >= 20.0:                 # near the side rail: saddle runs into it
            y0, y1 = sorted((y - sy * w, sy * (DECK_RAIL_Y0 + 0.5)))
        else:                              # H1: on the rear cross bar, with a bar out to the side rail
            y0, y1 = y - w, y + w
            out.append(box(x0, x0 + 6.0, y1 - 0.01, DECK_RAIL_Y0 + 0.5, DECK_Z0, 20.7))
            out.append(box(-46.0, x0 + 0.01, y0, y1, DECK_Z0, DECK_Z1)) if x0 > -46.0 else None
        out.append(box(x0, x1, y0, y1, DECK_Z0, BOARD_ZB))
    return out


def board_seat_cuts():
    """M3x6 from the board top into an M3 nut dropped in a hex well; tip clearance below it."""
    out = []
    for h in BOARD_HOLES:
        x, y = h['xy']
        out.append(cyl(x, y, BOARD_ZT - 6.0 - 0.2, BOARD_ZB + 0.01, M3_CLEAR))
        out.append(hexprism_z(0, 0, BOARD_ZB - NUT_WELL_D, BOARD_ZB + 0.01, NUT_AF + 0.3).rotate((0, 0, 0), (0, 0, 1), 30).translate((x, y, 0)))
    return _union(out)


def frame_upper():
    p = []
    for sy in (1, -1):
        p.append(_sy_box(-BX, BX, 34.0, RAIL_Y1, UPPER_RAIL_Z0, TAB_Z1, sy))         # side rails
    for sg in (1, -1):
        X = lambda a, b: tuple(sorted((sg * a, sg * b)))
        p.append(box(*X(*OUTER_BAR_X), -BY, BY, UPPER_RAIL_Z0, TAB_Z1))                # outer end bar
        p.append(box(*X(*INNER_BAR_X), -BY, BY, UPPER_RAIL_Z0, TAB_Z1))                # inner end bar
        # centre saddle (both servos of the pair sit their inner tab here) and corner saddles; open below, no pocket, no cup
        p.append(box(*X(INNER_BAR_X[1] - 0.1, OUTER_BAR_X[0] + 0.1), -CENTRE_SADDLE_Y, CENTRE_SADDLE_Y, SADDLE_Z0, TAB_Z0))
        for sy in (1, -1):
            p.append(_sy_box(*X(INNER_BAR_X[1] - 0.1, BX), OUTER_SADDLE_Y0, RAIL_Y1, SADDLE_Z0, TAB_Z0, sy))
        # LED/screen beams from the hip block to the strip. The rear +Y beam would pass through the display (D27), so it is left out:
        # the strip's rear end is carried by the -Y beam and by the screen rim on the +Y side rail.
        for sy in (1, -1):
            if sg < 0 and sy > 0:
                continue
            p.append(_sy_box(*X(STRIP_END_X - 4.4, INNER_BAR_X[0] + 1.05), LED_BEAM_Y[0], LED_BEAM_Y[1], UPPER_RAIL_Z0, TAB_Z1, sy))
            p.append(_sy_box(*X(STRIP_END_X - 4.4, STRIP_END_X), LED_BEAM_Y[0], LED_BEAM_Y[1], TAB_Z1 - 0.01, LID_Z1, sy))
    # joint pads on the side rails
    for (x, y) in JOINT_SCREWS:
        sy = 1 if y > 0 else -1
        x0, x1 = sorted((math.copysign(JOINT_XS[0], x), math.copysign(JOINT_XS[1], x)))
        p.append(_sy_box(x0, x1, COL_Y0, 34.05, UPPER_RAIL_Z0, TAB_Z1, sy))
    # open head: LED strip and screen rim only
    p.append(box(-STRIP_END_X, STRIP_END_X, -LED_BEAM_Y[1], LED_BEAM_Y[1], LID_Z0, LID_Z1))
    # screen rim: open at the rear end (the module overlaps the inner bar line) and open at the front between two corner tabs, so the J10 wires rise free
    rim_x0, rim_front = -46.5, DISP_X1 + 0.3
    p.append(box(rim_x0, rim_front, LED_BEAM_Y[0] - 0.01, BY, LID_Z0, LID_Z1))
    p.append(box(rim_x0, -33.8, -6.0, LED_BEAM_Y[0], LID_Z0, LID_Z1))                 # -Y rear stringer behind the LED channel
    p.append(box(-46.15, -40.15, -6.0, 0.0, TAB_Z1 - 0.01, LID_Z0 + 0.01))     # 6 x 6 post carrying it to the inner end bar
    for y0, y1 in ((LED_BEAM_Y[0] - 0.01, 13.0), (27.5, BY)):
        p.append(box(rim_front - 0.01, rim_front + 6.0, y0, y1, 42.0, LID_Z1))          # front corner tabs: +X stop for the PCB, clear of the J10 wire span y 13..27.5
    # webs tying the screen rim down to the +Y side rail
    for xc in (-43.0, 2.0):
        p.append(box(xc - 3.0, xc + 3.0, 34.0, BY, TAB_Z1 - 0.01, LID_Z0 + 0.01))
    s = _union(p)
    # SG90 bag screw pilots, through the saddle (a longer screw just pokes out below); no nut, no drilling
    for (x, y) in TAB_PILOTS:
        s = s.cut(cyl(x, y, SADDLE_Z0 - 1, TAB_Z0 + 0.1, TAB_PILOT))
    for (x, y) in JOINT_SCREWS:
        s = s.cut(cyl(x, y, UPPER_RAIL_Z0 - 1, TAB_Z1 + 1, M3_CLEAR))
    # LED diffuser channel from below (0.8 skin), one tie slot beyond each bar end
    s = s.cut(box(-29.0, 29.0, -LED_CH_HALF_Y, LED_CH_HALF_Y, LID_Z0 - 0.01, LID_Z1 - 0.8))
    for sx in (1, -1):
        x0, x1 = sorted((sx * 29.5, sx * 31.0))     # the tie runs under the bar, up through this slot and around the strip end
        s = s.cut(box(x0, x1, -1.8, 1.8, LID_Z0 - 1, LID_Z1 + 1))
    # local relief over RESET so a pin reaches it from the open -Y side (the strip is not load-bearing here)
    s = s.cut(box(-13.9, -2.0, -LED_BEAM_Y[1] - 0.1, -7.2, LID_Z0 - 1, LID_Z1 + 1))
    # screen: PCB rim pocket, panel through-window, tie slots
    s = s.cut(box(DISP_X0 - 0.3, DISP_X1 + 0.3, DISP_Y0 - 0.3, DISP_Y1 + 0.3, LID_Z0 - 0.01, DISP['z_ledge']))
    w = DISP_WIN
    s = s.cut(box(w['x0'], w['x1'], w['y0'], w['y1'], LID_Z0 - 1, LID_Z1 + 1))
    # two zip ties across the module back: up through a slot in each stringer and around its outer edge
    for tx in DISP_TIE_X:
        for y0, y1 in ((2.0, 3.3), (34.6, 35.9)):
            s = s.cut(box(tx - 1.8, tx + 1.8, y0, y1, LID_Z0 - 1, LID_Z1 + 1))
    # the inner bar under the module rear end is removed so the module lifts straight into its rim; its -Y half still ties the centre saddle
    s = s.cut(box(-46.2, -42.95, DISP_Y0 - 0.3, DISP_Y1 + 0.3, UPPER_RAIL_Z0 - 1, TAB_Z1 + 1))
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

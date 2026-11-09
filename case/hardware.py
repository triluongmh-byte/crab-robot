"""Bought hardware instances (single source for CAD checks, fastener_map.csv and the overview).

Only the owner's set: M3x6/8/12/20 + M3 nuts, plus the screws that come in each SG90 bag.
All positions are in the assembled robot frame at the neutral pose.
"""
import math
import model as M

CORNERS = ('FL', 'FR', 'RL', 'RR')
CORNER_SIGN = {'FL': (1, 1), 'FR': (1, -1), 'RL': (-1, 1), 'RR': (-1, -1)}


def _leg_point(corner, r, t, z):
    """FL leg-frame point (r, t, z) -> assembled frame for any corner (true mirror)."""
    a = math.radians(45)
    x = M.HIP_X + r * math.cos(a) - t * math.sin(a)
    y = M.HIP_Y + r * math.sin(a) + t * math.cos(a)
    sx, sy = CORNER_SIGN[corner]
    return (sx * x, sy * y, z)


def _leg_dir(corner, dr, dt, dz):
    a = math.radians(45)
    x = dr * math.cos(a) - dt * math.sin(a)
    y = dr * math.sin(a) + dt * math.cos(a)
    sx, sy = CORNER_SIGN[corner]
    return (sx * x, sy * y, dz)


def instances():
    """List of dicts: id, kind, size, head xyz, axis (unit vector from head toward tip), length,
    nut (xyz or None), parts it joins, step, entry, action."""
    out = []
    # cap clamp screws: M3x20 from the cap top, nut in a side slot of the base corner block
    k = 1
    for sx, label in ((1, 'trước'), (-1, 'sau')):
        for (cx, cy) in M.CAP_SCREW_XY:
            x, y = sx * cx, cy
            out.append(dict(id=f'C{k}', kind='M3', size='M3x20', length=20.0, head=(x, y, M.LID_Z1),
                            axis=(0, 0, -1), nut=(x, y, 28.2 + M.NUT_T / 2), nut_entry=(0, 1 if y > 0 else -1, 0),
                            parts=[f'cap_{"front" if sx > 0 else "rear"}', 'base'],
                            step=3 if sx > 0 else 3, entry='từ trên xuống (đầu vít trên thanh đè)',
                            action=f'Đẩy tán M3 vào khe hông thân ({label}, mặt {"trái" if y > 0 else "phải"}), vặn vít M3x20 qua thanh đè tới khi chặt, không siết quá.'))
            k += 1
    # board screws: M3x6 from the board top into a nut dropped in a hex well of the seat
    for i, h in enumerate(M.BOARD_HOLES, start=1):
        x, y = h['xy']
        out.append(dict(id=f'B{i}', kind='M3', size='M3x6', length=6.0, head=(x, y, M.BOARD_ZT),
                        axis=(0, 0, -1), nut=(x, y, M.BOARD_ZB - M.NUT_WELL_D + M.NUT_T / 2), nut_entry=(0, 0, 1),
                        parts=['board', 'base'], step=6, entry='từ trên board xuống khối đỡ',
                        action='Thả tán M3 vào hốc lục giác trên khối đỡ trước (Bước 6). Đặt board, vặn vít M3x6 qua lỗ board.'))
    # lid screws: M3x8 through the lid, self-tapping into a pilot in the rail-end pads (no nut)
    for i, (x, y) in enumerate(M.LID_SCREWS, start=1):
        out.append(dict(id=f'L{i}', kind='M3', size='M3x8', length=8.0, head=(x, y, M.LID_Z1),
                        axis=(0, 0, -1), nut=None, parts=['lid', 'base'], step=7, entry='từ trên nắp xuống',
                        action='Vặn vít M3x8 qua nắp, vít tự ăn ren vào lỗ dẫn Ø2.7 trên pad; đừng siết quá.'))
    # SG90 bag screws (factory, not M3): hip horn centre + horn arm, knee tabs, knee horn arm + centre
    for c in CORNERS:
        hub_top = M.SERVO_Z0 + M.HORN['hub_z0'] + M.HORN['hub_h']
        out.append(dict(id=f'H{c}-arm', kind='SG90', size='vít tự ren nhỏ túi SG90', length=6.0,
                        head=_leg_point(c, M.HORN['hole_r'], 0, hub_top - M.HORN['arm_t']), axis=(0, 0, 1), nut=None,
                        parts=[f'thigh_{c}', 'horn hông'], step=4, entry='từ dưới lên, xuyên lỗ tay horn vào đùi',
                        action='Ép horn 1 tay vào rãnh dưới đùi, bắt 1 vít nhỏ túi SG90 qua lỗ tay horn.'))
        out.append(dict(id=f'H{c}-ctr', kind='SG90', size='vít tâm horn túi SG90', length=4.0,
                        head=_leg_point(c, 0, 0, hub_top + 0.1), axis=(0, 0, -1), nut=None,
                        parts=[f'thigh_{c}', f'SG90 hông {c}'], step=8, entry='từ trên xuống qua lỗ Ø6 của đùi',
                        action='Đặt đùi (đã có horn) lên trục servo hông ở góc giữa, vặn vít tâm.'))
        cxs = M.R_KNEE - M.SG['shaft_off'] + M.SG['L'] / 2
        for j, rx in enumerate((cxs - M.SG['tab_span'] / 2 + 2.3, cxs + M.SG['tab_span'] / 2 - 2.3)):
            tab_face = M.T_SERVO_B + M.SG['tab_z0'] + M.SG['tab_t']
            out.append(dict(id=f'K{c}-tab{j + 1}', kind='SG90', size='vít bắt tai túi SG90', length=8.0,
                            head=_leg_point(c, rx, tab_face, M.Z_KNEE), axis=_leg_dir(c, 0, -1, 0), nut=None,
                            parts=[f'thigh_{c}', f'SG90 gối {c}'], step=4, entry='xuyên lỗ tai servo vào tấm đùi',
                            action='Luồn servo gối qua ô của tấm đùi, bắt 2 vít tai túi SG90.'))
        horn_face = M.FOOT_T0
        out.append(dict(id=f'K{c}-arm', kind='SG90', size='vít tự ren nhỏ túi SG90', length=6.0,
                        head=_leg_point(c, M.R_KNEE, horn_face + 2.0, M.Z_KNEE - M.HORN['hole_r']),
                        axis=_leg_dir(c, 0, 1, 0), nut=None, parts=[f'foot_{c}', 'horn gối'], step=4,
                        entry='từ phía horn, xuyên lỗ tay horn vào cẳng',
                        action='Ép horn 1 tay vào rãnh cẳng (tay horn hướng xuống), bắt 1 vít nhỏ túi SG90.'))
        out.append(dict(id=f'K{c}-ctr', kind='SG90', size='vít tâm horn túi SG90', length=4.0,
                        head=_leg_point(c, M.R_KNEE, M.FOOT_T1 + 0.1, M.Z_KNEE), axis=_leg_dir(c, 0, -1, 0), nut=None,
                        parts=[f'foot_{c}', f'SG90 gối {c}'], step=8, entry='từ ngoài vào qua lỗ Ø6 của cẳng',
                        action='Lắp cẳng lên trục servo gối ở góc giữa (cẳng thẳng đứng), vặn vít tâm.'))
    return out


def m3_count():
    return sum(1 for h in instances() if h['kind'] == 'M3')

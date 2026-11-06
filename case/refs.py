"""Non-printed reference solids for checks and the overview (servos, modules, screws/nuts)."""
import cadquery as cq
import geometry as g


def _fuse(ws):
    out = ws[0]
    for w in ws[1:]:
        out = out.union(w)
    return out


def hip_servos():
    return {f'{n}_hip': g.sg90_hip(g.LEGS[n][0], g.LEGS[n][1]) for n in g.LEGS}


def knee_servos(hip_deg=0.0):
    return {f'{n}_knee': g.leg_posed(g.knee_servo_local(), n, hip_deg) for n in g.LEGS}


def horns():
    out = {}
    for n in g.LEGS:
        h = g.horn_solid().translate((0, 0, g.HORN_TOP_Z))
        out[f'{n}_hip_horn'] = g.leg_posed(h, n)
        # knee horn: flat face at t = KNEE_HORN_T, arm along the tibia, axis along +t
        import math
        dx, dz = g.FOOT_R - g.LEG_R_KNEE, g.FOOT_Z - g.KNEE_AXIS_Z
        ang = math.degrees(math.atan2(dz, dx))
        k = g.horn_solid().mirror('XY').rotate((0, 0, 0), (0, 0, 1), ang).translate((g.LEG_R_KNEE, g.KNEE_AXIS_Z, -g.KNEE_HORN_T))
        k = k.rotate((0, 0, 0), (1, 0, 0), 90)
        out[f'{n}_knee_horn'] = g.leg_posed(k, n)
    return out


def servos():
    return _fuse(list(hip_servos().values()) + list(knee_servos().values()) + list(horns().values()))


def modules():
    return _fuse(list(g.modules_ref().values()))


def hardware():
    ws = []
    for f in g.fasteners():
        ws.append(g.screw(f['x'], f['y'], f['zhead'], f['L']))
        ws.append(g.nut(f['x'], f['y'], f['nut']))
    return _fuse(ws)

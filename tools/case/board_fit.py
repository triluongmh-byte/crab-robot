"""Does a board contract fit the robot body? -> case/reports/board-fit.json (no CAD booleans, < 2 s).

Compares the board outline, tall parts (with the measured overrides in case/board_placement.json) and the USB-C plug
against the keep-outs of the current base, using the same constants as case/model.py.
Usage: case-python tools/case/board_fit.py [enclosure.json] [--out PATH]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'case'))


def boxes_hit(a, b):
    return a[0] < b[1] and a[1] > b[0] and a[2] < b[3] and a[3] > b[2] and a[4] < b[5] and a[5] > b[4]


def keepouts(M):
    k = []
    for sg in (1, -1):
        X = lambda a, b: tuple(sorted((sg * a, sg * b)))
        t = M.USB_TUNNEL
        for ya, yb in ((-34, -t['y']), (t['y'], 34)) if sg < 0 else ((-34, 34),):
            k += [('hip pocket inner wall (below the slot top)', *X(M.SLOT_X, 47.0), ya, yb, 21.5, M.SLOT_TOP),
                  ('hip pocket inner wall', *X(44.0, 47.0), ya, yb, M.SLOT_TOP, M.TAB_Z1)]
        if sg < 0:
            k += [('hip pocket inner wall (below the USB tunnel)', *X(44.0, 47.0), -t['y'], t['y'], 21.5, t['z0']),
                  ('hip pocket inner wall (above the USB tunnel)', *X(44.0, 47.0), -t['y'], t['y'], t['z1'], M.TAB_Z1)]
        k += [
              ('cap-screw corner block', *X(40.0, 47.0), M.SLOT_Y, 34, 21.5, M.TAB_Z1), ('cap-screw corner block', *X(40.0, 47.0), -34, -M.SLOT_Y, 21.5, M.TAB_Z1),
              ('cap-screw corner block', *X(40.0, 47.0), 26.5, 34, M.SLOT_TOP, M.TAB_Z1), ('cap-screw corner block', *X(40.0, 47.0), -34, -26.5, M.SLOT_TOP, M.TAB_Z1),
              ('clamp bar (frozen plate 2)', *X(40.0, 62.5), -37, 37, M.TAB_Z1, M.LID_Z1)]
    t = M.USB_TUNNEL
    k += [('front central block', 44.0, 59.5, -5.8, 5.8, 21.5, M.TAB_Z0),
          ('rear central block below the USB tunnel', -59.5, -44.0, -5.8, 5.8, 21.5, t['z0']),
          ('rear central block above the USB tunnel', -59.5, -44.0, -5.8, 5.8, t['z1'], M.TAB_Z0),
          ('side rail -Y', -62.5, 62.5, -37, -34, M.RAIL_Z0, M.LID_Z0), ('side rail +Y', -62.5, 62.5, 34, 37, M.RAIL_Z0, M.LID_Z0)]
    for s in (1, -1):
        k.append(('hip servo end', 47.15 * s if s > 0 else -59.35, 59.35 if s > 0 else -47.15, 5.9, 28.7, 21.5, 44.2))
        k.append(('hip servo end', 47.15 * s if s > 0 else -59.35, 59.35 if s > 0 else -47.15, -28.7, -5.9, 21.5, 44.2))
    led = M.LED
    k.append(('LED bar', -28, 28, -6, 6, led['cz'] - led['sz'] / 2, led['cz'] + led['sz'] / 2))
    for lab, x0, x1, y0, y1, z0, z1 in M.disp_back_boxes():
        k.append((f'display {lab}', x0, x1, y0, y1, z0, z1))
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('--out', default=str(ROOT / 'case/reports/board-fit.json'))
    a = ap.parse_args()
    import model as M
    e = json.loads(Path(a.src).read_text()) if a.src else M._EC
    kout = keepouts(M)
    t = e['board']['thicknessMm']
    zb, zt = M.BOARD_ZB, M.BOARD_ZB + t
    w, h = e['board']['widthMm'], e['board']['heightMm']
    outline = (-w / 2 + M._PLACE['dxMm'], w / 2 + M._PLACE['dxMm'], -h / 2 + M._PLACE['dyMm'], h / 2 + M._PLACE['dyMm'], zb, zt)
    findings = [{'item': 'board outline', 'hits': k[0]} for k in kout if boxes_hit(outline, k[1:])]
    parts = []
    for p in e.get('parts', []):
        if p.get('heightMm', 0) <= 2.5 or p.get('side') != 'top':
            continue
        q = dict(p, boxMm=M._part_box(p), heightMm=M._top_h(p))
        x0, y0, x1, y1 = M.board_box(q['boxMm'])
        b = (x0, x1, y0, y1, zt, zt + q['heightMm'])
        hits = [k[0] for k in kout if boxes_hit(b, k[1:])]
        parts.append({'ref': p['ref'], 'topZ': round(b[5], 2), 'heightUsedMm': q['heightMm'],
                      'heightSource': 'board_placement override' if p['ref'] in M._H_OVR or p['ref'] in M._BOX_OVR else ('seated plug' if q['heightMm'] != p['heightMm'] else 'contract'),
                      'hits': hits, 'pass': not hits})
    usb = next((i for i in e.get('interfaces', []) if i.get('kind') == 'usb'), None)
    usb_rep = {'found': bool(usb)}
    if usb:
        ux, uy = M.board_xy(*usb['centerMm'])
        ax, ay = usb.get('access', [0, 0, 0])[:2]
        pw, ph = M.USB_PLUG_REAL
        zc = zt + usb.get('zMm', 3.3) / 2
        mouth = usb.get('sizeMm', [9.5, 10.7])[0] / 2
        px, py = ux + ax * mouth, uy + ay * mouth
        x = sorted((px, px + ax * 15.0)) if ax else [px - pw / 2, px + pw / 2]
        y = sorted((py, py + ay * 15.0)) if ay else [py - pw / 2, py + pw / 2]
        if ax and not ay:
            y = [py - pw / 2, py + pw / 2]
        pb = (x[0], x[1], y[0], y[1], zc - ph / 2, zc + ph / 2)
        hits = [k[0] for k in kout if boxes_hit(pb, k[1:])]
        usb_rep.update({'plugBoxRobotMm': [round(v, 2) for v in pb], 'plugSizeMm': list(M.USB_PLUG_REAL), 'hits': hits, 'pass': not hits})
    res = {'schema': 1, 'source': str(a.src or M._PLACE['source']), 'board': e['board'], 'placement': {'dx': M._PLACE['dxMm'], 'dy': M._PLACE['dyMm'], 'zBottom': zb},
           'outlineRobotMm': [round(v, 2) for v in outline], 'outlineFindings': findings, 'usb': usb_rep, 'tallParts': parts,
           'fits': not findings and usb_rep.get('pass', False) and all(p['pass'] for p in parts),
           'note': 'Boxes only. mechanical.json and native-case-check.json are the checks of the real solids.'}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'fits': res['fits'], 'outlineHits': len(findings), 'usb': usb_rep.get('pass'), 'partHits': [p['ref'] for p in parts if not p['pass']]}))
    return 0 if res['fits'] else 2


if __name__ == '__main__':
    sys.exit(main())

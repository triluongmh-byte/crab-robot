"""Arranged Bambu Studio projects for the crab case.

  case/print/production.3mf   Print all: every production part on named plates (owner's PETG profile)
  case/print/test-only.3mf    TEST ONLY coupon (separate project)
  case/print/mating-test.3mf  MATING_TEST: the real thigh_FL + foot_FL (separate project)
  case/print/production-check.json   verifier report (layout + real Bambu CLI slice estimates)

Plate assignment follows case/PRINTED-INVENTORY.md / print/events.jsonl: parts confirmed printed go to
"ĐÃ IN — GIỮ LẠI" plates, the rest to "MỚI/SỬA — CẦN IN". Never sends anything to a printer.
Skips work when meshes, rotations, inventory and this file are unchanged.
"""
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/robot'
BOARD_OUT = ROOT / 'case/out'   # board-frame copies the tile binds to; meshes here are rigid z translates of case/robot
PRINT = ROOT / 'case/print'
SETTINGS = ROOT / 'case/print-settings.json'
BAMBU = Path('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio')
BED = (256.0, 256.0, 256.0)
EDGE = 8.0          # bed edge margin (brim 5 mm + skirt)
GAP = 14.0          # part-to-part gap (two 5 mm auto brims + 4 mm)
PLATE_PITCH = BED[0] * 1.2   # Bambu Studio lays plates out with a 1/5 bed gap
LIMIT_PLATE_S = 4.5 * 3600
LIMIT_TOTAL_S = 8 * 3600
LIMIT_G = 220.0
sys.path.insert(0, str(ROOT / 'case'))
sys.path.insert(0, str(Path(__file__).parent))
import plate2_freeze as FREEZE


def sha(b):
    return hashlib.sha256(b).hexdigest()


def stl_tris(path):
    d = path.read_bytes()
    n = int.from_bytes(d[80:84], 'little')
    a = np.frombuffer(d[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n)
    return a['v'].reshape(-1, 3, 3).astype(float)


def rotate(P, r):
    P = P.copy()
    for axis, deg in enumerate(r):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        x, y, z = P[..., 0].copy(), P[..., 1].copy(), P[..., 2].copy()
        if axis == 0:
            P[..., 1], P[..., 2] = y * c - z * s, y * s + z * c
        elif axis == 1:
            P[..., 0], P[..., 2] = x * c + z * s, -x * s + z * c
        else:
            P[..., 0], P[..., 1] = x * c - y * s, x * s + y * c
    return P


def oriented(name, rot):
    T = rotate(stl_tris(OUT / f'{name}.stl'), rot)
    mn = T.reshape(-1, 3).min(0)
    mx = T.reshape(-1, 3).max(0)
    T = T - np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    return T, (mx - mn)


SKELETON_REVISION = 'A1V4-r5'
# Owner's completion report (release note 6) and bars-removed report (notes 7, 8): 8 leg parts printed. Clamp bars are not production parts.
OWNER_REPORTED_PRINTED = set(FREEZE.PLATE2)


def printed_parts():
    """Parts confirmed physically printed (print/events.jsonl, else PRINTED-INVENTORY.md table)."""
    done = set(OWNER_REPORTED_PRINTED)
    ev = ROOT / 'print/events.jsonl'
    if ev.exists():
        for line in ev.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get('kind') in ('printed', 'print_confirmed') or e.get('status') == 'printed':
                for p in e.get('parts', []):
                    done.add(p['name'] if isinstance(p, dict) else p)
    return done


def shelf_pack(items, bed_w, bed_d):
    """items: (name, sx, sy). Rows along X (long sides along X). Returns placements or None."""
    x, y, row_h, out = EDGE, EDGE, 0.0, []
    for name, sx, sy in items:
        if x + sx > bed_w - EDGE + 1e-6:
            x, y, row_h = EDGE, y + row_h + GAP, 0.0
        if y + sy > bed_d - EDGE + 1e-6 or sx > bed_w - 2 * EDGE:
            return None
        out.append((name, x + sx / 2, y + sy / 2))
        x += sx + GAP
        row_h = max(row_h, sy)
    return out


def mesh_xml(oid, T):
    V, idx = {}, []
    verts = []
    for tri in T:
        ids = []
        for v in tri:
            k = (round(v[0], 4), round(v[1], 4), round(v[2], 4))
            if k not in V:
                V[k] = len(verts)
                verts.append(k)
            ids.append(V[k])
        if len(set(ids)) == 3:
            idx.append(ids)
    vs = ''.join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in verts)
    ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in idx)
    return f'<object id="{oid}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>'


def write_3mf(path, plates, title):
    """plates: [(plate_name, [(part_name, T_oriented, cx, cy)])]."""
    settings = json.loads(SETTINGS.read_text())['settings']
    objs, items, cfg_objs, cfg_plates = [], [], [], []
    oid = 0
    cols = max(1, math.ceil(math.sqrt(len(plates))))
    for pi, (pname, parts) in enumerate(plates):
        col, row = pi % cols, pi // cols
        ox, oy = col * PLATE_PITCH, -row * PLATE_PITCH
        inst = []
        for name, T, cx, cy in parts:
            oid += 1
            objs.append(mesh_xml(oid, T))
            items.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {ox + cx:.4f} {oy + cy:.4f} 0" printable="1"/>')
            cfg_objs.append(f'<object id="{oid}"><metadata key="name" value="{name}.stl"/><metadata key="extruder" value="1"/>'
                            f'<part id="{oid}" subtype="normal_part"><metadata key="name" value="{name}"/></part></object>')
            inst.append(f'<model_instance><metadata key="object_id" value="{oid}"/><metadata key="instance_id" value="0"/>'
                        f'<metadata key="identify_id" value="{100 + oid}"/></model_instance>')
        cfg_plates.append(f'<plate><metadata key="plater_id" value="{pi + 1}"/><metadata key="plater_name" value="{pname}"/>'
                          f'<metadata key="locked" value="false"/>{"".join(inst)}</plate>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
             f'<metadata name="Application">BambuStudio-02.07.01.62</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'
             f'<metadata name="Title">{title}</metadata>'
             f'<resources>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    cfg = '<?xml version="1.0" encoding="UTF-8"?>\n<config>' + ''.join(cfg_objs) + ''.join(cfg_plates) + '</config>'
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            '</Relationships>')
    tmp = path.with_suffix('.tmp')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in (('[Content_Types].xml', ct), ('_rels/.rels', rels), ('3D/3dmodel.model', model),
                           ('Metadata/model_settings.config', cfg),
                           ('Metadata/project_settings.config', json.dumps(settings, indent=1))):
            zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)
    tmp.replace(path)


def slice_estimates(src):
    """Slice every plate with the Bambu Studio CLI (no printer contact); return per-plate time/filament."""
    if not BAMBU.exists():
        return None, 'Bambu Studio CLI not found'
    work = ROOT / 'build/case/slice' / src.stem
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    out3 = work / 'sliced.3mf'
    cmd = [str(BAMBU), '--slice', '0', '--export-3mf', out3.name, '--outputdir', str(work), '--debug', '1', str(src)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=work)
    log = (r.stdout or '') + (r.stderr or '')
    (work / 'cli.log').write_text(log)
    if r.returncode or not out3.exists():
        return None, f'CLI exit {r.returncode}: ' + log[-800:]
    plates = []
    with zipfile.ZipFile(out3) as z:
        names = z.namelist()
        info = z.read('Metadata/slice_info.config').decode() if 'Metadata/slice_info.config' in names else ''
        for m in re.finditer(r'<plate>(.*?)</plate>', info, re.S):
            body = m.group(1)
            g = lambda k: (re.search(rf'key="{k}" value="([^"]*)"', body) or [None, None])[1]
            fil = [(float(a), float(b)) for a, b in re.findall(r'used_m="([\d.]+)" used_g="([\d.]+)"', body)]
            warn = re.findall(r'<warning msg="([^"]*)"', body)
            plates.append({'index': int(g('index')), 'savedName': None, 'predictionS': float(g('prediction') or 0), 'weightG': float(g('weight') or 0),
                           'filamentM': round(sum(a for a, _ in fil), 2), 'supportUsed': g('support_used'), 'warnings': warn})
        cfg = z.read('Metadata/model_settings.config').decode() if 'Metadata/model_settings.config' in names else ''
    saved = dict((int(a), b) for a, b in re.findall(r'plater_id" value="(\d+)"/>\s*<metadata key="plater_name" value="([^"]*)"', cfg))
    for p in plates:
        p['savedName'] = saved.get(p['index'])
    return {'plates': plates, 'cli': ' '.join(cmd[1:6]) + ' ...', 'log': str(work.relative_to(ROOT) / 'cli.log')}, None


def main():
    man = json.loads((OUT / 'parts.json').read_text())
    prod = [p for p in man['parts'] if p.get('printable', True) and p['role'] != 'coupon']
    key = hashlib.sha256()
    for p in prod + [x for x in man['parts'] if x['role'] == 'coupon']:
        key.update(p['name'].encode()); key.update(json.dumps(p.get('printRotateDeg')).encode())
        key.update((OUT / p['stl']).read_bytes())
    key.update(Path(__file__).read_bytes())
    key.update((Path(__file__).parent / 'plate2_freeze.py').read_bytes())
    key.update((ROOT / 'case/frozen-plate2-A1V4-r1.json').read_bytes())
    inv = ROOT / 'case/PRINTED-INVENTORY.md'
    ev = ROOT / 'print/events.jsonl'
    for f in (inv, ev):
        if f.exists():
            key.update(f.read_bytes())
    key = key.hexdigest()
    report_path = PRINT / 'production-check.json'
    if report_path.exists() and '--force' not in sys.argv:
        old = json.loads(report_path.read_text())
        if old.get('passed') is True and old.get('inputHash') == key and (PRINT / 'production.3mf').exists() and \
                sha((PRINT / 'production.3mf').read_bytes()) == old.get('sha256'):
            print('print project up to date'); bind(man); return 0
    PRINT.mkdir(parents=True, exist_ok=True)
    done = printed_parts()
    ori = {p['name']: oriented(p['name'], p['printRotateDeg']) for p in prod}
    errors, warnings, layout = [], [], []
    for n, (T, ext) in ori.items():
        if ext[1] > ext[0] + 1e-6:
            warnings.append(f'{n}: long side along Y ({ext[0]:.1f} x {ext[1]:.1f})')
        if ext[2] > BED[2] or max(ext[0], ext[1]) > BED[0] - 2 * EDGE:
            errors.append(f'{n} does not fit the bed: {ext}')
    # Bambu Studio 2.7 drops plate names that contain '/' or ':' -> the group slash is U+2215 '∕'
    groups = [('MỚI∕SỬA — CẦN IN', [p['name'] for p in prod if p['name'] not in done]),
              ('ĐÃ IN — GIỮ LẠI', [p['name'] for p in prod if p['name'] in done])]
    plates = []
    for gname, names in groups:
        if not names:
            continue
        rev = SKELETON_REVISION if gname.startswith('MỚI') else 'A1V4-r1'
        label = ('Khung xương MỚI A1V4-r5 (khung dưới, khung trên) — CHỌN IN PLATE NÀY' if gname.startswith('MỚI')
                 else '4 đùi 4 cẳng (bạn báo đã in và đã ráp, chưa thử chạy) — KHÔNG IN LẠI')
        if gname.startswith('ĐÃ IN'):
            # the printed leg parts keep their exact bed spots from the frozen plate 2 (the clamp bars' spots simply stay empty)
            fz = FREEZE.load()['parts']
            pl = []
            for n in names:
                t = fz[n]['transform'].split()
                pl.append((n, float(t[9]) - PLATE_PITCH, float(t[10])))
        else:
            items = sorted(((n, ori[n][1][0], ori[n][1][1]) for n in names), key=lambda t: -t[2])
            pl = shelf_pack(items, BED[0], BED[1])
        if pl is None:
            errors.append(f'{label} does not fit one plate'); continue
        plates.append((f'{gname} — {label} — PETG — {rev}', [(n, ori[n][0], cx, cy) for n, cx, cy in pl]))
    prod_file = PRINT / 'production.3mf'
    write_3mf(prod_file, plates, 'Robot Cua A1 V4 — Print all')
    # separate projects (never inside Print all)
    coupon_T, cext = oriented('coupon_TEST_ONLY', [0, 0, 0])
    write_3mf(PRINT / 'test-only.3mf', [('TEST ONLY — coupon hốc servo, rãnh horn, lỗ M3 và tán, trụ mảnh', [('coupon_TEST_ONLY', coupon_T, 128, 128)])],
              'TEST ONLY coupon')
    sad_T, sext = oriented('coupon_saddle_TEST_ONLY', [180, 0, 0])
    write_3mf(PRINT / 'test-saddle.3mf', [('TEST ONLY — yên tai servo hông thật của khung r5 (thử 1 servo, 2 vít túi)', [('coupon_saddle_TEST_ONLY', sad_T, 128, 128)])],
              'TEST ONLY saddle coupon')
    mt = [(n, ori[n][0], ori[n][1][0], ori[n][1][1]) for n in ('thigh_FL', 'foot_FL')]
    pl = shelf_pack([(n, sx, sy) for n, _, sx, sy in mt], BED[0], BED[1])
    write_3mf(PRINT / 'mating-test.3mf', [('MATING_TEST — đùi FL + cẳng FL (part thật)', [(n, ori[n][0], cx, cy) for n, cx, cy in pl])],
              'MATING_TEST leg FL')
    # verify the written project: reopen, check names, plate membership, footprints, overlap and bed bounds
    with zipfile.ZipFile(prod_file) as z:
        cfg = z.read('Metadata/model_settings.config').decode()
    names_in = re.findall(r'<plate><metadata key="plater_id" value="(\d+)"/><metadata key="plater_name" value="([^"]*)"', cfg)
    plate_rep = []
    seen = set()
    for (idx, pname), (pn, parts) in zip(names_in, plates):
        boxes = []
        recs = []
        for n, T, cx, cy in parts:
            sx, sy = ori[n][1][0], ori[n][1][1]
            b = (cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2)
            if b[0] < EDGE - 0.01 or b[1] < EDGE - 0.01 or b[2] > BED[0] - EDGE + 0.01 or b[3] > BED[1] - EDGE + 0.01:
                errors.append(f'{n} outside plate {idx} margin')
            for o, ob in boxes:
                if not (b[2] + GAP - 0.01 <= ob[0] or ob[2] + GAP - 0.01 <= b[0] or b[3] + GAP - 0.01 <= ob[1] or ob[3] + GAP - 0.01 <= b[1]):
                    errors.append(f'{n} closer than {GAP} mm to {o} on plate {idx}')
            boxes.append((n, b))
            if n in seen:
                errors.append(f'{n} twice')
            seen.add(n)
            recs.append({'name': f'{n}.stl', 'footprintMm': [round(sx, 1), round(sy, 1)], 'heightMm': round(ori[n][1][2], 1),
                         'centreMm': [round(cx, 1), round(cy, 1)],
                         'yAlongReason': None})
        plate_rep.append({'index': int(idx), 'name': pname, 'filament': 'PETG Basic Flow Rate Calibrated (1 colour)',
                          'parts': [f'{n}.stl' for n, *_ in parts], 'layout': recs})
    if seen != {p['name'] for p in prod}:
        errors.append('plates do not cover every production part exactly once')
    # frozen plate 2: same files, same meshes, same plate, same bed position as the 3MF the owner printed from
    frozen_errs = FREEZE.verify_files()
    e3mf, frozen_rows = FREEZE.verify_3mf(prod_file)
    frozen_errs += e3mf
    errors += frozen_errs
    est, err = slice_estimates(prod_file)
    limits = {}
    if est:
        for pr in plate_rep:
            e = next((x for x in est['plates'] if x['index'] == pr['index']), None)
            if e:
                pr['estimate'] = e
                if e.get('savedName') != pr['name']:
                    errors.append(f"plate {pr['index']} name not preserved by Bambu Studio: {e.get('savedName')!r}")
                if e['predictionS'] > LIMIT_PLATE_S:
                    errors.append(f"plate {pr['index']} prints {e['predictionS'] / 3600:.2f} h > 4.5 h")
        tot_s = sum(x['predictionS'] for x in est['plates'])
        tot_g = sum(x['weightG'] for x in est['plates'])
        limits = {'totalHours': round(tot_s / 3600, 2), 'totalGrams': round(tot_g, 1),
                  'plates': len(plate_rep), 'pass': tot_s <= LIMIT_TOTAL_S and tot_g <= LIMIT_G and len(plate_rep) <= 2}
        if not limits['pass']:
            errors.append(f'print limits exceeded: {limits}')
    else:
        errors.append('slicer estimate unavailable (limits unverified): ' + str(err)[-600:])
    data = prod_file.read_bytes()
    settings = json.loads(SETTINGS.read_text())['settings']
    report = {
        'schema': 1, 'passed': not errors, 'errors': errors, 'warnings': warnings,
        'file': str(prod_file.relative_to(ROOT)), 'sha256': sha(data), 'inputHash': key,
        'printer': settings.get('printer_settings_id'), 'process': settings.get('print_settings_id'),
        'filament': settings.get('filament_settings_id'),
        'profile': {k: settings.get(k) for k in ('layer_height', 'wall_loops', 'sparse_infill_density', 'sparse_infill_pattern',
                                                 'enable_support', 'support_type', 'brim_type')},
        'bedMm': list(BED), 'edgeMarginMm': EDGE, 'partGapMm': GAP,
        'meshes': [{'name': f"{p['name']}.stl", 'canonicalSTLSha256': sha((BOARD_OUT / p['stl']).read_bytes()),
                    'printRotateDeg': p.get('printRotateDeg') or [0, 0, 0]} for p in prod],
        'plates': plate_rep, 'slicer': est, 'limits': limits,
        'separateProjects': {'testOnly': 'case/print/test-only.3mf', 'testSaddle': 'case/print/test-saddle.3mf', 'matingTest': 'case/print/mating-test.3mf'},
        'printedInventory': sorted(done),
        'plate2Frozen': {'passed': not frozen_errs, 'errors': frozen_errs, 'baseline': FREEZE.load()['sourceCommit'],
                         'parts': frozen_rows, 'status': 'owner reports printed and assembled (2026-11-10, photo); both clamp bars removed and left out of Print all; not walked; not reprinted'},
        'selectForPrinting': {'plateIndex': 1, 'name': plates[0][0], 'why': 'new open bar skeleton r5: frame_lower + frame_upper (replaces base + lid; hip servos on their own tabs, no clamp bars)'},
        'checkedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'note': 'Layout verified by reopening the saved 3MF; estimates from a real Bambu Studio CLI slice of that file '
                '(no printer contacted). Physical printability/fit remain untested.',
    }
    report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'plates': [(p['index'], p['name'], len(p['parts']), p.get('estimate')) for p in plate_rep],
                      'limits': limits, 'errors': errors, 'warnings': warnings}, ensure_ascii=False, indent=1))
    if report['passed']:
        bind(man)
    return 0 if report['passed'] else 1


def bind(man):
    if man.get('printProject') != {'file': '../print/production.3mf', 'report': '../print/production-check.json'}:
        man['printProject'] = {'file': '../print/production.3mf', 'report': '../print/production-check.json'}
        (OUT / 'parts.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    sys.exit(main())

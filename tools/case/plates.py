"""Print all: one native Bambu 3MF with named plates -> case/print/production.3mf (+ TEST ONLY project).

  "$KICAD_CASE_PYTHON" tools/case/plates.py            # write 3MFs, slice with Bambu Studio CLI, verify
  "$KICAD_CASE_PYTHON" tools/case/plates.py --no-slice # layout only (fast, during repairs)
Reads print/events.jsonl (read-only ledger) to put already-printed parts on 'DA IN - GIU LAI' plates.
Skips the slicer when the STL bytes, layout and this script are unchanged.
"""
import hashlib, json, math, os, re, struct, subprocess, sys, time, zipfile
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'case/out'
PRINT = ROOT / 'case/print'
BUILD = ROOT / 'build/case/slice'
SETTINGS = ROOT / 'prompts/assets/ROBOT-CRAB-A1-V3-refs/2026-10-31-owner-native-project-settings.json'
BAMBU = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
BED = (256.0, 256.0, 256.0)
MARGIN, GAP = 8.0, 8.0          # edge margin (auto brim 5 mm fits inside), part gap
STRIDE = BED[0] * 1.2           # Bambu plate grid stride (plate width + 1/5 gap)
LIMIT_PLATE_H, LIMIT_TOTAL_H, LIMIT_G = 4.5, 8.0, 220.0
NEW = 'MỚI∕SỬA — CẦN IN'   # U+2215: Bambu Studio drops plate names that contain '/'
OLD = 'ĐÃ IN — GIỮ LẠI'

# production plates (big parts together, small parts together; one PETG colour each)
PLAN = [
    ('than', ['P01_day', 'P02_nap']),
    ('chan + thanh de', ['P03_thanh_de_truoc', 'P04_thanh_de_sau', 'P05_dui_FL', 'P06_dui_FR', 'P07_dui_RL',
                         'P08_dui_RR', 'P09_cang_FL', 'P10_cang_FR', 'P11_cang_RL', 'P12_cang_RR']),
]
TEST_PLAN = [('TEST ONLY', ['C01_TEST_ONLY_coupon', 'C02_MATING_TEST_dui_FL', 'C03_MATING_TEST_cang_FL'])]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_stl(path):
    data = Path(path).read_bytes()
    if len(data) >= 84:
        n = struct.unpack('<I', data[80:84])[0]
        if 84 + 50 * n == len(data):
            arr = np.frombuffer(data, dtype=np.uint8, offset=84).reshape(n, 50)
            return arr[:, 12:48].copy().view('<f4').reshape(n, 3, 3).astype(float)
    v = [list(map(float, m.groups())) for m in re.finditer(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', data)]
    return np.array(v, dtype=float).reshape(-1, 3, 3)


def rot(rx, ry, rz):
    def R(axis, d):
        c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
        return {0: np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), 1: np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
                2: np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])}[axis]
    return R(2, rz) @ R(1, ry) @ R(0, rx)


def ledger():
    """Already-printed part names from the read-only print ledger (explicit owner confirmations only)."""
    f = ROOT / 'print/events.jsonl'
    printed = {}
    if f.exists():
        for line in f.read_text().splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get('kind') in ('printed', 'print_confirmed', 'confirmed') or e.get('status') == 'printed':
                for p in e.get('parts', []) or [e.get('part')]:
                    name = p.get('name') if isinstance(p, dict) else p
                    if name:
                        printed[name] = e
    return printed


def orient(tris, rot_deg):
    """printRotateDeg, then a Z rotation putting the long footprint side along X; ground at z=0."""
    pts = tris.reshape(-1, 3) @ rot(*rot_deg).T
    best = None
    xy = pts[:, :2]
    for a in np.arange(0, 180, 1.0):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        q = xy @ np.array([[c, s], [-s, c]])
        ext = q.max(0) - q.min(0)
        if ext[0] + 1e-6 < ext[1]:
            continue
        if best is None or ext[1] < best[1][1] - 1e-6:
            best = (a, ext)
    a = best[0]
    Rz = rot(0, 0, a)
    pts = pts @ Rz.T
    pts -= pts.min(0)
    return pts.reshape(-1, 3, 3), a


def pack(items):
    """Shelf packing inside the bed (rows along X); returns {name: (x0, y0)} or raises."""
    items = sorted(items, key=lambda it: -it[1][1])
    pos, x, y, row_h = {}, MARGIN, MARGIN, 0.0
    for name, ext in items:
        if x + ext[0] > BED[0] - MARGIN:
            x, y, row_h = MARGIN, y + row_h + GAP, 0.0
        if y + ext[1] > BED[1] - MARGIN or ext[0] > BED[0] - 2 * MARGIN:
            raise ValueError(f'{name} does not fit the plate')
        pos[name] = (x, y)
        x += ext[0] + GAP
        row_h = max(row_h, ext[1])
    return pos


def model_xml(objects):
    res, build = [], []
    for oid, o in enumerate(objects, start=1):
        tris = o['tris']
        flat = tris.reshape(-1, 3)
        keys, inv = np.unique(np.round(flat, 5), axis=0, return_inverse=True)
        inv = inv.reshape(-1, 3)
        vs = ''.join(f'<vertex x="{v[0]:.5f}" y="{v[1]:.5f}" z="{v[2]:.5f}"/>' for v in keys)
        ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in inv if a != b and b != c and a != c)
        res.append(f'<object id="{oid}" name="{o["name"]}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        tx, ty = o['offset']
        build.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} 0" printable="1"/>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
            'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
            '<metadata name="Application">BambuStudio-02.00.00.00</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'
            '<metadata name="Title">Robot Cua A1 V4 r001</metadata>'
            f'<resources>{"".join(res)}</resources><build>{"".join(build)}</build></model>')


def settings_xml(objects, plates):
    o = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>']
    for oid, ob in enumerate(objects, start=1):
        o.append(f'<object id="{oid}"><metadata key="name" value="{ob["name"]}"/><metadata key="extruder" value="1"/>'
                 f'<part id="1" subtype="normal_part"><metadata key="name" value="{ob["name"]}"/></part></object>')
    for p in plates:
        o.append(f'<plate><metadata key="plater_id" value="{p["index"]}"/><metadata key="plater_name" value="{p["name"]}"/>'
                 '<metadata key="locked" value="false"/>')
        for oid in p['objectIds']:
            o.append(f'<model_instance><metadata key="object_id" value="{oid}"/><metadata key="instance_id" value="0"/>'
                     f'<metadata key="identify_id" value="{100 + oid}"/></model_instance>')
        o.append('</plate>')
    o.append('</config>')
    return ''.join(o)


def write_3mf(path, plan, manifest, printed, group_names=True):
    parts = {p['name']: p for p in manifest['parts']}
    objects, plates = [], []
    groups = []
    for title, names in plan:
        old = [n for n in names if n in printed]
        new = [n for n in names if n not in printed]
        if new:
            groups.append((NEW if group_names else '', title, new))
        if old:
            groups.append((OLD if group_names else '', title, old))
    for idx, (group, title, names) in enumerate(groups, start=1):
        oriented = {}
        for n in names:
            tris, a = orient(read_stl(OUT / parts[n]['stl']), parts[n].get('printRotateDeg') or [0, 0, 0])
            oriented[n] = (tris, a)
        ext = {n: tuple((t.reshape(-1, 3).max(0))[:2]) for n, (t, _) in oriented.items()}
        pos = pack(list(ext.items()))
        col, row = (idx - 1) % 2, (idx - 1) // 2
        ox, oy = col * STRIDE, -row * STRIDE
        ids = []
        for n in names:
            tris, a = oriented[n]
            objects.append(dict(name=n, tris=tris, offset=(ox + pos[n][0], oy + pos[n][1]), zrot=a,
                                footprint=[round(ext[n][0], 2), round(ext[n][1], 2)], plate=idx))
            ids.append(len(objects))
        name = f'{group} {idx} — {title} (r001-v1)' if group else f'{title} (r001-v1)'
        plates.append(dict(index=idx, name=name, group=group or 'TEST ONLY', objectIds=ids, parts=[f'{n}.stl' for n in names]))
    st = json.loads(SETTINGS.read_text())['settings']
    files = {
        '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                               '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                               '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                               '<Default Extension="png" ContentType="image/png"/><Default Extension="config" ContentType="text/xml"/></Types>',
        '_rels/.rels': '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
        '3D/3dmodel.model': model_xml(objects),
        'Metadata/model_settings.config': settings_xml(objects, plates),
        'Metadata/project_settings.config': json.dumps(st, indent=1),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            zi = zipfile.ZipInfo(k, date_time=(2026, 11, 6, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, v)
    return objects, plates, st


def slice_project(path, tag):
    """Slice every plate with the Bambu Studio CLI (no printer contact). Returns per-plate estimates."""
    out = BUILD / tag
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob('*'):
        if f.is_file():
            f.unlink()
    cmd = [BAMBU, '--slice', '0', '--export-3mf', 'sliced.3mf', '--outputdir', str(out), str(path)]
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    log = (p.stdout or '') + (p.stderr or '')
    (out / 'cli.log').write_text(log)
    res = dict(returncode=p.returncode, seconds=round(time.time() - t, 1), plates={}, warnings=[], savedPlateNames=[])
    sliced = out / 'sliced.3mf'
    if sliced.exists():
        with zipfile.ZipFile(sliced) as z:
            names = z.namelist()
            info = z.read('Metadata/slice_info.config').decode() if 'Metadata/slice_info.config' in names else ''
            ms = z.read('Metadata/model_settings.config').decode() if 'Metadata/model_settings.config' in names else ''
        res['savedPlateNames'] = re.findall(r'plater_name" value="([^"]*)"', ms)
        for m in re.finditer(r'<plate>(.*?)</plate>', info, re.S):
            blk = m.group(1)
            g = lambda k: (re.search(rf'key="{k}" value="([^"]*)"', blk) or [None, None])[1]
            idx = int(g('index'))
            res['plates'][idx] = dict(predictionS=float(g('prediction') or 0), weightG=float(g('weight') or 0),
                                      support=g('support_used'), objects=re.findall(r'<object [^>]*name="([^"]*)"', blk),
                                      warnings=re.findall(r'<warning [^>]*msg="([^"]*)"', blk))
    for line in log.splitlines():
        if re.search(r'warn|error|fail', line, re.I):
            res['warnings'].append(line.strip()[:300])
    return res


def main():
    manifest = json.loads((OUT / 'parts.json').read_text())
    printed = ledger()
    noslice = '--no-slice' in sys.argv
    stamp_in = sha(json.dumps([sha((OUT / p['stl']).read_bytes()) for p in manifest['parts']] +
                              [p.get('printRotateDeg') for p in manifest['parts']] + [sorted(printed), PLAN, TEST_PLAN]).encode()
                   + Path(__file__).read_bytes())
    report_f = PRINT / 'production-check.json'
    if report_f.exists() and not noslice and '--force' not in sys.argv:
        old = json.loads(report_f.read_text())
        if old.get('inputsSha256') == stamp_in and old.get('passed') and (PRINT / 'production.3mf').exists():
            print('plates: inputs unchanged, report current'); return
    prod = PRINT / 'production.3mf'
    objs, plates, st = write_3mf(prod, PLAN, manifest, printed)
    tobjs, tplates, _ = write_3mf(PRINT / 'TEST-ONLY-coupons.3mf', TEST_PLAN, manifest, {}, group_names=False)
    errors, warnings = [], []
    parts = {p['name']: p for p in manifest['parts']}
    want = [p['name'] for p in manifest['parts'] if p.get('printable', True) and p['role'] != 'coupon']
    got = [o['name'] for o in objs]
    if sorted(want) != sorted(got) or len(set(got)) != len(got):
        errors.append('Print all does not hold every production part exactly once')
    for o in objs:
        if o['footprint'][1] > o['footprint'][0] + 1e-6:
            errors.append(f"{o['name']} long side along Y")
    est = {}
    if not noslice:
        for tag, f in (('production', prod), ('test', PRINT / 'TEST-ONLY-coupons.3mf')):
            est[tag] = slice_project(f, tag)
            if est[tag]['returncode'] != 0 or not est[tag]['plates']:
                errors.append(f'Bambu Studio CLI failed on {f.name} (see build/case/slice/{tag}/cli.log)')
            warnings += est[tag]['warnings'][:20]
            want_names = [p['name'] for p in (plates if tag == 'production' else tplates)]
            if est[tag]['savedPlateNames'] != want_names:
                errors.append(f'{tag}: plate names not preserved by Bambu Studio: {est[tag]["savedPlateNames"]}')
        pe = est.get('production', {}).get('plates', {})
        tot_h = sum(p['predictionS'] for p in pe.values()) / 3600
        tot_g = sum(p['weightG'] for p in pe.values())
        for i, p in pe.items():
            if p['predictionS'] / 3600 > LIMIT_PLATE_H:
                errors.append(f'plate {i} {p["predictionS"] / 3600:.2f} h > 4.5 h')
        if pe and tot_h > LIMIT_TOTAL_H:
            errors.append(f'total {tot_h:.2f} h > 8 h')
        if pe and tot_g > LIMIT_G:
            errors.append(f'plastic {tot_g:.1f} g > 220 g')
        if len(plates) > 2:
            errors.append('more than 2 plates')
    data = prod.read_bytes()
    pe = est.get('production', {}).get('plates', {})
    report = dict(
        passed=not errors and not noslice, errors=errors, warnings=warnings, inputsSha256=stamp_in,
        file=str(prod.relative_to(ROOT)), sha256=sha(data), slicer='Bambu Studio CLI ' + BAMBU,
        settings=dict(source=str(SETTINGS.relative_to(ROOT)), printer=st.get('printer_settings_id'), process=st.get('print_settings_id'),
                      filament=st.get('filament_settings_id'), layer=st.get('layer_height'), walls=st.get('wall_loops'),
                      infill=f"{st.get('sparse_infill_density')} {st.get('sparse_infill_pattern')}", support=st.get('support_type'),
                      enableSupport=st.get('enable_support'), brim=st.get('brim_type')),
        meshes=[dict(name=f"{o['name']}.stl", canonicalSTLSha256=sha((OUT / parts[o['name']]['stl']).read_bytes()),
                     printRotateDeg=parts[o['name']].get('printRotateDeg') or [0, 0, 0], extraZRotateDeg=o['zrot'],
                     bedFootprintMm=o['footprint'], plate=o['plate'],
                     yLongReason=None) for o in objs],
        plates=[dict(index=p['index'], name=p['name'], group=p['group'], filament='PETG Basic (one colour)', parts=p['parts'],
                     estimate=pe.get(p['index'])) for p in plates],
        totals=dict(hours=round(sum(p['predictionS'] for p in pe.values()) / 3600, 2) if pe else None,
                    grams=round(sum(p['weightG'] for p in pe.values()), 1) if pe else None),
        testProject=dict(file=str((PRINT / 'TEST-ONLY-coupons.3mf').relative_to(ROOT)), sha256=sha((PRINT / 'TEST-ONLY-coupons.3mf').read_bytes()),
                         plates=[dict(index=p['index'], name=p['name'], parts=p['parts'], estimate=est.get('test', {}).get('plates', {}).get(p['index'])) for p in tplates]),
        ledger=dict(file='print/events.jsonl', present=(ROOT / 'print/events.jsonl').exists(), printedParts=sorted(printed)),
        layoutRules='one PETG colour per plate; big parts together, small parts together; long side along X (Z rotation only); auto brim inside 8 mm margin',
        checkedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    PRINT.mkdir(parents=True, exist_ok=True)
    report_f.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n')
    print('passed' if report['passed'] else 'NOT PASSED', errors, report['totals'])


if __name__ == '__main__':
    main()

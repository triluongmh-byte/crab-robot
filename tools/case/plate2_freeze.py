"""Freeze of the plate-2 parts (A1V4-r1), which the owner reports printing.

  freeze_from_git()  writes case/frozen-plate2-A1V4-r1.json once, from commit 2ef9e2c (the 3MF the owner has).
  verify(path)       re-reads case/out + a 3MF and returns errors if any frozen mesh, rotation or position moved.

CLI:  case-python tools/case/plate2_freeze.py --freeze     (one time, refuses to overwrite)
      case-python tools/case/plate2_freeze.py              (fast verify of case/print/production.3mf, < 1 s)
"""
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_COMMIT = '2ef9e2c'
MANIFEST = ROOT / 'case/frozen-plate2-A1V4-r1.json'
RETIRED = ('cap_front', 'cap_rear')   # owner removed both clamp bars (notes 7, 8): no longer current production parts
PLATE2 = [f'{k}_{c}' for k in ('thigh', 'foot') for c in ('FL', 'FR', 'RL', 'RR')]
ALSO_FROZEN = ['coupon_TEST_ONLY', 'MATING_TEST_leg_FL']   # test prints: same geometry, must not churn


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(path):
    return subprocess.run(['git', 'show', f'{BASELINE_COMMIT}:{path}'], cwd=ROOT, capture_output=True, check=True).stdout


def read_3mf(data):
    """-> {part: {'meshSha': .., 'plate': int, 'transform': str}}. Names come from model_settings.config."""
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        model = z.read('3D/3dmodel.model').decode()
        cfg = z.read('Metadata/model_settings.config').decode()
    names = dict(re.findall(r'<object id="(\d+)"><metadata key="name" value="([^"]+)\.stl"/>', cfg))
    meshes = dict(re.findall(r'<object id="(\d+)" type="model">(<mesh>.*?</mesh>)</object>', model, re.S))
    trans = dict(re.findall(r'<item objectid="(\d+)" transform="([^"]+)"', model))
    plates = {}
    for m in re.finditer(r'<plate><metadata key="plater_id" value="(\d+)"/><metadata key="plater_name" value="([^"]*)"/>(.*?)</plate>',
                         cfg, re.S):
        for oid in re.findall(r'key="object_id" value="(\d+)"', m.group(3)):
            plates[oid] = (int(m.group(1)), m.group(2))
    out = {}
    for oid, name in names.items():
        out[name] = {'meshSha': sha(meshes[oid].encode()), 'plate': plates[oid][0], 'plateName': plates[oid][1],
                     'transform': trans[oid]}
    return out


def freeze_from_git():
    if MANIFEST.exists():
        sys.exit(f'{MANIFEST} already exists: the freeze is one-time')
    tmf = read_3mf(git_blob('case/print/production.3mf'))
    plate2 = sorted(n for n, r in tmf.items() if r['plate'] == 2)
    if plate2 != sorted(PLATE2):
        sys.exit(f'existing plate 2 is not the expected set: {plate2}')
    parts_json = json.loads(git_blob('case/out/parts.json'))
    pinfo = {p['name']: p for p in parts_json['parts']}
    frozen = {}
    for n in PLATE2 + ALSO_FROZEN:
        stl, step = git_blob(f'case/out/{n}.stl'), git_blob(f'case/out/{n}.step')
        e = {'stlSha256': sha(stl), 'stepSha256': sha(step), 'volumeMm3': pinfo[n].get('volumeMm3'),
             'printRotateDeg': pinfo[n].get('printRotateDeg')}
        if n in tmf:
            e.update(mesh3mfSha256=tmf[n]['meshSha'], plate=tmf[n]['plate'], transform=tmf[n]['transform'])
        frozen[n] = e
    MANIFEST.write_text(json.dumps({
        'schema': 1, 'revision': 'A1V4-r1', 'sourceCommit': BASELINE_COMMIT,
        'why': 'Owner reports plate 2 printing (release note 2). Reported only: not finished, not confirmed, not fit-checked.',
        'plate2Name': next(r['plateName'] for r in tmf.values() if r['plate'] == 2),
        'plate2Parts': PLATE2, 'parts': frozen}, indent=1, ensure_ascii=False) + '\n')
    print('wrote', MANIFEST.relative_to(ROOT))


def load():
    return json.loads(MANIFEST.read_text())


def verify_files():
    """Frozen STL/STEP bytes in case/out. Returns a list of error strings."""
    errs = []
    for n, e in load()['parts'].items():
        if n in RETIRED:
            continue
        for suffix, key in (('stl', 'stlSha256'), ('step', 'stepSha256')):
            p = ROOT / f'case/robot/{n}.{suffix}'
            if not p.exists():
                errs.append(f'frozen {n}.{suffix} is missing')
            elif sha(p.read_bytes()) != e[key]:
                errs.append(f'frozen {n}.{suffix} changed')
    return errs


def verify_3mf(path):
    """Frozen meshes, plate number and bed position inside a saved Print-all 3MF. Returns (errors, rows)."""
    man = load()
    now = read_3mf(Path(path).read_bytes())
    errs, rows = [], []
    for n in man['plate2Parts']:
        if n in RETIRED:
            if n in now:
                errs.append(f'{n} (retired clamp bar) is still in the 3MF')
            continue
        e, r = man['parts'][n], now.get(n)
        if r is None:
            errs.append(f'{n} is missing from the 3MF'); continue
        ok = {'mesh': r['meshSha'] == e['mesh3mfSha256'], 'plate': r['plate'] == e['plate'], 'position': r['transform'] == e['transform']}
        for k, v in ok.items():
            if not v:
                errs.append(f'{n}: {k} differs from the frozen plate 2')
        rows.append({'part': n, 'meshSha256': r['meshSha'], **ok})
    extra = sorted(n for n, r in now.items() if r['plate'] == 2 and n not in PLATE2)
    if extra:
        errs.append(f'extra parts on plate 2: {extra}')
    return errs, rows


def main():
    if '--freeze' in sys.argv:
        freeze_from_git()
        return 0
    errs = verify_files()
    e2, rows = verify_3mf(ROOT / 'case/print/production.3mf')
    errs += e2
    print(json.dumps({'passed': not errs, 'errors': errs, 'meshesChecked': len(rows)}, ensure_ascii=False))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())

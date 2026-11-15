"""Write sonar_bracket.3mf: an unsliced Bambu Studio project (A1, 0.4 mm, calibrated PETG profile of case/print-settings.json)
with the bracket in print orientation in the middle of the plate. Optionally slice it offline with the Bambu Studio CLI.

Never contacts a printer.

Usage:  python3 case/sonar_bracket/make_3mf.py [--slice OUTDIR]
        --slice writes OUTDIR/sliced.3mf and OUTDIR/plate_1.gcode and prints the time / mass estimate.
"""
import argparse
import json
import re
import subprocess
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SETTINGS = HERE.parent / 'print-settings.json'
BAMBU = Path('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio')
BED_CENTRE = (128.0, 128.0)


def stl_tris(path):
    d = path.read_bytes()
    n = int.from_bytes(d[80:84], 'little')
    a = np.frombuffer(d[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', 9), ('a', '<u2')]), count=n)
    return a['v'].reshape(-1, 3, 3).astype(float)


def mesh_xml(oid, T):
    V, idx, verts = {}, [], []
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


def write_3mf(path, T, name):
    settings = json.loads(SETTINGS.read_text())['settings']
    T = T.copy()
    T[:, :, 0] -= (T[:, :, 0].min() + T[:, :, 0].max()) / 2
    T[:, :, 1] -= (T[:, :, 1].min() + T[:, :, 1].max()) / 2
    T[:, :, 2] -= T[:, :, 2].min()
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
             '<metadata name="Application">BambuStudio-02.07.01.62</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'
             f'<metadata name="Title">{name}</metadata><resources>{mesh_xml(1, T)}</resources>'
             f'<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 {BED_CENTRE[0]} {BED_CENTRE[1]} 0" printable="1"/></build></model>')
    cfg = ('<?xml version="1.0" encoding="UTF-8"?>\n<config><object id="1">'
           f'<metadata key="name" value="{name}.stl"/><metadata key="extruder" value="1"/>'
           f'<part id="1" subtype="normal_part"><metadata key="name" value="{name}"/></part></object>'
           '<plate><metadata key="plater_id" value="1"/><metadata key="plater_name" value="SONAR — MỚI — CẦN IN"/>'
           '<metadata key="locked" value="false"/><model_instance><metadata key="object_id" value="1"/>'
           '<metadata key="instance_id" value="0"/><metadata key="identify_id" value="101"/></model_instance></plate></config>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, data in (('[Content_Types].xml', ct), ('_rels/.rels', rels), ('3D/3dmodel.model', model),
                        ('Metadata/model_settings.config', cfg), ('Metadata/project_settings.config', json.dumps(settings, indent=1))):
            zi = zipfile.ZipInfo(n, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)


def slice_offline(src, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    out3 = outdir / 'sliced.3mf'
    cmd = [str(BAMBU), '--slice', '0', '--export-3mf', out3.name, '--outputdir', str(outdir), '--debug', '1', str(src)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd=outdir)
    (outdir / 'cli.log').write_text((r.stdout or '') + (r.stderr or ''))
    if r.returncode or not out3.exists():
        raise SystemExit(f'Bambu Studio CLI failed ({r.returncode}); see {outdir / "cli.log"}')
    with zipfile.ZipFile(out3) as z:
        info = z.read('Metadata/slice_info.config').decode()
        g = [n for n in z.namelist() if n.endswith('.gcode')]
        if g:
            (outdir / 'plate_1.gcode').write_bytes(z.read(g[0]))
    get = lambda k: (re.search(rf'key="{k}" value="([^"]*)"', info) or [None, None])[1]
    return {'predictionS': float(get('prediction') or 0), 'weightG': float(get('weight') or 0), 'supportUsed': get('support_used'),
            'warnings': re.findall(r'<warning msg="([^"]*)"', info), 'gcode': str(outdir / 'plate_1.gcode') if g else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    a = ap.parse_args()
    dst = HERE / 'sonar_bracket.3mf'
    write_3mf(dst, stl_tris(HERE / 'sonar_bracket.stl'), 'sonar_bracket')
    print(dst)
    if a.slice:
        print(json.dumps(slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

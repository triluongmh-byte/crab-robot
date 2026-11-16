"""Write power_tray.3mf: an unsliced Bambu Studio project (A1, 0.4 mm, the repo's calibrated PETG profile in
case/print-settings.json) with the tray and the switch holder side by side, both flat on the bed.
Optionally slice it offline with the Bambu Studio CLI. Never contacts a printer.

Usage:  python3 case/power_tray/make_3mf.py [--slice OUTDIR]
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'sonar_bracket'))
import power_tray as PT  # noqa: E402
from make_3mf import stl_tris, mesh_xml, slice_offline, SETTINGS, BED_CENTRE  # noqa: E402  (sonar_bracket helpers)

PLATE_NAME = 'KHAY PIN — MỚI — CẦN IN'


def export_stl(shape, path):
    cq.exporters.export(shape, str(path), tolerance=0.05, angularTolerance=0.1)
    return stl_tris(path)


def centred(T, dx, dy):
    T = T.copy()
    T[:, :, 0] -= (T[:, :, 0].min() + T[:, :, 0].max()) / 2 - dx
    T[:, :, 1] -= (T[:, :, 1].min() + T[:, :, 1].max()) / 2 - dy
    T[:, :, 2] -= T[:, :, 2].min()
    return T


def write_3mf(path, objects):
    settings = json.loads(SETTINGS.read_text())['settings']
    # Nothing on these parts needs support: the tie grooves have 45 deg sides and a 2.6 mm bridge, and tree
    # supports placed inside them would block the zip ties.
    settings['enable_support'] = '0'
    res = ''.join(mesh_xml(i + 1, T) for i, (_, T) in enumerate(objects))
    items = ''.join(f'<item objectid="{i + 1}" transform="1 0 0 0 1 0 0 0 1 {BED_CENTRE[0]} {BED_CENTRE[1]} 0" printable="1"/>'
                    for i in range(len(objects)))
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">'
             '<metadata name="Application">BambuStudio-02.07.01.62</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'
             f'<metadata name="Title">power_tray</metadata><resources>{res}</resources><build>{items}</build></model>')
    objs = ''.join(f'<object id="{i + 1}"><metadata key="name" value="{n}.stl"/><metadata key="extruder" value="1"/>'
                   f'<part id="{i + 1}" subtype="normal_part"><metadata key="name" value="{n}"/></part></object>'
                   for i, (n, _) in enumerate(objects))
    inst = ''.join(f'<model_instance><metadata key="object_id" value="{i + 1}"/><metadata key="instance_id" value="0"/>'
                   f'<metadata key="identify_id" value="{101 + i}"/></model_instance>' for i in range(len(objects)))
    cfg = (f'<?xml version="1.0" encoding="UTF-8"?>\n<config>{objs}<plate><metadata key="plater_id" value="1"/>'
           f'<metadata key="plater_name" value="{PLATE_NAME}"/><metadata key="locked" value="false"/>{inst}</plate></config>')
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--slice', metavar='OUTDIR')
    a = ap.parse_args()
    tray = export_stl(PT.gen_step(), HERE / 'power_tray.stl')
    sw = export_stl(PT.switch_holder(), HERE / 'switch_holder.stl')
    cq.exporters.export(PT.switch_holder(), str(HERE / 'switch_holder.step'))
    ty = (tray[:, :, 1].max() - tray[:, :, 1].min())
    objects = [('power_tray', centred(tray, 0, 0)), ('switch_holder', centred(sw, 0, -(ty / 2 + 6 + PT.P.sw_plate[1] / 2)))]
    dst = HERE / 'power_tray.3mf'
    write_3mf(dst, objects)
    print(dst)
    if a.slice:
        print(json.dumps(slice_offline(dst, Path(a.slice)), indent=1))


if __name__ == '__main__':
    main()

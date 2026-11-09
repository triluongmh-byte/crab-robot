#!/usr/bin/env python3
"""Restore library inputs and generate the two documented clearance envelopes.

STEP assets are build outputs. Library source hashes prevent a different local
KiCad asset from silently changing the checked assembly. No network installs.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
LIB = Path(os.environ.get('KICAD_MODEL_LIBRARY', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels'))
OUT = ROOT / 'design/Local.3dshapes'
INPUTS = ROOT / 'engineering/model-inputs.json'

def main():
    data = json.loads(INPUTS.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    for name, item in data['nativeLibrary'].items():
        source = LIB / item['path']
        if not source.is_file():
            raise SystemExit(f'Missing KiCad model: {source}; set KICAD_MODEL_LIBRARY to the pinned library')
        if hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']:
            raise SystemExit(f'KiCad model revision differs: {source}; use the documented library version')
        shutil.copyfile(source, OUT / name)
    for name, item in data['measuredEnvelopes'].items():
        lo, hi = item['usedBounds']
        shape = cq.Workplane('XY').box(*[hi[i]-lo[i] for i in range(3)], centered=False).translate(tuple(lo))
        target = OUT / name
        cq.exporters.export(shape, str(target))
        content = target.read_bytes()
        pattern = rb"Open CASCADE STEP translator [^']*"
        observed = list(dict.fromkeys(re.findall(pattern, content)))
        original = [s.encode() for s in item['productNames']]
        if len(observed) != len(original):
            raise RuntimeError(f'Unexpected STEP structure: {name}')
        mapping = dict(zip(observed, original))
        content = re.sub(rb'FILE_NAME\(.*?;\n', lambda _: item['fileNameHeader'].encode(), content, count=1, flags=re.S)
        content = re.sub(pattern, lambda m: mapping[m.group()], content)
        if hashlib.sha256(content).hexdigest() != item['stepSha256']:
            raise RuntimeError(f'Clearance model differs from pinned geometry: {name}')
        target.write_bytes(content)
    print(f"Prepared {len(data['nativeLibrary'])} pinned library models and {len(data['measuredEnvelopes'])} measured clearance envelopes")

if __name__ == '__main__':
    main()

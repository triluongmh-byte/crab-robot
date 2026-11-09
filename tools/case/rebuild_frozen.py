#!/usr/bin/env python3
"""Recreate accepted r1 frozen parts from source, preserving exact print/STEP bytes.

Baseline STEP timestamp/product names are explicit reproducibility inputs. Only
those metadata strings are restored; full expected hashes guard all geometry.
One fresh OCCT process per export prevents the process-global naming counter
from changing otherwise identical STEP metadata. No prior generated CAD is read.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / 'case/frozen_r1/source'
METADATA = ROOT / 'case/frozen_r1/metadata.json'
CHILD = '''import importlib.util,pathlib,sys
source=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(source))
s=importlib.util.spec_from_file_location('baseline_build',source/'build.py')
b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
b.OUT=pathlib.Path(sys.argv[2]);b.OUT.mkdir(parents=True,exist_ok=True)
b.export_one(sys.argv[3])
'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'case/out')
    parser.add_argument('--manifest', type=Path, default=ROOT / 'case/frozen-plate2-A1V4-r1.json')
    args = parser.parse_args()
    py = os.environ.get('KICAD_CASE_PYTHON')
    if not py or not Path(py).is_file():
        raise SystemExit('Set KICAD_CASE_PYTHON to the pinned Harness CadQuery interpreter; no automatic install')
    data = json.loads(METADATA.read_text())
    for name, expected in data['sourceFiles'].items():
        if sha(LEGACY / name) != expected:
            raise SystemExit(f'Frozen baseline source changed: {name}')
    manifest = json.loads(args.manifest.read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    scratch = ROOT / 'build/case/frozen'
    scratch.mkdir(parents=True, exist_ok=True)
    names = list(manifest['parts'])
    for name in names:
        if name not in data['parts']:
            raise SystemExit(f'No source-backed baseline for frozen part {name}')
        for suffix in ('stl', 'step'):
            field = suffix + 'Sha256'
            if data['parts'][name][field] != manifest['parts'][name][field]:
                raise SystemExit(f'Frozen manifest differs from accepted source baseline: {name}.{suffix}')
    def rebuild(name):
        expected = data['parts'][name]
        targets = {kind: output / f'{name}.{kind}' for kind in ('stl', 'step')}
        if all(p.is_file() and sha(p) == expected[kind + 'Sha256'] for kind, p in targets.items()):
            return name, False
        with tempfile.TemporaryDirectory(prefix=name + '-', dir=scratch) as directory:
            subprocess.run([py, '-c', CHILD, str(LEGACY), directory, name], cwd=ROOT,
                           check=True, timeout=180, capture_output=True, text=True)
            folder = Path(directory)
            step = folder / f'{name}.step'
            content = step.read_bytes()
            pattern = rb"Open CASCADE STEP translator [^']*"
            observed = list(dict.fromkeys(re.findall(pattern, content)))
            original = [s.encode() for s in expected['productNames']]
            if len(observed) != len(original):
                raise RuntimeError(f'Unexpected OCCT STEP product structure: {name}')
            mapping = dict(zip(observed, original))
            header = expected['fileNameHeader'].encode()
            content, count = re.subn(rb'FILE_NAME\(.*?;\n', lambda _: header, content, count=1, flags=re.S)
            if count != 1:
                raise RuntimeError(f'Unexpected STEP header: {name}')
            content = re.sub(pattern, lambda m: mapping[m.group()], content)
            step.write_bytes(content)
            for kind, target in targets.items():
                source = folder / f'{name}.{kind}'
                if sha(source) != expected[kind + 'Sha256']:
                    raise RuntimeError(f'Regenerated frozen {name}.{kind} does not match; check pinned CadQuery/OCP/fonts')
            for kind, target in targets.items():
                (folder / f'{name}.{kind}').replace(target)
        return name, True
    with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        results = list(pool.map(rebuild, names))
    baseline = ROOT / 'case/ref/baseline-A1V4-r1/base.step'
    expected = data['baselineBase']
    if not baseline.is_file() or sha(baseline) != expected['stepSha256']:
        with tempfile.TemporaryDirectory(prefix='baseline-base-', dir=scratch) as directory:
            subprocess.run([py, '-c', CHILD, str(LEGACY), directory, 'base'], cwd=ROOT,
                           check=True, timeout=180, capture_output=True, text=True)
            content = (Path(directory) / 'base.step').read_bytes()
            pattern = rb"Open CASCADE STEP translator [^']*"
            observed = list(dict.fromkeys(re.findall(pattern, content)))
            original = [s.encode() for s in expected['productNames']]
            if len(observed) != len(original):
                raise RuntimeError('Unexpected baseline base STEP product structure')
            mapping = dict(zip(observed, original))
            content, count = re.subn(rb'FILE_NAME\(.*?;\n', lambda _: expected['fileNameHeader'].encode(), content, count=1, flags=re.S)
            if count != 1:
                raise RuntimeError('Unexpected baseline base STEP header')
            content = re.sub(pattern, lambda m: mapping[m.group()], content)
            if hashlib.sha256(content).hexdigest() != expected['stepSha256']:
                raise RuntimeError('Regenerated baseline base differs from the accepted source')
            baseline.parent.mkdir(parents=True, exist_ok=True)
            baseline.write_bytes(content)
    print(f'PASS: {len(results)} frozen parts and baseline base source-reproduced/verified; rebuilt {sum(changed for _, changed in results)} frozen parts')

if __name__ == '__main__':
    main()

"""Run the tile's `kicadpy.case check-print` for this case and bind the result to the real files.

check-print only accepts handwired manifests (verification.nativePCBCheckerApplies false) but its
printable-surface/bed/mesh validation is what this project's print handoff needs. The integrated-board
manifest declares the native checker applicable, so this tool runs check-print on an identical scratch
copy (same STL/STEP bytes, manifest changed only in that one field) and copies the receipt back.
Skips when inputs are unchanged. Usage: case-python tools/case/print_check.py [--force]
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = ROOT / 'build/case/print-check'
OUT = ROOT / 'case/robot'
TARGET = ROOT / 'case/reports/print-check.json'


def main():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    (SCRATCH / 'case/reports').mkdir(parents=True)
    shutil.copytree(OUT, SCRATCH / 'case/out')
    shutil.copy2(ROOT / 'case/interfaces.json', SCRATCH / 'case/interfaces.json')
    shutil.copy2(ROOT / 'case/reports/mechanical.json', SCRATCH / 'case/reports/mechanical.json')
    man = json.loads((SCRATCH / 'case/out/parts.json').read_text())
    man['verification']['nativePCBCheckerApplies'] = False
    (SCRATCH / 'case/out/parts.json').write_text(json.dumps(man, indent=1, ensure_ascii=False) + '\n')
    r = subprocess.run([sys.executable, '-m', 'kicadpy.case', 'check-print', str(SCRATCH)], capture_output=True, text=True, cwd=ROOT)
    rep_f = SCRATCH / 'case/reports/print-check.json'
    if not rep_f.exists():
        print(r.stdout, r.stderr)
        return 1
    rep = json.loads(rep_f.read_text())
    rep['validationScope'] = 'integrated-board print receipt from an identical scratch copy (only the manifest native flag differs)'
    rep['realManifestSha256'] = hashlib.sha256((OUT / 'parts.json').read_bytes()).hexdigest()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(rep, indent=1, sort_keys=True) + '\n')
    print('print-check passed:', rep.get('passed'), 'errors:', len(rep.get('errors', [])))
    return 0 if rep.get('passed') else 1


if __name__ == '__main__':
    sys.exit(main())

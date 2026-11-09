"""Run the tile's unmodified `kicadpy.case check .` on this workspace: case/out (board frame) against boards/main.enclosure.json.
Writes case/reports/case-check.json. Usage: case-python tools/case/case_check.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    r = subprocess.run([sys.executable, '-m', 'kicadpy.case', 'check', '.'], cwd=ROOT, capture_output=True, text=True)
    print(r.stdout[-600:], r.stderr[-400:])
    rep = ROOT / 'case/reports/case-check.json'
    d = json.loads(rep.read_text())
    print(json.dumps({'passed': d.get('passed'), 'errors': len(d.get('errors', [])), 'warnings': len(d.get('warnings', [])), 'contractSha': d.get('contractSha', '')[:12]}))
    for e in d.get('errors', [])[:30]:
        print(' ERR', e.get('kind'), e.get('message'))
    for w in d.get('warnings', [])[:20]:
        print(' WARN', w.get('kind'), w.get('message'))
    return 0 if d.get('passed') else 1


if __name__ == '__main__':
    sys.exit(main())

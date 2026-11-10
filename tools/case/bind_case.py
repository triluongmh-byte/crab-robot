#!/usr/bin/env python3
"""Materialize case dependency snapshots from the current board publication.

Placement/clearance settings are authored source inputs. Export fingerprints
and enclosure snapshots are derived, so a clean build never needs old STEP.
"""
import hashlib
import json
from pathlib import Path
import shutil
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]

def main():
    verdict = json.loads((ROOT / 'boards/main.board.json').read_text())
    if verdict.get('fab', {}).get('ready') is not True:
        raise SystemExit('Current native board is not fabrication-ready; cannot bind the case')
    placement = json.loads((ROOT / 'case/placement-settings.json').read_text())
    source = ROOT / 'boards/main.enclosure.json'
    target = ROOT / 'case/ref/board-published.enclosure.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    placement['source'] = str(target.relative_to(ROOT / 'case'))
    handoff = ROOT / 'case/ref/board-interface.json'
    shutil.copyfile(ROOT / 'engineering/board-interface.json', handoff)
    placement['interfaceSource'] = str(handoff.relative_to(ROOT / 'case'))
    board_step = ROOT / 'build/board/integrated.step'
    placement['boardStepSha256'] = hashlib.sha256(board_step.read_bytes()).hexdigest()
    (ROOT / 'case/board_placement.json').write_text(json.dumps(placement, ensure_ascii=False, indent=2)+'\n')
    display = ROOT / 'engineering/sources/integrated/waveshare-display.step'
    if display.is_file():
        shutil.copyfile(display, ROOT / 'case/ref/waveshare-23822-display.step')
    subprocess.run([os.environ['KICAD_CASE_PYTHON'],
                    str(ROOT/'tools/case/board_import.py'), str(source),
                    '--interface', str(ROOT/'engineering/board-interface.json')],
                   check=True, cwd=ROOT)
    print('Case bound to current published enclosure and actual board STEP')

if __name__ == '__main__':
    main()

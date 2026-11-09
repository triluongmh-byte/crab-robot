#!/usr/bin/env python3
"""Reject incomplete packets even when an individual seated-pose check passes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    path = ROOT / name
    if not path.is_file():
        raise SystemExit(f'Missing release evidence: {name}')
    return json.loads(path.read_text())

def require(condition, message):
    if not condition:
        raise SystemExit(message)

def main():
    require(read('boards/main.board.json').get('fab', {}).get('ready') is True,
            'Native board fabrication gate is not ready')
    for name in ['case/reports/case-check.json', 'case/reports/mechanical.json',
                 'case/reports/print-check.json', 'case/print/production-check.json',
                 'firmware/TEST-RESULTS.json']:
        require(read(name).get('passed') is True, f'Check did not pass: {name}')
    insertion = read('case/reports/assembly-access.json')
    require(insertion.get('published', {}).get('pass') is True,
            'The actual published board insertion/tool path does not pass; a virtual revision is insufficient')
    require(read('firmware/BOARD-RECONCILIATION.json').get('status') == 'reconciled',
            'Firmware is not reconciled with the actual native board')
    for name in ['case/overview.html', 'case/print/production.3mf',
                 'case/print/test-only.3mf', 'case/print/mating-test.3mf', 'build/board/integrated.step',
                 'build/firmware/esp32/crab.ino.bin', 'build/firmware/integrated/crab.ino.bin']:
        require((ROOT / name).is_file(), f'Missing promised artifact: {name}')
    print('PASS: current board, case insertion/tools, native case, plates and both firmware targets; hardwareTested=false')

if __name__ == '__main__':
    main()

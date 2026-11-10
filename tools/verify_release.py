#!/usr/bin/env python3
"""Reject incomplete packets even when an individual seated-pose check passes."""
import hashlib
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
    require(insertion.get('schema', 0) >= 2 and insertion.get('pass') is True
            and insertion.get('assemblable') is True,
            'The actual published board insertion/tool path does not pass; a virtual revision is insufficient')
    require(insertion.get('usbCableAssessment', {}).get('fitsPublishedJ1') is True,
            'The actual published J1 must accept the normal USB-C cable; a virtual port relocation is insufficient')
    require(read('case/reports/mechanical.json').get('sampling') == 'full',
            'A coarse motion preview is insufficient for release')
    routing = read('case/reports/route-evidence.json')
    expected_leads = {f'{joint} {corner}' for joint in ('hip', 'knee')
                      for corner in ('FL', 'FR', 'RL', 'RR')}
    counts = routing.get('routesPassingPerLead', {})
    require(routing.get('pass') is True and set(counts) == expected_leads
            and all(counts[name] >= 2 for name in expected_leads),
            'Every servo lead needs two passing open-route checks')
    moving = routing.get('movingLegCheck', {})
    require(moving.get('sampling') == 'full' and moving.get('poses', 0) >= 252
            and len(routing.get('routes', [])) >= 16
            and all(item.get('movingPass') is True for item in routing['routes']),
            'Complete installed leads must clear all moving legs; a slack-loop-only check is insufficient')
    loop = routing.get('kneeLeadCrossingHipJoint', {})
    require(loop.get('sampling') == 'full'
            and len(loop.get('sweeps', [])) == 4
            and all(item.get('pass') is True and item.get('thighRunClearanceMm', 0) > 0
                    for item in loop['sweeps']),
            'All four knee leads need full combined-joint sampling')
    route_inputs = sorted((ROOT / 'case/robot').glob('*.step')) + [
        ROOT / 'tools/case/route_check.py', ROOT / 'tools/case/mech_check.py',
        ROOT / 'case/model.py']
    fingerprint = hashlib.sha256()
    for path in route_inputs:
        fingerprint.update(path.read_bytes())
    require(routing.get('inputHash') == fingerprint.hexdigest(),
            'Wire-route evidence is stale or was only a coarse preview')
    require(read('firmware/BOARD-RECONCILIATION.json').get('status') == 'reconciled',
            'Firmware is not reconciled with the actual native board')
    for name in ['case/overview.html', 'case/print/production.3mf',
                 'case/print/test-only.3mf', 'case/print/mating-test.3mf', 'build/board/integrated.step',
                 'case/print/test-saddle.3mf',
                 'build/firmware/esp32/crab.ino.bin', 'build/firmware/integrated/crab.ino.bin']:
        require((ROOT / name).is_file(), f'Missing promised artifact: {name}')
    print('PASS: current board, case insertion/tools, sampled wire/motion checks, plates and both firmware targets; hardwareTested=false')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Unit tests for restore_settings planning (no network)."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from restore_settings import plan, plan_steps

assert plan_steps(0, 0) == []
assert plan_steps(0, 7) == [3, 3, 1]
assert plan_steps(6, -21) == [-3] * 9
assert plan_steps(-11, -30) == [-3] * 6 + [-1]
for cur in range(-30, 31, 7):
    for want in range(-30, 31, 5):
        steps = plan_steps(cur, want)
        assert cur + sum(steps) == want and all(s in (-3, -1, 1, 3) for s in steps)

root = pathlib.Path(__file__).resolve().parents[2]
settings = json.loads((root / 'firmware/settings/owner-2026-11-13.json').read_text(encoding='utf-8'))
assert len(settings['offsets']) == 8 and all(abs(v) <= 30 for v in settings['offsets'])
status = {'offsets': [0] * 8}
reqs = plan(settings, status)
assert reqs[0] == ('assembly', {'active': '1'})
paths = [p for p, _ in reqs]
assert paths.index('save') < paths.index('knee') and reqs[paths.index('save') + 1] == ('assembly', {'active': '0'})
for ch in range(8):
    total = sum(int(q['delta']) for p, q in reqs if p == 'trim' and q['ch'] == str(ch))
    assert total == settings['offsets'][ch]
tail = dict((p, q['value']) for p, q in reqs if 'value' in q)
assert tail['speed'] == '0.90' and tail['knee'] == '35' and tail['balance'] == '4' and tail['lightcolor'] == 'ff0f0f'
print('PASS: restore_settings step planner and request order')

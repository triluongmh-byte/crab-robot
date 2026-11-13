#!/usr/bin/env python3
"""Restore owner-tuned settings (trims, knee lift, heading trim, speed, flick hip,
gait, lamp colour) to a running crab over its HTTP API.

Usage:
  python3 tools/firmware/restore_settings.py firmware/settings/owner-2026-11-13.json --host 172.168.20.249 [--dry-run]

Opening a session takes control from any open page; the robot stops walking.
Trims are stepped in the firmware's 3 deg / 1 deg increments inside Assembly,
then saved with Lưu tâm and Assembly is closed.
"""
import argparse, json, sys, urllib.parse, urllib.request


def plan_steps(current, target, coarse=3, fine=1):
    """Deltas accepted by /api/trim that move one channel from current to target."""
    diff = int(round(target - current))
    steps = []
    sign = 1 if diff > 0 else -1
    while abs(diff) >= coarse:
        steps.append(sign * coarse)
        diff -= sign * coarse
    while diff != 0:
        steps.append(sign * fine)
        diff -= sign * fine
    return steps


def plan(settings, status):
    """Ordered list of (path, params) requests; token is added at send time."""
    reqs = [('assembly', {'active': '1'})]
    for ch, (cur, want) in enumerate(zip(status['offsets'], settings['offsets'])):
        for d in plan_steps(cur, want):
            reqs.append(('trim', {'ch': str(ch), 'delta': str(d)}))
    reqs += [('save', {}), ('assembly', {'active': '0'})]
    reqs += [('knee', {'value': str(int(settings['kneeLift']))}),
             ('balance', {'value': str(int(settings['balance']))}),
             ('speed', {'value': '%.2f' % settings['speed']}),
             ('flickhip', {'value': str(int(settings['flickHip']))}),
             ('gait', {'value': settings['gait']}),
             ('lightcolor', {'value': settings['lightColor'].lstrip('#').lower()})]
    return reqs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('settings')
    ap.add_argument('--host', default='192.168.4.1')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    base = 'http://%s/api/' % a.host
    settings = json.load(open(a.settings, encoding='utf-8'))

    def get(path):
        with urllib.request.urlopen(base + path, timeout=5) as r:
            return json.load(r)

    def post(path, params):
        data = urllib.parse.urlencode(params).encode()
        with urllib.request.urlopen(urllib.request.Request(base + path, data=data), timeout=5) as r:
            return json.load(r)

    status = get('status')
    if not status.get('positional') or status.get('enabled') != 8:
        sys.exit('Servos are not armed (Bật servo) yet; trims need armed 180-degree servos.')
    reqs = plan(settings, status)
    if a.dry_run:
        for p, q in reqs:
            print(p, q)
        return
    token = post('session', {})['token']
    for path, params in reqs:
        post(path, dict(params, token=token))
    after = get('status')
    checks = {'offsets': after['offsets'] == settings['offsets'], 'knee': after['knee'] == settings['kneeLift'],
              'balance': after['balance'] == settings['balance'], 'lightColor': after['lightColor'] == settings['lightColor'].lower()}
    print(json.dumps(checks))
    if not all(checks.values()):
        sys.exit('Restore incomplete; compare /api/status with the settings file.')


if __name__ == '__main__':
    main()

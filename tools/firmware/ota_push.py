#!/usr/bin/env python3
"""Push a firmware image to a running crab over Wi-Fi (firmware v24+).

Usage:
  python3 tools/firmware/ota_push.py --host 172.168.20.249 --bin build/firmware/esp32/crab.ino.bin [--dry-run]
  Two steps (when nobody can type at the prompt):
    ... --show-pin            the crab shows a PIN
    ... --pin 123456          upload with that PIN

Steps, using the same API as the page's "Cập nhật firmware qua Wi-Fi":
  1. POST /api/session         take control (the open page loses it; the crab stops)
  2. POST /api/ota/begin       the crab shows a 6-digit PIN on its screen for 2 min
  3. the PIN                   --pin, or typed at the prompt by whoever can see the screen
  4. POST /api/ota?token&pin   multipart upload; the crab writes, then restarts
  5. GET  /api/status          wait until it answers again and report the firmware

The image must be a LILYGO build of v24 or later (it carries the OTA marker);
anything else is refused by the crab before its boot slot switches. Standard
library plus the system curl, no third-party packages.
"""
import argparse, hashlib, json, subprocess, sys, time, urllib.parse
from pathlib import Path

MARKER_PREFIX = b'crab-ota-target='


def image_target(data):
    """Board name from the OTA marker inside the image, or None."""
    i = data.find(MARKER_PREFIX)
    if i < 0:
        return None
    end = data.find(b';', i)
    return data[i + len(MARKER_PREFIX):end].decode('ascii', 'replace') if end > i else None


def multipart(data, filename='crab.ino.bin', boundary=None):
    """(body, content_type) for one file part. WebServer only treats a part as
    an upload (calling the firmware's upload handler) when it has a filename."""
    boundary = boundary or 'crabota' + hashlib.sha256(data).hexdigest()[:24]
    head = ('--%s\r\nContent-Disposition: form-data; name="firmware"; filename="%s"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n' % (boundary, filename)).encode()
    tail = ('\r\n--%s--\r\n' % boundary).encode()
    return head + data + tail, 'multipart/form-data; boundary=' + boundary


def upload_url(base, token, pin):
    return base + 'ota?' + urllib.parse.urlencode({'token': token, 'pin': pin})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', required=True)
    ap.add_argument('--bin', required=True, type=Path)
    ap.add_argument('--pin', help='6-digit PIN already showing on the crab screen; skips asking for a new one')
    ap.add_argument('--show-pin', action='store_true', help='only ask the crab to show a PIN (2 min), then exit; run again with --pin')
    ap.add_argument('--target', default='lilygo')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    data = a.bin.read_bytes()
    target = image_target(data)
    if not data or data[0] != 0xE9:
        sys.exit('Not an ESP32 app image: %s' % a.bin)
    if target != a.target:
        sys.exit('Image is for %r, not %r (or older than v24): refusing' % (target, a.target))
    base = 'http://%s/api/' % a.host
    print('Image %s: %d bytes, sha256 %s, target %s' % (a.bin.name, len(data), hashlib.sha256(data).hexdigest()[:16], target))

    def call(path, params=None, body=None, headers=None, timeout=10):
        """HTTP through the system curl: on macOS 15 a Homebrew Python gets
        "No route to host" on the LAN (Local Network privacy), curl does not."""
        url = path if '://' in path else base + path
        cmd = ['curl', '-s', '-m', str(timeout), '-w', '\n%{http_code}']
        for k, v in (headers or {}).items():
            cmd += ['-H', '%s: %s' % (k, v)]
        if body is not None:
            cmd += ['--data-binary', '@-']
        elif params is not None:
            cmd += ['-X', 'POST'] + [x for k, v in params.items() for x in ('--data-urlencode', '%s=%s' % (k, v))]
        p = subprocess.run(cmd + [url], input=body, capture_output=True)
        out, _, code = p.stdout.rpartition(b'\n')
        try:
            code = int(code) if p.returncode == 0 else 0  # cut-off body on a weak link
        except ValueError:
            code = 0
        try:
            return code, json.loads(out or b'{}')
        except ValueError:
            return code, {}

    for _ in range(8):  # a weak Wi-Fi link drops or cuts some requests
        code, status = call('status')
        if code == 200 and status.get('firmware'):
            break
        time.sleep(0.5)
    if code != 200 or not status.get('firmware'):
        sys.exit('No crab at %s (HTTP %s)' % (a.host, code))
    print('Running now: %s, slot %s, target %s' % (status.get('firmware'), status.get('slot', '?'), status.get('target', '?')))
    if status.get('target', a.target) != a.target or 'otaMarker' not in status:
        sys.exit('This crab has no OTA (needs v24+) or is a different board')
    if a.dry_run:
        print('Dry run: would take control, show the PIN and upload.')
        return
    code, s = call('session', {})
    token = str(s.get('token', ''))
    if code != 200 or not token:
        sys.exit('Could not take control (HTTP %s)' % code)
    pin = a.pin
    if not pin:
        code, s = call('ota/begin', {'token': token})
        if code != 200:
            sys.exit('PIN request refused (HTTP %s): %s' % (code, s.get('error', '')))
        if s.get('pin'):  # v26+ over the home/office Wi-Fi: no one needs to read the screen
            pin = str(s['pin'])
            print('PIN received over the home Wi-Fi.')
        elif a.show_pin:
            print('The crab shows a 6-digit PIN for 2 minutes. Run again with --pin <PIN>.')
            return
        else:
            pin = input('PIN on the crab screen: ').strip()
    body, ctype = multipart(data, a.bin.name)
    print('Uploading…')
    code, s = call(upload_url(base, token, pin), body=body, headers={'Content-Type': ctype}, timeout=120)
    if code != 200:
        sys.exit('Upload refused (HTTP %s): %s' % (code, s.get('error', '')))
    print('Written. Waiting for the restart…')
    time.sleep(4)
    for _ in range(30):
        code, st = call('status', timeout=3)
        if code == 200 and st.get('firmware'):
            print('Back up: %s, slot %s' % (st.get('firmware'), st.get('slot', '?')))
            return
        time.sleep(1)
    sys.exit('The crab did not answer within 34 s; check its screen.')


if __name__ == '__main__':
    main()

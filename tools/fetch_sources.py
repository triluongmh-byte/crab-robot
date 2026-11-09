#!/usr/bin/env python3
"""Fetch hash-pinned manufacturer reference inputs; never install software."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    spec = json.loads((ROOT / 'engineering/upstream-inputs.json').read_text())
    for item in spec['inputs']:
        target = ROOT / item['path']
        if not target.is_file() or digest(target.read_bytes()) != item['sha256']:
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'CrabRobot-source-build/1.0'})
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    content = response.read()
            except Exception as error:
                raise SystemExit(f"Cannot fetch manufacturer input {item['url']}: {error}; download to {target} and rerun")
            if digest(content) != item['sha256']:
                raise SystemExit(f"Manufacturer input changed at {item['url']}; review the new revision before updating its hash")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        if 'extract' in item:
            member = item['extract']
            with zipfile.ZipFile(target) as archive:
                content = archive.read(member['member'])
            if digest(content) != member['sha256']:
                raise SystemExit('Manufacturer CAD member differs from the pinned revision')
            output = ROOT / member['path']
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        print('Verified manufacturer input:', item['path'])

if __name__ == '__main__':
    main()

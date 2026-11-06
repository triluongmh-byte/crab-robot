#!/usr/bin/env python3
"""Compile only when inputs/toolchain change. Never installs or flashes anything."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/firmware/esp32'
recipe=json.loads((ROOT/'firmware/flash.json').read_text())
cli=shutil.which('arduino-cli')
if not cli:sys.exit('Missing arduino-cli; use the Harness shared Arduino cache.')
data=os.environ.get('ARDUINO_DIRECTORIES_DATA')
if not data:sys.exit('ARDUINO_DIRECTORIES_DATA must name the shared cache, not this worktree.')
libs=Path(os.environ.get('CIRCUIT_FIRMWARE_CACHE',str(Path(data).parent)))/'sketchbook/libraries'
inputs=sorted(p for p in (ROOT/'firmware/crab').rglob('*') if p.is_file())+[ROOT/'firmware/flash.json',Path(__file__)]
fingerprint=hashlib.sha256()
for path in inputs:fingerprint.update(path.name.encode()+path.read_bytes())
for cmd in ([cli,'version'],[cli,'core','list']):fingerprint.update(subprocess.check_output(cmd))
for name in ['TFT_eSPI','Adafruit_NeoPixel']:
 p=libs/name/'library.properties'
 if not p.exists():sys.exit(f'Missing shared library: {p}; no automatic installs.')
 fingerprint.update(p.read_bytes())
stamp=OUT/'input-sha256.txt';digest=fingerprint.hexdigest()
if stamp.exists() and stamp.read_text().strip()==digest and (OUT/'crab.ino.bin').exists():
 print('Firmware unchanged; reusing',OUT/'crab.ino.bin');sys.exit(0)
OUT.mkdir(parents=True,exist_ok=True)
cmd=[cli,'compile','--jobs',str(os.cpu_count() or 1),'--fqbn',recipe['fqbn'],'--libraries',str(libs),'--build-path',str(OUT),'--build-property',f'compiler.cpp.extra_flags=-include {ROOT}/firmware/crab/TftSetup.h',str(ROOT/'firmware/crab')]
print('Building ESP32-S3 using all CPU cores and shared dependencies.',flush=True)
subprocess.run(cmd,check=True,cwd=ROOT)
stamp.write_text(digest+'\n')
print('Built',OUT/'crab.ino.bin')

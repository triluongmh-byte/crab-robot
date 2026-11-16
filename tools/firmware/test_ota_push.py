#!/usr/bin/env python3
"""Unit tests for ota_push request building (no network)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ota_push import image_target, multipart, upload_args, upload_url

img = b'\xe9' + b'\x11' * 100 + b'crab-ota-target=lilygo;' + b'\x00' * 50
assert image_target(img) == 'lilygo'
assert image_target(b'\xe9' + b'\x00' * 100) is None
assert image_target(b'xxcrab-ota-target=integrated;') == 'integrated'
body, ctype = multipart(img, 'crab.ino.bin', boundary='B0')
assert ctype == 'multipart/form-data; boundary=B0'
# WebServer calls the upload handler only for a part with a filename.
assert body.startswith(b'--B0\r\nContent-Disposition: form-data; name="firmware"; filename="crab.ino.bin"\r\n')
assert b'\r\n\r\n' + img + b'\r\n--B0--\r\n' in body and body.endswith(b'--B0--\r\n')
_, auto = multipart(img)
assert auto.split('boundary=')[1].encode() not in img
assert upload_url('http://1.2.3.4/api/', '42', '123456') == 'http://1.2.3.4/api/ota?token=42&pin=123456'
assert upload_args('/x/crab v30.bin', 'crab.bin') == ['-F', 'firmware=@/x/crab v30.bin;filename=crab.bin;type=application/octet-stream']
print('PASS: ota_push curl -F upload args, marker/target check, multipart with filename, upload URL')

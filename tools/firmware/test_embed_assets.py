#!/usr/bin/env python3
"""The gzip arrays in web_ui.h decompress to exactly the page sources."""
import gzip, pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
h = (root / 'firmware/crab/web_ui.h').read_text()
for name, src in (('WEB_UI', 'ui.html'), ('EMOTE_UI', 'emote.html'), ('RADAR_UI', 'radar.html')):
    body = re.search(r'static const uint8_t %s_GZ\[\] PROGMEM=\{([0-9,]+)\};' % name, h).group(1)
    data = bytes(int(x) for x in body.split(','))
    assert int(re.search(r'%s_GZ_LEN=(\d+);' % name, h).group(1)) == len(data)
    assert gzip.decompress(data) == (root / 'firmware/assets' / src).read_bytes(), name
print('PASS: gzip page arrays match ui.html, emote.html and radar.html')

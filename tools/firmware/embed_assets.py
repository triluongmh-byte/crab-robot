#!/usr/bin/env python3
"""Deterministic embedded UI and Vietnamese glyph generator; writes only if changed."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[2]
def put(p,data):
 p=ROOT/p
 if not p.exists() or p.read_bytes()!=data:p.write_bytes(data)
ui=(ROOT/'firmware/assets/ui.html').read_text()
put(Path('firmware/crab/web_ui.h'),('#pragma once\n#include <pgmspace.h>\nstatic const char WEB_UI[] PROGMEM=R"CRABHTML('+ui+')CRABHTML";\n').encode())
# SIL Open Font License, pinned Noto Sans source; font is data, not an SDK.
font=ROOT/'firmware/assets/NotoSans-Regular.ttf'
if not font.exists():
 url='https://raw.githubusercontent.com/notofonts/noto-fonts/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf'
 font.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 lic=urllib.request.urlopen('https://raw.githubusercontent.com/notofonts/noto-fonts/main/LICENSE',timeout=60).read()
 (ROOT/'firmware/assets/OFL.txt').write_bytes(lic)
from PIL import Image,ImageFont,ImageDraw
f=ImageFont.truetype(str(font),12)
# ASCII plus every Vietnamese vowel/tone and Latin extensions used by Vietnamese.
chars=sorted(set(chr(i) for i in range(32,127))|set(chr(i) for i in range(0x1ea0,0x1efa))|set('ĂăÂâĐđÊêÔôƠơƯưÀÁÃÈÉÌÍÒÓÕÙÚÝàáãèéìíòóõùúýĂăĨĩŨũƠơƯưẠạỴỵµ°'))
rows=[]
for c in chars:
 im=Image.new('1',(16,20));ImageDraw.Draw(im).text((0,0),c,font=f,fill=1)
 bits=[sum((1<<(15-x)) for x in range(16) if im.getpixel((x,y))) for y in range(20)]
 rows.append('{%d,%d,{%s}}'%(ord(c),round(f.getlength(c)),','.join(str(x) for x in bits)))
data='#pragma once\n#include <stdint.h>\nstruct Glyph{uint32_t cp;uint8_t advance;uint16_t rows[20];};\nstatic const Glyph GLYPHS[]={\n'+',\n'.join(rows)+'\n};\n'
put(Path('firmware/crab/font_vi.h'),data.encode())
put(Path('firmware/assets/font-manifest.json'),json.dumps({'source':'Noto Sans Regular (SIL OFL)','sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'sizePx':12,'codepoints':[ord(c) for c in chars]},indent=2).encode()+b'\n')

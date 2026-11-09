"""Compare calls emitted by actual Screen::begin against independent vendor source."""
from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parents[2]
manifest=json.loads((root/'firmware/vendor/waveshare-source.json').read_text())
for source,h in manifest['files'].items():
 assert hashlib.sha256((root/'firmware/vendor'/Path(source).name).read_bytes()).hexdigest()==h
vendor=(root/'firmware/vendor/LCD_1in9.c').read_text()
init=vendor.split('static void LCD_1IN9_InitReg(void)',1)[1].split('/********************************************************************************',1)[0]
expected=[]
for kind,value in re.findall(r'LCD_1IN9_Send(Command|Data_8Bit)\((0[xX][0-9a-fA-F]+)\)',init):
 if kind=='Command':expected.append([int(value,16)])
 else:expected[-1].append(int(value,16))
actual=[[int(i) for i in line.split()] for line in (root/'build/firmware/host/integrated/panel-commands.txt').read_text().splitlines()]
assert len(expected)==16 and actual[:-1]==expected, 'actual driver differs from vendor init'
assert actual[-1]==[0x36,0x70^0xc0], 'missing case D15 180-degree landscape flip'
print('PASS: emitted SPI init equals all 16 vendor commands, pixel format/gamma/inversion/sleep/display-on; final MADCTL=vendor landscape xor 180deg')

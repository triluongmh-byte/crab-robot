#!/usr/bin/env python3
"""Independent integrated-board pin/rail/geometry audit, parallel and byte cached."""
import concurrent.futures,hashlib,json,os,pathlib,sys
from kicadpy import toolchain,verify
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R);O=R/'build/board'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geometry():
 s=toolchain.worker('inspect',R/'design/main.kicad_pcb');refs={f['reference']:f for f in s['footprints']}
 assert s['boardBoundsMm']==[-44,-31,44,31] and s['thicknessMm']==1.6 and s['copperLayers']==['F.Cu','B.Cu']
 expected={'U1':{'1':'GND','2':'3V3','3':'CHIP_EN','5':'LCD_RES','6':'LCD_CS','7':'LCD_DC','10':'I2C_SCL','11':'I2C_SDA','12':'LCD_SCLK','13':'USB_DM_MCU','14':'USB_DP_MCU','23':'SERVO_OE','27':'BTN_BOOT','31':'LCD_BL','32':'LCD_MOSI','39':'LED_DIN','40':'GND','41':'GND'},'U2':{'1':'GND','2':'3V3','3':'PB1_5V'},'U3':{**{str(i):'GND' for i in [1,2,3,4,5,14,24,25]},**{str(i+6):f'SERVO_PWM_{i}' for i in range(8)},'23':'SERVO_OE','26':'I2C_SCL','27':'I2C_SDA','28':'3V3'},'J10':dict(zip(map(str,range(1,9)),['LCD_BL','LCD_RES','LCD_DC','LCD_CS','LCD_SCLK','LCD_MOSI','GND','3V3'])),'J11':{'1':'LED_DIN','2':'SERVO_5V','3':'GND'},'J12':{'1':'SERVO_5V','2':'GND'}}
 for i in range(8):expected[f'J{i+2}']={'1':'GND','2':'SERVO_5V','3':f'SERVO_PWM_{i}'}
 for r,m in expected.items():
  for pad in refs[r]['pads']:
   num=pad['number']
   if not num:continue
   want=m.get(num)
   if want is None:assert str(pad['net']).startswith('unconnected-'),(r,num,pad['net'])
   else:assert pad['net']==want,(r,num,pad['net'],want)
 for i,xy in enumerate([[-40,-13],[39,-26],[-39,26],[39,26]],1):
  f=refs[f'H{i}'];pd=f['pads'][0];assert f['at']==xy and pd['drillMm']==[3.2,3.2] and not pd['plated']
 # Exact rail endpoints, irrespective of the verifier's rail-name heuristic.
 totals={}
 for f in refs.values():
  if not f['reference'].startswith('C'):continue
  ns={x['net'] for x in f['pads']}
  if 'GND' in ns and len(ns)==2:
   n=(ns-{'GND'}).pop();totals[n]=totals.get(n,0)+verify.cap_farads(f['value'])*1e6
 assert abs(totals['PB1_5V']-4.8)<1e-6 and totals['PB1_5V']*1.1<10
 assert abs(totals['SERVO_5V']-1000)<1e-6 and abs(totals['3V3']-31.3)<1e-6
 # USB connector may not feed servo rail; no positive bridge/component between the two5V nets.
 for f in refs.values():
  ns={x['net'] for x in f['pads']};assert not {'PB1_5V','SERVO_5V'}<=ns
 widths={}
 for t in s['copper']:
  if t['kind']=='track':widths.setdefault(t['net'],[]).append(t['widthMm'])
 assert min(widths['PB1_5V'])>=.6-1e-6 and min(widths['SERVO_5V'])>=1-1e-6 and max(widths['SERVO_5V'])>=2
 assert min(w for ws in widths.values() for w in ws)>=.2-1e-6
 # Literal GPIO15/strapping/PSRAM/UART pad NC audit against actual copper.
 up={x['number']:x['net'] for x in refs['U1']['pads'] if x['number']}
 for n in ['4','8','9','15','16','24','25','26','28','29','30','33','34','35','36','37','38']:assert up[n].startswith('unconnected-'),(n,up[n])
 rules=json.load(open('design/main.kicad_pro'))['board']['design_settings'];assert not rules['drc_exclusions'] and rules['rules']['min_track_width']>=.2
 out={'passed':True,'nativeState':s,'railNominalUF':totals,'PB1CapWorstUF':totals['PB1_5V']*1.1,'minWidthsMm':{n:min(w) for n,w in widths.items()}}
 (O/'geometry.json').write_text(json.dumps(out,indent=2)+'\n');return 'Independent module/power/PCA/header map and actual rail geometry pass'
def netlist():
 toolchain.run([toolchain.executable('cli'),'sch','export','netlist','--format','kicadxml','-o',str(O/'main.net'),'design/main.kicad_sch'])
 d=verify.netlist('design/main.kicad_pro');assert not d['differences'] and not d['hollowSymbols'],d
 (O/'netlist-audit.json').write_text(json.dumps(d,indent=2)+'\n');return 'Real XML netlist and all-pad native parity pass'
def main():
 files=[p for p in (R/'design').rglob('*') if p.is_file() and p.suffix not in ['.lck','.kicad_prl']]+[R/'parts.json',R/'product.json',pathlib.Path(__file__)]
 key=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(files))).hexdigest();stamp=O/'audit.stamp'
 if stamp.exists() and stamp.read_text()==key and all((O/n).exists() for n in ['geometry.json','netlist-audit.json','main.net']):print('Board audit unchanged; cached pass');return
 with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
  for s in ex.map(lambda f:f(),[geometry,netlist]):print(s)
 stamp.write_text(key)
if __name__=='__main__':main()

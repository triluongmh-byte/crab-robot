#!/usr/bin/env python3
"""Read actual board output without publishing or modifying board-team files.
This is an integration check, separate from firmware host tests. It intentionally
fails for the superseded carrier. Populate board-interface.json from the FINAL
board report before the complete pin audit can pass; never guess component pads.
"""
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect():
 inputs={};findings=[]
 xmlpath=ROOT/'build/board/main.net';pcbpath=ROOT/'design/main.kicad_pcb'
 for p in [xmlpath,pcbpath]:
  if p.exists():inputs[str(p.relative_to(ROOT))]=sha(p)
 if not xmlpath.exists() or not pcbpath.exists():
  return {'status':'pending-board-outputs','findings':['Final PCB/XML netlist missing'],'inputSha256':inputs}
 xml=ET.parse(xmlpath).getroot()
 comps={c.attrib['ref']:c.findtext('value','') for c in xml.findall('./components/comp')}
 esp=[r for r,v in comps.items() if 'ESP32-S3-WROOM-1' in v.upper()]
 pca=[r for r,v in comps.items() if 'PCA9685' in v.upper()]
 if len(esp)!=1 or len(pca)!=1:
  return {'status':'pending-board-outputs','findings':['Available board is not the note4 integrated ESP32-S3-WROOM-1 + PCA9685 PCB; note3 carrier does not qualify.'],
          'observedComponents':comps,'inputSha256':inputs}
 nets={n.attrib['name']:{x.attrib['ref']+'.'+x.attrib['pin'] for x in n.findall('node')} for n in xml.findall('./nets/net')}
 xmlpads={pin:net for net,pins in nets.items() for pin in pins}
 from kicadpy.verify import pcb_pads
 pads,_=pcb_pads(pcbpath.read_text())
 if pads!=xmlpads:findings.append('PCB pad/net map differs from exported XML; request fresh board export')
 specpath=ROOT/'firmware/board-interface.json';inputs[str(specpath.relative_to(ROOT))]=sha(specpath)
 spec=json.loads(specpath.read_text())
 if spec.get('status')!='reviewed-final-board':findings.append('Final board pinout/panel/connector handoff has not been reconciled in firmware/board-interface.json')
 if spec.get('boardInputSha256')!= {str(p.relative_to(ROOT)):sha(p) for p in [xmlpath,pcbpath]}:
  findings.append('Reviewed board hashes missing/stale')
 if not findings:
  # Node groups are copied from the final manufacturer-checked board report,
  # never inferred from current net names or an earlier carrier schematic.
  groups=spec.get('connections',{})
  functions={n.attrib['ref']+'.'+n.attrib['pin']:n.attrib.get('pinfunction','') for n in xml.findall('./nets/net/node')}
  profile=json.loads((ROOT/'firmware/INTEGRATION.json').read_text())['targets']['integrated']['pins']
  gpio={k:v for k,v in profile.items() if isinstance(v,int)}
  # USB signals have dedicated manufacturer pinfunction names, not IO19/20.
  for signal,number in gpio.items():
   matches={n for n,f in functions.items() if n.startswith(esp[0]+'.') and (re.match(r'(?:GPIO|IO)'+str(number)+r'(?:_|$)',f) or (signal=='USB_DM' and number==19 and f.startswith('USB_D-')) or (signal=='USB_DP' and number==20 and f.startswith('USB_D+')))}
   if len(matches)!=1 or not matches.issubset(set(groups.get(signal,[]))):
    findings.append(signal+': reviewed connection does not include actual MCU GPIO'+str(number))
  required=['SDA','SCL','PCA_OE','BOOT','USB_DM','USB_DP','LED_DIN','SERVO_5V','PB1_5V','3V3','GND','LCD_BL','LCD_RST','LCD_CS','LCD_DC','LCD_SCLK','LCD_MOSI']+[f'SERVO_CH{i}' for i in range(8)]
  for name in required:
   nodes=groups.get(name,[])
   if len(nodes)<2:findings.append(name+': no reviewed node pair');continue
   node_nets={pads.get(n) for n in nodes}
   if None in node_nets or len(node_nets)!=1:findings.append(name+': pads absent or not on one net')
  rails=[groups.get(n,[]) for n in ['SERVO_5V','PB1_5V','3V3','GND']]
  railnets=[pads.get(ns[0]) for ns in rails if ns]
  if len(set(railnets))!=4:findings.append('PB1_5V, SERVO_5V, 3V3 and GND must remain separate nets')
  if not spec.get('displayManufacturerEvidence') or not spec.get('oeResetPullupEvidence'):
   findings.append('Panel/init/backlight or OE reset-state evidence missing')
  evidence=spec.get('evidenceSha256',{})
  if not evidence or any(spec.get(k) not in evidence for k in ['displayManufacturerEvidence','oeResetPullupEvidence']):
   findings.append('Manufacturer/display and OE evidence paths must have reviewed hashes')
  for name,h in spec.get('firmwareDisplaySha256',{}).items():
   if sha(ROOT/name)!=h:findings.append('Display source changed after reconciliation: '+name)
  if set(spec.get('firmwareDisplaySha256',{}))!={'firmware/crab/display.h','firmware/crab/waveshare_panel.h'}:
   findings.append('Display source evidence missing')
  if comps.get('R9')!='10k' or not {'R9.2',esp[0]+'.23',pca[0]+'.23'}.issubset(nets.get('SERVO_OE',set())) or 'R9.1' not in nets.get('3V3',set()):
   findings.append('OE must have R9 10k pullup and GPIO21 connection')
  if 'U1.8' not in nets.get('unconnected-(U1-IO15-Pad8)',set()):findings.append('GPIO15 is no longer NC')
  for signal,ns in spec.get('usbSeriesResistors',{}).items():
   if len(ns)!=5 or comps.get(ns[1].split('.')[0])!='22' or pads.get(ns[0])!=pads.get(ns[1]) or len({pads.get(n) for n in ns[2:]})!=1:
    findings.append(signal+': USB 22-ohm series path mismatch')
  for ch in range(8):
   ref='J'+str(ch+2)
   if pads.get(ref+'.1')!='GND' or pads.get(ref+'.2')!='SERVO_5V' or not {ref+'.3',pca[0]+'.'+str(6+ch)}.issubset(set(groups.get('SERVO_CH'+str(ch),[]))):
    findings.append(ref+': servo GND/5V/PWM header order mismatch')
  if spec.get('firmwareHardwareSha256')!=sha(ROOT/'firmware/crab/hardware.h'):
   findings.append('Pin profile changed after board reconciliation')
  for name,h in spec.get('evidenceSha256',{}).items():
   p=ROOT/name
   if not p.exists() or sha(p)!=h:findings.append('Board evidence missing/stale: '+name)
 return {'status':'mismatch-or-unreviewed' if findings else 'reconciled', 'hardwareTested':False,
         'findings':findings,'inputSha256':inputs,'observedComponents':comps,
         'scope':'Native board parity and reviewed interface only; native ERC/DRC/fab gate remain board-team responsibility'}
if __name__=='__main__':
 report=inspect();report['releaseNoteSha256']='122b5b3d406fc1cc148b6bf5abaf6c6fc7315e933a95e5565c1b60ee86d35e08'
 out=ROOT/'firmware/BOARD-RECONCILIATION.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
 sys.exit(0 if report['status']=='reconciled' else 2)

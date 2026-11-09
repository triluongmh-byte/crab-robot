#!/usr/bin/env python3
"""KiCad runtime: note4 native placement, outline, pins, no pre-existing copper."""
import json,pathlib
import pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];mm=p.FromMM
v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
def main():
 b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(mm(1.6))
 title=b.GetTitleBlock();title.SetTitle('CRAB INTEGRATED ESP32-S3 / PCA9685');title.SetRevision('I0');title.SetDate('2026-11-09');b.SetTitleBlock(title)
 spec=json.loads((R/'design/spec.json').read_text());xy=json.loads((R/'build/board/placements.json').read_text());paths=json.loads((R/'build/board/instances.json').read_text())
 nets={};pn={};schpins=json.loads((R/'build/board/schematic-pins.json').read_text())
 for n,ps in spec['nets'].items():
  ni=p.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
  for ref,num in ps:pn[ref,str(num)]=n
 def text(s,x,y,size=.8,layer=p.F_SilkS,angle=0):
  t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(mm(.15));t.SetLayer(layer);t.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T));b.Add(t)
 for d in spec['parts']:
  ref=d['ref']
  if not d['footprint']:continue
  name=d['footprint'].split(':')[1];x,y,a=xy[ref]
  f=p.FootprintLoad(str(R/'design/Local.pretty'),name);f.SetFPID(p.LIB_ID('Local',name));f.SetReference(ref);f.SetValue(d['value']);f.SetPath(p.KIID_PATH('/'+paths[ref]));f.SetPosition(v(x,y));f.SetOrientationDegrees(a)
  f.Reference().SetVisible(False);f.Value().SetVisible(False)
  if ref.startswith(('H','TP')):f.SetAttributes(f.GetAttributes()|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
  for t in f.GraphicalItems():
   if isinstance(t,p.PCB_TEXT):t.SetVisible(False)
  for pad in f.Pads():
   num=pad.GetNumber();n=pn.get((ref,num))
   if not n and num:
    n=schpins.get(ref+'.'+num,f'unconnected-({ref}-Pad{num})')
    if n not in nets:ni=p.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
   if n:pad.SetNet(nets[n])
  b.Add(f)
  # Reference labels added explicitly at clear coordinates below.
  if False:pass
  elif ref.startswith('TP'):text(ref,x,y+2,.8)
 for a,z in zip([(-44,-31),(44,-31),(44,31),(-44,31)],[ (44,-31),(44,31),(-44,31),(-44,-31)]):
  s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*z));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
 for i in range(8):text('CH'+str(i),-16+i*7,24.5,.8)
 for s,x,y,sz in [('CRAB INTEGRATED V0',15,-28,1.2),('ESP32-S3 N16R8',-23,-3,1),('U2 3V3 LDO',-26,3.5,.8),('U3 PCA9685 0x40',9,-8,1),('BOOT',-6,-.8,.8),('RESET',-6,14,.8),('USB / PB1 5V',-37,19,.8),('J10 LCD SPI 3V3',16,-24,.8),('J11 LED',16,27,.8),('DIN 5V GND',26,29.2,.8),('J12 SERVO IN',34,-9,.8),('+5V',36,8,.8),('GND',36,-6.5,.8),('BROWN GND / RED +5V / ORANGE PWM',11,14,.8),('C11 +',22,13,.8)]:text(s,x,y,sz)
 for i,(x,y) in enumerate([(-40,-13),(39,-26),(-39,26),(39,26)],1):text('H'+str(i),x,y+(-4 if y>0 else 4),.8)
 # LCD pin labels outside header courtyard.
 for i,s in enumerate(['BL','RES','DC','CS','SCK','MOSI','GND','3V3']):text(s,6+2.54*i,-16.4,.8,angle=90)
 # Servo current trunk is deliberate copper, retained in the initial router round trip.
 def track(n,pts,w):
  for a,z in zip(pts,pts[1:]):
   t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(w));t.SetLayer(p.F_Cu);t.SetNet(nets[n]);b.Add(t)
 track('SERVO_5V',[(-16,19.54),(33,19.54)],2)
 track('SERVO_5V',[(36,3),(42,9),(42,19.54),(33,19.54)],2)
 p.SaveBoard(str(R/'design/main.kicad_pcb'),b)
 path=R/'design/main.kicad_pcb';s=path.read_text()
 stack='''(stackup
 (layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Paste" (type "Top Solder Paste"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "core") (thickness 1.53) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.Paste" (type "Bottom Solder Paste")) (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "HASL") (dielectric_constraints no))'''
 if '(stackup' not in s:s=s.replace('(setup','(setup\n'+stack,1)
 path.write_text(s)
if __name__=='__main__':main()

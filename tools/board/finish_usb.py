#!/usr/bin/env python3
"""KiCad runtime: finish only missing scoped candidate paths and shell fanout."""
import json,pathlib,shutil,pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];C=R/'build/board/usb-relocation'
seed=C/'pre-paths.kicad_pcb'
if not seed.exists():shutil.copyfile(C/'candidate.kicad_pcb',seed)
b=p.LoadBoard(str(seed));mm=p.FromMM;v=lambda xy:p.VECTOR2I(mm(xy[0]),mm(xy[1]))
def track(n,a,z,w,layer):
 if v(a)==v(z):return
 t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(mm(w));t.SetLayer(layer);t.SetNet(b.FindNet(n));b.Add(t)
def via(n,xy):
 t=p.PCB_VIA(b);t.SetPosition(v(xy));t.SetWidth(mm(.6));t.SetDrill(mm(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet(n));b.Add(t)
for path in json.loads((C/'paths.json').read_text()):
 for a,z in zip(path['points'],path['points'][1:]):
  if a[2]!=z[2]:via(path['net'],a)
  else:track(path['net'],a,z,path['width'],[p.F_Cu,p.B_Cu][a[2]])
track('PB1_5V',[19,-23.955],[19,-22.5],.6,p.F_Cu);via('PB1_5V',[19,-22.5])
track('GND',[18.2,-23.955],[17.13,-24.87],.25,p.F_Cu)
track('GND',[24.7,-23.955],[25.77,-24.87],.25,p.F_Cu)
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT) and t.GetText()=='USB / PB1 5V':
  t.SetPosition(v([33,-23]));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
# Merge a path-search grid via into an existing same-net endpoint within 0.2 mm.
known=[]
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA):continue
 old=t.GetPosition();match=next((q for q in known if q.GetNetname()==t.GetNetname() and (q.GetPosition()-old).EuclideanNorm()<mm(.2)),None)
 if match:
  for x in b.GetTracks():
   if isinstance(x,p.PCB_VIA) or x.GetNetname()!=t.GetNetname():continue
   if x.GetStart()==old:x.SetStart(match.GetPosition())
   if x.GetEnd()==old:x.SetEnd(match.GetPosition())
  b.Remove(t)
 else:known.append(t)
# Router fanout leaves redundant vias where both routed branches are on F.Cu.
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA) or t.GetNetname() not in ['USB_CC1']:continue
 layers=set()
 for x in b.GetTracks():
  if isinstance(x,p.PCB_VIA) or x.GetNetname()!=t.GetNetname():continue
  if x.GetStart()==t.GetPosition() or x.GetEnd()==t.GetPosition():layers.add(x.GetLayer())
 if len(layers)<2:b.Remove(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(C/'candidate.kicad_pcb'),b)
print('Scoped paths, USB input fanout and shell ground finished; native DRC required.')

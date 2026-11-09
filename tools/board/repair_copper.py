#!/usr/bin/env python3
"""Three local missing connections and one moved-cap USB supply repair."""
import pathlib,pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];path=R/'design/main.kicad_pcb';b=p.LoadBoard(str(path));mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y));nets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
def trace(n,pts,w=.5,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
def via(n,x,y):
 z=p.PCB_VIA(b);z.SetPosition(v(x,y));z.SetWidth(mm(.6));z.SetDrill(mm(.3));z.SetLayerPair(p.F_Cu,p.B_Cu);z.SetViaType(p.VIATYPE_THROUGH);z.SetNet(nets[n]);b.Add(z)
# Remove only the USB-to-bulk feeder; leave LDO/cap/testpoint copper in place.
keep={'4a4dd54e-9aa2-44a8-a46d-e9c64fdbc476','707326d8-1ada-441c-8cb4-b85a69c43ede','795af394-dea6-4d9a-907d-b536df0398ee','87b15e80-15e9-4725-86f6-a94436e5c3c9','b003f026-9101-4ea9-8b25-77dcfebffbb9','b9d766d1-4b89-4eeb-b070-1dd6183b4ae7','d499bf0f-33cd-4ecb-820b-96f92290f0cd'}
# Identify feeder by geometry instead of router UUIDs (reproducible after regeneration).
remove=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) or t.GetNetname()!='PB1_5V':continue
 a=t.GetStart();z=t.GetEnd();coords=[(p.ToMM(q.x),p.ToMM(q.y)) for q in [a,z]]
 if min(y for x,y in coords)<6 or any(abs(x+36.9033)<.01 for x,y in coords):remove.append(t)
trace('PB1_5V',[(-36.955,-2.45),(-35.9,-2.45)])
trace('PB1_5V',[(-36.955,2.45),(-35.9,2.45)])
for x,y in [(-35.9,-2.45),(-35.9,2.45),(-36,14)]:via('PB1_5V',x,y)
trace('PB1_5V',[(-35.9,-2.45),(-35.9,2.45),(-35.9,13.9),(-36,14)],layer=p.B_Cu)
trace('PB1_5V',[(-36,14),(-35,15)])
trace('SERVO_5V',[(35,12),(42,12)],1)
# C9 and C10 are both actual3V3 pads: complete the isolated PCA decoupling group.
trace('3V3',[(17.52,-2),(17.52,-3.2)])
via('3V3',17.52,-3.2);via('3V3',25.52,-14.7)
trace('3V3',[(17.52,-3.2),(17.52,-12),(20.22,-14.7),(25.52,-14.7)],layer=p.B_Cu)
trace('3V3',[(25.52,-14.7),(25.52,-16)])
# Removal last avoids KiCad nightly SWIG invalidating iterators.
for t in remove:b.Remove(t)
p.SaveBoard(str(path),b)

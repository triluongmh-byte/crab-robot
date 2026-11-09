#!/usr/bin/env python3
"""Preserve routed signals; make top3V3/bottomGND planes and local USB supply detour."""
import pathlib,pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];path=R/'design/main.kicad_pcb';b=p.LoadBoard(str(path));mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y));nets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
def trace(n,pts,w=.5,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
def via(n,x,y):
 z=p.PCB_VIA(b);z.SetPosition(v(x,y));z.SetWidth(mm(.6));z.SetDrill(mm(.3));z.SetLayerPair(p.F_Cu,p.B_Cu);z.SetViaType(p.VIATYPE_THROUGH);z.SetNet(nets[n]);b.Add(z)
remove=[]
for t in b.GetTracks():
 n=t.GetNetname();a=(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y));z=(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))
 if n=='3V3' and a[0]>17 and z[0]>17 and (a in [(17.52,-2),(17.52,-3.2),(17.52,-12),(20.22,-14.7),(25.52,-14.7)] or z in [(17.52,-3.2),(25.52,-14.7)]):remove.append(t)
 elif n=='PB1_5V':
  if isinstance(t,p.PCB_VIA) or t.GetLayer()==p.B_Cu or min(a[1],z[1])<6 or (abs(a[0]+36.5402)<.01 and abs(a[1]-11.4951)<.01):remove.append(t)
for zone in b.Zones():
 if not zone.GetIsRuleArea() and zone.GetLayer()==p.F_Cu and zone.GetAssignedPriority()==0:zone.SetNet(nets['3V3'])
# Both USB VBUS pad groups join behind connector on B.Cu, away fromD+/D- escapes.
for y in [-2.45,2.45]:trace('PB1_5V',[(-36.955,y),(-38.2,y)]);via('PB1_5V',-38.2,y)
trace('PB1_5V',[(-38.2,-2.45),(-39.7,-2.45),(-39.7,2.45),(-38.2,2.45)],layer=p.B_Cu)
trace('PB1_5V',[(-39.7,2.45),(-39.7,10.3),(-36,14)],layer=p.B_Cu);via('PB1_5V',-36,14);trace('PB1_5V',[(-36,14),(-35,15)])
for t in remove:b.Remove(t)
p.SaveBoard(str(path),b)

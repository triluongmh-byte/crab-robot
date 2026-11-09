#!/usr/bin/env python3
"""Local supply feeder clear of USB locating pegs and data pair."""
import pathlib,pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];path=R/'design/main.kicad_pcb';b=p.LoadBoard(str(path));mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y));n=b.FindNet('PB1_5V')
remove=[]
for t in b.GetTracks():
 a=(p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y));z=(p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y))
 if t.GetNetname()=='PB1_5V' and (isinstance(t,p.PCB_VIA) or t.GetLayer()==p.B_Cu or min(a[1],z[1])<6):remove.append(t)
 # Two redundant GND detours are replaced by the existing filled bottom plane.
 if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND':
  if (abs(a[0]+34)<.01 and abs(a[1]+.8878)<.01 and t.GetLength()>mm(3)) or (t.GetLayer()==p.B_Cu and abs(a[0]+31.9652)<.01 and abs(a[1]-12.0117)<.01):remove.append(t)
def trace(pts,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(.5));t.SetLayer(layer);t.SetNet(n);b.Add(t)
def via(x,y):
 t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(mm(.6));t.SetDrill(mm(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(n);b.Add(t)
trace([(-36.955,-2.45),(-34,-2.45)]);via(-34,-2.45)
trace([(-36.955,2.45),(-36.5,2.45)]);via(-36.5,2.45)
trace([(-36.5,2.45),(-34,4.95)],p.B_Cu)
trace([(-34,-2.45),(-34,12),(-36,14)],p.B_Cu);via(-36,14)
# End joins TP1 and the already correct regulator/capacitor cluster.
# Previous F.Cu end(-36,14)->TP1(-35,15) is retained.
for t in remove:b.Remove(t)
p.SaveBoard(str(path),b)

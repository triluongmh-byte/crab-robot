#!/usr/bin/env python3
"""Local finish of routed board: correct imported fanout widths; thermal/GND pours."""
import json,pathlib,math
import pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];path=R/'design/main.kicad_pcb';mm=p.FromMM
v=lambda x,y:p.VECTOR2I(mm(x),mm(y))
b=p.LoadBoard(str(path));nets={n.GetNetname():n for n in b.GetNetsByNetcode().values()}
# Small capacitor clearance repair, keep all other placement and copper.
for ref in ['C2','C5']:
 f=b.FindFootprintByReference(ref);old={d.GetNumber():d.GetPosition() for d in f.Pads()};f.SetPosition(v(-35.7,p.ToMM(f.GetPosition().y)))
 for d in f.Pads():
  prior=old[d.GetNumber()];now=d.GetPosition()
  for t in b.GetTracks():
   if isinstance(t,p.PCB_VIA):continue
   if t.GetStart()==prior:t.SetStart(now)
   if t.GetEnd()==prior:t.SetEnd(now)
# Freerouting's fanout stage uses75% of declared netclass width, even with DSN200um.
# Restore actual project floor, never lower a rule. Recheck every widened clearance.
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):
  floor=.5 if t.GetNetname()=='PB1_5V' else .2
  if t.GetWidth()<mm(floor):t.SetWidth(mm(floor))
pads=[]
for f in b.GetFootprints():
 for pd in f.Pads():
  bb=pd.GetBoundingBox();pads.append((pd.GetNetname(),p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()),pd.IsOnLayer(p.F_Cu),pd.IsOnLayer(p.B_Cu)))
tracks=[]
for t in b.GetTracks():
 tracks.append((t.GetNetname(),p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y),p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y),p.ToMM(t.GetWidth())/2))
# No overlapping zones in repeated runs.
for z in list(b.Zones()):
 if not z.GetIsRuleArea():b.Remove(z)
def zone(net,layer,pts,priority=0):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets[net]);z.SetAssignedPriority(priority);z.SetLocalClearance(mm(.25));z.SetMinThickness(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetThermalReliefGap(mm(.25));z.SetThermalReliefSpokeWidth(mm(.5));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetMinIslandArea(mm(1)*mm(1))
 chain=p.SHAPE_LINE_CHAIN()
 for x,y in pts:chain.Append(mm(x),mm(y))
 chain.SetClosed(True);z.AddPolygon(chain)
 b.Add(z)
# Output-tab heat spreader both sides, nested at higher priority than GND.
rect=[(-30,1.5),(-13,1.5),(-13,16),(-30,16)]
for layer in [p.F_Cu,p.B_Cu]:zone('3V3',layer,rect,1)
for layer in [p.F_Cu,p.B_Cu]:zone('GND',layer,[(-43.3,-30.3),(43.3,-30.3),(43.3,30.3),(-43.3,30.3)],0)
# Find genuinely clear via sites from KiCad native shapes on both layers.
def clear(x,y,net,rad=.3):
 for n,l,top,r,bot,front,back in pads:
  if n==net or not(front or back):continue
  dx=max(l-x,0,x-r);dy=max(top-y,0,y-bot)
  if math.hypot(dx,dy)<rad+.25:return False
 for n,ax,ay,bx,by,tr in tracks:
  if n==net:continue
  den=(bx-ax)**2+(by-ay)**2;t=max(0,min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/den)) if den else 0
  if math.hypot(x-(ax+t*(bx-ax)),y-(ay+t*(by-ay)))<rad+.25+tr:return False
 return True
sites=[]
for x,y in [(-25,4),(-24,4),(-23,4),(-22,4),(-25,11),(-24,11),(-23,11),(-22,11),(-23,7),(-22,7),(-21,7),(-21,10)]:
 if clear(x,y,'3V3'):
  via=p.PCB_VIA(b);via.SetPosition(v(x,y));via.SetWidth(mm(.6));via.SetDrill(mm(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNet(nets['3V3']);b.Add(via);sites.append([x,y])
 if len(sites)>=6:break
print('3V3 thermal vias',sites)
# Remove only redundant signal vias connected on one layer, retaining tracks.
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA) or t.GetNetname() in ['GND','3V3']:continue
 pos=t.GetPosition();layers=set()
 for z in b.GetTracks():
  if isinstance(z,p.PCB_VIA) or z.GetNetCode()!=t.GetNetCode():continue
  if z.GetStart()==pos or z.GetEnd()==pos:layers.add(z.GetLayer())
 if len(layers)<2:b.Remove(t)

p.SaveBoard(str(path),b)

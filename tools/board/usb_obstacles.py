#!/usr/bin/env python3
"""KiCad runtime: export actual copper polygons and holes for local path search."""
import json,pathlib,pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2];C=R/'build/board/usb-relocation'
b=p.LoadBoard(str(C/'candidate.kicad_pcb'));out=[]
def polygon(a,net,layer):
 for k in range(a.OutlineCount()):
  c=a.COutline(k);out.append({'net':net,'layer':layer,'poly':[[p.ToMM(c.CPoint(i).x),p.ToMM(c.CPoint(i).y)] for i in range(c.PointCount())]})
for f in b.GetFootprints():
 for d in f.Pads():
  for lay in [p.F_Cu,p.B_Cu]:
   if d.IsOnLayer(lay):polygon(d.GetEffectivePolygon(lay),d.GetNetname(),int(lay))
  if d.GetDrillSize().x:
   bb=d.GetBoundingBox();pos=d.GetPosition();dr=d.GetDrillSize()
   for lay in [p.F_Cu,p.B_Cu]:
    # Actual oval orientation via effective hole shape polygon.
    a=p.SHAPE_POLY_SET();d.TransformHoleToPolygon(a,0,p.FromMM(.002),p.ERROR_OUTSIDE)
    polygon(a,'HOLE',int(lay))
 for z in f.Zones():
  if z.GetIsRuleArea() and z.GetDoNotAllowTracks():
   for lay in [p.F_Cu,p.B_Cu]:polygon(z.Outline(),'KEEPOUT',int(lay))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  for lay in [p.F_Cu,p.B_Cu]:out.append({'net':t.GetNetname(),'layer':int(lay),'line':[[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)]]*2,'radius':p.ToMM(t.GetWidth())/2})
 else:out.append({'net':t.GetNetname(),'layer':int(t.GetLayer()),'line':[[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]],'radius':p.ToMM(t.GetWidth())/2})
(C/'obstacles.json').write_text(json.dumps(out));print(len(out),'actual obstacles')

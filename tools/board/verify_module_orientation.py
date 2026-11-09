#!/usr/bin/env python3
"""Resolve raw rotation warning by all 41 logical pad numbers, retaining raw input."""
import collections,hashlib,json,math,pathlib
from kicadpy.verify import pcb_pads,_rot
R=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pcb=R/"design/main.kicad_pcb";source=R/"engineering/factory-pads.json"
 _,fps=pcb_pads(pcb.read_text());fp=next(f for f in fps if f["reference"]=="U1")
 native={p["number"]:(p["x"],p["y"]) for p in fp["pads"] if p["number"]}
 supplier=json.loads(source.read_text())["C2913202"]["pads"];groups=collections.defaultdict(list)
 for p in supplier:groups[p["number"]].append((p["x"],p["y"]))
 assert set(native)==set(groups)==set(map(str,range(1,42)))
 assert len(groups["41"])==9 and len(supplier)==49
 # The nine GND land centres represent one physical module pad41. Their
 # centroid is the documented exposed-pad centre, not an extra GPIO.
 logical={n:tuple(sum(v[i] for v in vs)/len(vs) for i in range(2)) for n,vs in groups.items()}
 rows=[]
 for angle in [0,90,180,270]:
  rotated={n:_rot(*v,angle) for n,v in logical.items()}
  delta={n:(native[n][0]-rotated[n][0],native[n][1]-rotated[n][1]) for n in native}
  shift=[sum(v[i] for v in delta.values())/len(delta) for i in range(2)]
  errors={n:math.hypot(v[0]-shift[0],v[1]-shift[1]) for n,v in delta.items()}
  rows.append({"rotationOffsetDeg":angle,"translationMm":shift,"maxErrorMm":max(errors.values()),"meanErrorMm":sum(errors.values())/len(errors),"perPadErrorMm":errors})
 best=min(rows,key=lambda d:d["maxErrorMm"])
 assert best["rotationOffsetDeg"]==0 and best["maxErrorMm"]<.03
 assert all(r["maxErrorMm"]>19 for r in rows if r is not best)
 assert next(p for p in fp["pads"] if p["number"]=="41")["net"]=="GND"
 result={"passed":True,"method":"by logical pad number; centroid of nine supplier GND pad41 lands, no source change","sourcePCBsha256":sha(pcb),"factoryInputSha256":sha(source),"logicalPads":41,"supplierPhysicalLands":49,"verifiedOffsetDeg":0,"candidates":rows}
 (R/"build/board/module-orientation.json").write_text(json.dumps(result,indent=2)+"\n")
 print("U1 all41 logical pads: offset0deg, max error",round(best["maxErrorMm"],6),"mm; raw rotation warning retained")
if __name__=="__main__":main()

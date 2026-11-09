#!/usr/bin/env python3
"""KiCad runtime: local PB1 input width repair; preserve placement and other nets."""
import pathlib, json, pcbnew as p
R=pathlib.Path(__file__).resolve().parents[2]; path=R/"design/main.kicad_pcb";b=p.LoadBoard(str(path));changed=0
for t in b.GetTracks():
 if isinstance(t,p.PCB_TRACK) and not isinstance(t,p.PCB_VIA) and t.GetNetname()=="PB1_5V" and t.GetWidth()<p.FromMM(.6):
  t.SetWidth(p.FromMM(.6)); changed+=1
if changed:
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
pro=R/"design/main.kicad_pro";d=json.loads(pro.read_text())
if not any(c["name"]=="USB_POWER" for c in d["net_settings"]["classes"]):
 c=next(c for c in d["net_settings"]["classes"] if c["name"]=="LOGIC_POWER").copy();c.update(name="USB_POWER",track_width=.6);d["net_settings"]["classes"].append(c)
for pattern in d["net_settings"]["netclass_patterns"]:
 if pattern["pattern"]=="PB1_5V":pattern["netclass"]="USB_POWER"
pro.write_text(json.dumps(d,indent=2)+"\n");print("PB1 tracks widened:",changed)

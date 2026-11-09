#!/usr/bin/env python3
"""Focused native checks, parallel independent read-only CLI, byte cached."""
import concurrent.futures,hashlib,json,os,pathlib,sys
from kicadpy import toolchain
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R);out=R/"build/board/native";out.mkdir(exist_ok=True)
def run(kind):
 files=list(pathlib.Path("design").rglob("*"));key=hashlib.sha256(b"".join(p.read_bytes() for p in sorted(files) if p.is_file() and p.suffix not in [".lck",".kicad_prl"])).hexdigest()
 stamp=out/(kind+".stamp");report=out/(kind+".json")
 if stamp.exists() and stamp.read_text()==key and report.exists():print(kind,"unchanged; cached");return
 args=[toolchain.executable("cli")]
 if kind=="drc":args+=["pcb","drc","--schematic-parity","--severity-all","--format","json","--units","mm","-o",str(report),"design/main.kicad_pcb"]
 else:args+=["sch","erc","--severity-all","--format","json","--units","mm","-o",str(report),"design/main.kicad_sch"]
 toolchain.run(args,timeout=180);stamp.write_text(key)
 d=json.loads(report.read_text())
 fs=d.get("violations",[])+d.get("unconnected_items",[])+d.get("schematic_parity",[])
 for s in d.get("sheets",[]):fs+=s.get("violations",[])
 from collections import Counter
 print(kind,Counter(f["type"] for f in fs))
 for f in fs:
  if f["type"]!="unconnected_items":print(f["type"],f.get("description"),[(i.get("description"),i.get("pos")) for i in f.get("items",[])])
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:list(ex.map(run,sys.argv[1:] or ["erc","drc"]))

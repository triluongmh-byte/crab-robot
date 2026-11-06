"""Run independent board checks concurrently, reusing only exact-input passes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,subprocess,sys
from kicadpy import toolchain
root=Path(__file__).resolve().parents[2];os.chdir(root)
out=root/'build/board';out.mkdir(parents=True,exist_ok=True)
host=os.environ['KICAD_HARNESS_PYTHON'];native=toolchain.executable('python');cli=toolchain.executable('cli')
design=list(Path('design').rglob('*'));sources=[p for p in design if p.is_file()]
jobs=[
 ('author',[host,'-m','kicadpy.author','check','design/main.kicad_pro','tools/board/spec.json'],sources+[Path('tools/board/spec.json')],[]),
 ('netlist',[host,'-m','kicadpy.verify','netlist','design/main.kicad_pro'],sources,[]),
 ('geometry',[native,'tools/board/measure.py'],sources+[Path('PILOT_CONTRACT.json'),Path('tools/board/measure.py')],['build/board/geometry.json']),
 ('netlist-export',[cli,'sch','export','netlist','--format','kicadxml','-o','build/board/main.net','design/main.kicad_sch'],sources,['build/board/main.net']),
 ('step',[cli,'pcb','export','step','--force','-o','build/board/main.step','design/main.kicad_pcb'],sources,['build/board/main.step'])]
def check(job):
 name,cmd,deps,outputs=job
 h=hashlib.sha256(json.dumps(cmd).encode()+b''.join(str(p).encode()+p.read_bytes() for p in sorted(deps))).hexdigest()
 cache=out/(name+'-check.json')
 if cache.exists():
  old=json.loads(cache.read_text())
  if old.get('inputSha256')==h and old.get('pass') and all(Path(p).is_file() for p in outputs):return {'check':name,'pass':True,'cached':True}
 p=subprocess.run(cmd,text=True,capture_output=True,timeout=180)
 ok=p.returncode==0
 if name in ('author','netlist') and ok:
  d=json.loads(p.stdout.strip().splitlines()[-1]);r=d.get('result',{})
  ok=d.get('ok') and (r.get('ok') if name=='author' else not r.get('differences') and not r.get('hollowSymbols'))
 record={'check':name,'inputSha256':h,'pass':bool(ok),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 cache.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 return {'check':name,'pass':bool(ok),'cached':False}
with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:results=list(pool.map(check,jobs))
print(json.dumps({'pass':all(r['pass'] for r in results),'cpuWorkers':os.cpu_count(),'checks':results}))
sys.exit(0 if all(r['pass'] for r in results) else 1)

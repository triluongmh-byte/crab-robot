#!/usr/bin/env python3
"""Host checks against production code. Parallel CPU use; cached compilation."""
import concurrent.futures,hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/firmware/host';OUT.mkdir(parents=True,exist_ok=True)
CORE=ROOT/'firmware/crab';TEST=ROOT/'firmware/tests'
GROUPS={'wifi','api','assembly','boot','gait','web','qr','pins','hardware'}
selected=set(sys.argv[1:]) or GROUPS
if not selected<=GROUPS:sys.exit('Choose: '+', '.join(sorted(GROUPS)))
def cached(name,inputs,cmd):
 stamp=OUT/(name+'.sha256');digest=hashlib.sha256()
 for p in inputs:digest.update(p.read_bytes())
 digest.update(repr(cmd).encode());sha=digest.hexdigest()
 if stamp.exists() and stamp.read_text()==sha and (OUT/name).exists():return
 subprocess.run(cmd,check=True,cwd=ROOT);stamp.write_text(sha)
if selected&{'wifi','api','assembly','boot','gait'}:
 cached('core',[CORE/'Config.h',CORE/'Robot.h',CORE/'Robot.cpp',TEST/'test_core.cpp'],['clang++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-g','-I'+str(CORE),str(TEST/'test_core.cpp'),str(CORE/'Robot.cpp'),'-o',str(OUT/'core')])
if 'hardware' in selected:
 cached('hardware',[CORE/'Config.h',CORE/'Hardware.h',TEST/'test_hardware.cpp',TEST/'stubs/Wire.h'],['clang++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(TEST/'stubs'),'-I'+str(CORE),str(TEST/'test_hardware.cpp'),'-o',str(OUT/'hardware')])
if 'qr' in selected:
 cached('qr.o',[CORE/'QrEncoder.h',CORE/'QrEncoder.c'],['clang','-std=c99','-O2','-I'+str(CORE),'-c',str(CORE/'QrEncoder.c'),'-o',str(OUT/'qr.o')])
 cached('qr',[CORE/'QrEncoder.h',CORE/'QrEncoder.c',TEST/'qr_dump.cpp'],['clang++','-std=c++17','-O2','-I'+str(CORE),str(TEST/'qr_dump.cpp'),str(OUT/'qr.o'),'-o',str(OUT/'qr')])
def check(group):
 if group=='hardware':cmd=[str(OUT/'hardware')]
 elif group=='web':cmd=['node',str(TEST/'test_web.js')]
 elif group=='qr':cmd=[sys.executable,str(ROOT/'tools/firmware/check_qr.py')]
 elif group=='pins':cmd=[sys.executable,str(ROOT/'tools/firmware/check_interfaces.py')]
 else:cmd=[str(OUT/'core'),group]
 p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
 return group,p.returncode,p.stdout+p.stderr
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
 for group,code,text in pool.map(check,sorted(selected)):
  print(text,end='');results.append({'check':group,'pass':code==0,'output':text})
source_shas={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in [ROOT/'firmware/crab',ROOT/'firmware/tests',ROOT/'tools/firmware'] for p in sorted(base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
report={'sourceSha256':source_shas,'hardwareTested':False,'contractSha256':hashlib.sha256((ROOT/'PILOT_CONTRACT.json').read_bytes()).hexdigest(),'checks':results,'pass':all(r['pass'] for r in results)}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
sys.exit(0 if report['pass'] else 1)

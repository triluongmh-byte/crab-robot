#!/usr/bin/env python3
"""Host-only regressions for both targets; all-core, content-cached compiles.
Board integration is a separate strict read-only check (reconcile.py).
"""
from pathlib import Path
import concurrent.futures, hashlib, json, os, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/firmware/host';OUT.mkdir(parents=True,exist_ok=True)
PROFILES={'lilygo': [], 'integrated': ['-DCRAB_INTEGRATED_BOARD=1']}
def run(cmd):
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(' '.join(map(str,cmd))+'\n'+p.stdout+p.stderr)
 return p.stdout.strip()
def digest(paths):
 h=hashlib.sha256()
 for p in sorted(set(paths)):h.update(str(p.relative_to(ROOT)).encode());h.update(p.read_bytes())
 return h.hexdigest()
def pooled(fn,items):
 with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
  return list(pool.map(fn,items))
def gait_report(core_digest):
 report=json.loads((OUT/'gait-summary.json').read_text())
 report.update({
  'contractSha256':hashlib.sha256((ROOT/'PILOT_CONTRACT.json').read_bytes()).hexdigest(),
  'fullCycleSamplesPerDirection':720,'maxHipDeg':25,'maxKneeDeg':30,
  'softJointLimitDeg':30,'trimLimitDeg':12,'coreInputDigest':core_digest,
  'interpretation':'Default diagonal trot (FL+RR / FR+RL): a full diagonal is always grounded, so the support line passes under the body centre; '
   'about 12% of each cycle has all four feet down. Equal-reach yaw model: trot gives zero body yaw in all 8 directions; '
   'the owner front/rear pairs option is yaw-free only for Forward/Backward and yaws during sideways/diagonal moves. '
   'Two-foot support is a line, not a COM stability margin; mass, friction, dynamic stability, servo load, actual SG90 '
   'angle per microsecond and CAD collisions are not modelled. Physical walking remains unverified.',
  'source':'firmware/crab/core.h::gait; firmware/tests/test_core.cpp::simulation',
  'trace':'../build/firmware/host/gait.csv'})
 target=ROOT/'firmware/GAIT-REPORT.json';content=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
 if not target.exists() or target.read_text()!=content:target.write_text(content)
def cpp(group,profile):
 dest=OUT if profile=='lilygo' else OUT/profile;dest.mkdir(parents=True,exist_ok=True)
 paths=[ROOT/'firmware/crab'/n for n in ['config.h','hardware.h']]+[ROOT/f'firmware/tests/test_{group}.cpp']
 flags=PROFILES[profile];args=[]
 if group in ('core','drivers','http'):paths += [ROOT/'firmware/crab/core.h',ROOT/'firmware/crab/continuous360.h',ROOT/'firmware/crab/drive360.h']
 if group in ('core','display'):paths += [ROOT/'firmware/crab'/n for n in ['qrcodegen.c','qrcodegen.h']]
 if group=='display':paths += [ROOT/'firmware/crab'/n for n in ['display.h','waveshare_panel.h','font_vi.h']]
 if group in ('drivers','display'):
  paths += ([ROOT/'firmware/crab/drivers.h',ROOT/'firmware/crab/actuator_output.h'] if group=='drivers' else [])+[p for p in (ROOT/'firmware/tests/stubs').rglob('*') if p.is_file()]
  args += ['-I'+str(ROOT/'firmware/tests/stubs')]
 if group=='http':
  paths += [ROOT/'firmware/crab'/n for n in ['network_http.h','web_ui.h']]+[ROOT/'firmware/tests/http_stubs.h',ROOT/'firmware/tests/stubs/pgmspace.h']
  args += ['-I'+str(ROOT/'firmware/tests/stubs')]
 # Include this runner (flags/compile recipe), not unrelated docs, in every key.
 d=hashlib.sha256((digest(paths+[Path(__file__)])+json.dumps(flags)+run(['clang++','--version'])).encode()).hexdigest()
 stamp=dest/f'{group}.sha256';exe=dest/f'test_{group}'
 products=[exe]+([dest/'gait-summary.json',dest/'gait.csv',dest/'qr1.pgm',dest/'qr2.pgm'] if group=='core' else ([dest/'panel-commands.txt'] if group=='display' and profile=='integrated' else []))
 if stamp.exists() and stamp.read_text()==d and all(p.exists() for p in products):
  result=f'SKIP {profile}: {group} unchanged (previously passed)'
 else:
  if group in ('core','display'):
   obj=dest/f'{group}-qr.o'
   run(['clang','-std=c99','-O2','-c',str(ROOT/'firmware/crab/qrcodegen.c'),'-o',str(obj)]);args += [str(obj)]
  run(['clang++','-std=c++11','-Wall','-Wextra','-Werror','-O2',*flags,*args,str(ROOT/f'firmware/tests/test_{group}.cpp'),'-o',str(exe)])
  result=run([str(exe)]+([str(dest)] if group in ('core','display') else []));stamp.write_text(d)
 return result,d

def core():
 results=pooled(lambda p:cpp('core',p),PROFILES)
 gait_report(results[0][1])
 # Independent Apple Vision decoder fed exact firmware QR bitmaps at LCD scale.
 from PIL import Image
 for i in (1,2):
  target=OUT/f'qr{i}.png';source=OUT/f'qr{i}.pgm'
  if not target.exists() or target.stat().st_mtime<source.stat().st_mtime:Image.open(source).save(target)
 swift=ROOT/'tools/firmware/qr_decode.swift';exe=OUT/'qr_decode';sd=digest([swift]);ss=OUT/'swift.sha256'
 if not exe.exists() or not ss.exists() or ss.read_text()!=sd:
  run(['swiftc','-num-threads',str(os.cpu_count()),'-module-cache-path',str(OUT/'swift-modules'),str(swift),'-o',str(exe)]);ss.write_text(sd)
 return '; '.join(r[0] for r in results)+'; '+run([str(exe),str(OUT)])
def web():return run(['node','firmware/tests/test_web.js'])+'; '+run(['node','firmware/tests/test_emote.js'])
def static():return run([sys.executable,'firmware/tests/test_interfaces.py'])
def drivers():return '; '.join(r[0] for r in pooled(lambda p:cpp('drivers',p),PROFILES))
def display():
 results=pooled(lambda p:cpp('display',p),PROFILES)
 return '; '.join(r[0] for r in results)+'; '+run([sys.executable,'firmware/tests/test_panel_vendor.py'])
def http():return '; '.join(r[0] for r in pooled(lambda p:cpp('http',p),PROFILES))
def targets():return '; '.join(r[0] for r in pooled(lambda p:cpp('targets',p),PROFILES))
checks={'core':core,'web':web,'interfaces':static,'drivers':drivers,'targets':targets,'display':display,'http':http}
selected=sys.argv[1:] or list(checks)
outputs={}
# The interface/doc-link check consumes GAIT-REPORT.json, produced by core.
# Respect that dependency in an empty clone; the remaining groups are independent.
if 'core' in selected:
 outputs['core']=core();print('core: '+outputs['core'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
 results={name:pool.submit(checks[name]) for name in selected if name!='core'}
 for name,f in results.items():outputs[name]=f.result();print(name+': '+outputs[name],flush=True)
if set(selected)==set(checks):
 paths=list((ROOT/'firmware/crab').glob('*'))+[p for p in (ROOT/'firmware/tests').rglob('*') if p.is_file()]+[ROOT/p for p in ['PILOT_CONTRACT.json','firmware/INTEGRATION.json','firmware/BUILD.json','firmware/BUILD-integrated.json','firmware/WIRING.md','firmware/README.md','firmware/OWNER-EVIDENCE.json','firmware/flash.json','firmware/flash-integrated.json','tools/firmware/check.py','tools/firmware/reconcile.py']]
 (ROOT/'firmware/TEST-RESULTS.json').write_text(json.dumps({'passed':True,'hardwareTested':False,
  'scope':'host regressions and binary integrity for both targets; board reconciliation separate',
  'releaseChainTip':'4cadb190eb0b3a92a9e7805c9956f41af7b085d71a2e18de54edbae19829277c',
  'implementedFirmwareNotes':[10,11,12,13,14,15,16,17,18],
  'ownerEvidence':'firmware/OWNER-EVIDENCE.json',
  'checks':outputs,'inputDigest':digest(paths),
  'integratedBoardStatus':json.loads((ROOT/'firmware/INTEGRATION.json').read_text())['integratedInterface']['status']},ensure_ascii=False,indent=2)+'\n')

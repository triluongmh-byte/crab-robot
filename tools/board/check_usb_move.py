#!/usr/bin/env python3
"""Note9 independent geometry, preserved-copper and measured DC/USB path audit."""
import concurrent.futures,hashlib,heapq,json,math,os,pathlib
from kicadpy import toolchain
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R);C=R/'build/board/usb-relocation';C.mkdir(parents=True,exist_ok=True)
source=R/'design/main.kicad_pcb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=R/'engineering/usb-relocation-baseline.json'
files=[source,manifest,R/'design/main.kicad_pro',pathlib.Path(__file__)]
key=hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest()
if (C/'audit.stamp').exists() and (C/'audit.stamp').read_text()==key and (R/'engineering/usb-relocation-audit.json').exists():
 print('USB relocation audit unchanged; cached pass');raise SystemExit
baseline=json.loads(manifest.read_text());current=toolchain.worker('inspect',source)
def fingerprint(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
refs=lambda s:{f['reference']:f for f in s['footprints']}
now=refs(current)
for r,h in baseline['footprintHashes'].items():assert fingerprint(now[r])==h,r
assert fingerprint([(p['number'],p['net']) for p in now['J1']['pads']])==baseline['J1PadNetHash']
assert sha(R/'design/main.kicad_pro')==baseline['projectRulesSha256']
assert now['J1']['at']==[21.45,-28] and now['J1']['rotationDeg'] in [-180,180]
assert current['boardBoundsMm']==[-44,-31,44,31]
assert current['thicknessMm']==1.6
assert current['copperLayers']==['F.Cu','B.Cu']
ct={t['uuid']:t for t in current['copper']}
for uuid,h in baseline['retainedCopperHashes'].items():assert fingerprint(ct[uuid])==h,uuid
def route(net,a,z,resistance=False):
 graph={}
 def edge(x,y,w):graph.setdefault(x,[]).append((y,w));graph.setdefault(y,[]).append((x,w))
 def point(x,l):return (*x,l)
 for t in current['copper']:
  if t['net']!=net:continue
  if t['kind']=='via':
   # Estimated conservative 15 um plated barrel, NOT a solid filled via.
   w=.0016*.0175/(math.pi*(.3+.015)*.015) if resistance else 1.6
   edge(point(t['at'],'F.Cu'),point(t['at'],'B.Cu'),w)
  elif t['kind']=='track':
   length=math.dist(t['start'],t['end']);w=length*.0175/(1000*.035*t['widthMm']) if resistance else length
   edge(point(t['start'],t['layer']),point(t['end'],t['layer']),w)
 start=point(a,'F.Cu');goal=point(z,'F.Cu');todo=[(0,start)];cost={start:0}
 while todo:
  d,q=heapq.heappop(todo)
  if d!=cost[q]:continue
  if q==goal:return d
  for n,w in graph.get(q,[]):
   v=d+w
   if v<cost.get(n,math.inf):cost[n]=v;heapq.heappush(todo,(v,n))
 raise AssertionError((net,'no graph path',a,z))
def pad(r,n):return next(p['at'] for p in now[r]['pads'] if p['number']==n)
lengths={n:route(n,pad('J1',jn),pad(r,'2'))+route(n+'_MCU',pad(r,'1'),pad('U1',un)) for n,jn,r,un in [('USB_DP','A6','R4','14'),('USB_DM','A7','R3','13')]}
resistance={n:route('PB1_5V',pad('J1',n),pad('U2','3'),True) for n in ['A4','A9']}
drop=max(resistance.values())*.560
assert max(lengths.values())<100 and abs(lengths['USB_DP']-lengths['USB_DM'])<10,lengths
assert drop<.1,drop
result={'passed':True,'sourcePCBsha256':sha(source),'releaseNoteSha256':'034b50d8298791a3011c5272db395aa2babb18093ff3843c3da109b633650101','J1':{'nativeOriginMm':[21.45,-28],'boardLocalOriginMm':[21.45,28],'rotationKiCadDeg':180,'mouthFaceBoardLocalYmm':32.8,'mouthFaces':'+Y','approvedPlugCentreXRangeMm':baseline['approvedPlugCentreXRangeMm']},'allOtherFootprintsUnchanged':True,'allRetainedCopperUnchanged':True,'retainedCopperItems':len(baseline['retainedCopperHashes']),'nativeUsbSignalPathMm':lengths,'pathSkewMm':abs(lengths['USB_DP']-lengths['USB_DM']),'estimatedFlightTimeNsAt6_3psPerMm':{n:l*.0063 for n,l in lengths.items()},'PB1FeederEstimatedOhm20C':resistance,'PB1EstimatedDropAt560mAV':drop,'limits':'Prototype FS USB only. No 90-ohm impedance, USB compliance or physical enumeration claim. See USB-RELOCATION.md. Native DRC and final case access remain separate.'}
(R/'engineering/usb-relocation-audit.json').write_text(json.dumps(result,indent=2)+'\n');(C/'audit.stamp').write_text(key)
print(json.dumps(result,indent=2))

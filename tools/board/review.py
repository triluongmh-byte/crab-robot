#!/usr/bin/env python3
"""Bind the final actual design/evidence hashes and measured factory corrections."""
import hashlib,json,os,pathlib
from kicadpy.manufacture import design_inputs,REVIEW_AREAS
from kicadpy.project import Project
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R)
parts=json.load(open('parts.json'))['parts'];rot=json.loads(pathlib.Path('build/board/rotation.log').read_text().splitlines()[-1])['result'];offsets={x['reference']:x['rotationOffsetDeg'] for x in rot['rows']}
# Keep the raw warning visible; accept only a separate, hash-bound all-pin audit.
poor=[x for x in rot['rows'] if x.get('poorMatch')]
assert all(x['reference']=='U1' for x in poor),poor
module=json.load(open('build/board/module-orientation.json'))
assert module['passed'] and module['verifiedOffsetDeg']==offsets['U1']==0
assert module['sourcePCBsha256']==hashlib.sha256((R/'design/main.kicad_pcb').read_bytes()).hexdigest()
assert module['factoryInputSha256']==hashlib.sha256((R/'engineering/factory-pads.json').read_bytes()).hexdigest()
ignored=json.load(open('engineering/check-policy.json'))['acceptedIgnoredChecks']
analysis={
'power':'Actual separate5V endpoint audit; USB4.8uFnominal/5.28uFworst;3V3reserve560mA versus1A LDO,415mA continuous thermal budget. Actual IC decoupling≤3mm. PCA /OE default-high GPIO21 and warm-reset reasoning documented.',
'protection':'User-authorized5V-only bought bank, separate positive rails/common ground, no forbidden protector or battery circuit. Labelled unpowered assembly, /OE pulse disable, no assumed source trip curve or default-off WS2812 retention claim.',
'pinout':'Manufacturer pad tables independently audited against native copper and real XML netlist. Full per-pad parity, no hollow symbols. Explicit documented SPI fallback8/39 and /OE21; GPIO15NC and straps/PSRAM/UART unused.',
 'thermal':'Native filled3V3 under LDO tab measured about3542mm²/10vias. Datasheet load and thermal calculation with25%theta margin,415mA continuous versus560mA transient reserve;2mmservo trunk. First-board thermal test remains explicit, no measured-temperature claim.',
'assembly':'29factory SMT references,15live exact supplier codes; native-vs-factory rotation measured(TI180deg,others0).37named THT joints across11connectors; factory/service hand solder preferred. No open via-in-pad. USB/switch conservative STEP envelopes are disclosed.',
'fabricator':'88x62x1.6mm2layer1oz explicit stackup; unchanged baseline rules/severities/noDRC exclusions. Actual power widths and drills, preserved USB pegs/slots and M3holes. Unmodified floor/packet check required, top assembly only.',
'bringup':'Vietnamese visual/power-on/QR/LED/servo steps, professional staged checks and explicit hardwareTested=false. Module assumptions and bank/LED/thermal/USB physical checks remain. Case/firmware must integrate final actual geometry/pinout.'}
d={'schemaVersion':1,'reviewer':'Codex board builder; independent tester and integration follow','designInputs':design_inputs(Project(R/'design/main.kicad_pro').root),'acceptedIgnoredChecks':ignored,'checks':{},'assembly':{}}
for part in parts:
 for ref in part['refdes']:
  method=part['assembly'];d['assembly'][ref]={'method':method}
  if method=='factory':d['assembly'][ref]['rotationOffsetDeg']=offsets[ref]
for area in REVIEW_AREAS:
 names=[f'engineering/{area}.md','engineering/sources.md']
 if area=='assembly':names+=['engineering/MUA-THEM-PCB.md','engineering/3D-MODELS.md','engineering/factory-pads.json']
 if area=='pinout':names+=['engineering/firmware-interface.md']
 d['checks'][area]={'status':'pass','analysis':analysis[area],'evidence':[{'path':n,'sha256':hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()} for n in names]}
pathlib.Path('manufacturing.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n');print('Integrated review bound to actual source and evidence hashes; gates unchanged.')

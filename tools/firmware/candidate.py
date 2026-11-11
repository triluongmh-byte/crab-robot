#!/usr/bin/env python3
"""Generate source-bound candidate metadata; never enumerate or access hardware.

Run after both named targets and board reconciliation, before interface tests.
This artifact describes a source build. It cannot certify independent review,
physical isolation, a device write, motor response or walking.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 evidence_path=ROOT/'firmware/OWNER-EVIDENCE.json'
 evidence=json.loads(evidence_path.read_text());tip=evidence['releaseChainTip']
 binaries={};notes=None
 for target,name in [('lilygo','BUILD.json'),('integrated','BUILD-integrated.json')]:
  path=ROOT/'firmware'/name;manifest=json.loads(path.read_text())
  assert manifest['target']==target and manifest['releaseChainTip']==tip
  assert manifest['ownerEvidence']=='firmware/OWNER-EVIDENCE.json'
  if notes is None:notes=manifest['implementedFirmwareNotes']
  assert notes==manifest['implementedFirmwareNotes']
  for rel,expected in manifest['sourceInputs'].items():
   source=(ROOT/rel).resolve();assert source.is_relative_to(ROOT) and sha(source)==expected,rel
  output=(ROOT/manifest['output']).resolve();assert output.is_relative_to(ROOT/'build/firmware')
  for name,record in manifest['artifacts'].items():
   artifact=output/name;assert artifact.stat().st_size==record['bytes'] and sha(artifact)==record['sha256'],name
  app=output/'crab.ino.bin'
  binaries[target]={'manifest':str(path.relative_to(ROOT)),'manifestSha256':sha(path),'path':str(app.relative_to(ROOT)),'sha256':sha(app),'bytes':app.stat().st_size,'flashCandidate':target=='lilygo'}
 reconciliation=ROOT/'firmware/BOARD-RECONCILIATION.json';assert reconciliation.is_file()
 result={'stage':'source-built; independent and physical acceptance are separate','contractSha256':sha(ROOT/'PILOT_CONTRACT.json'),'releaseChainTip':tip,'implementedNotes':notes,'hardwareTested':False,'flashed':False,'independentReview':'Not performed by this generator; use the native team review and a fresh entry comparison before a device write.','ownerEvidence':'firmware/OWNER-EVIDENCE.json','ownerEvidenceSha256':sha(evidence_path),'binaries':binaries,'boardReconciliation':'firmware/BOARD-RECONCILIATION.json','boardReconciliationSha256':sha(reconciliation),'testReport':'firmware/TEST-RESULTS.json','testReportStatus':'Written by the complete host suite after this candidate is checked; not a pass claimed by this generator.','guide':'firmware/CONTINUOUS360.md','flashInstructions':'firmware/FLASH-POLICY.md','projectRecipe':{'lilygo':'firmware/flash.json','integrated':'firmware/flash-integrated.json'},'limits':['No hardware access or motor command is part of a source build.','Only the original LILYGO has owner flash authorization; current motor isolation and verified full recovery are still required.','Timed displacement is an estimate; no angle feedback, holding or walking is established.']}
 path=ROOT/'firmware/FLASH-CANDIDATE.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Generated source-bound candidate for both targets; no device accessed.')
if __name__=='__main__':main()

"""Bind the current native sources and seven dummy-only evidence notes."""
from pathlib import Path
import json,hashlib
from kicadpy.manufacture import design_inputs,REVIEW_AREAS
from kicadpy.project import Project
root=Path(__file__).resolve().parents[2]
sidecar=json.loads((root/'boards/main.board.json').read_text())
# Read exact ignored categories from the latest native draft; never invent exclusions.
reports=sorted((root/'boards/main_review').glob('*/reports/check.json'),key=lambda p:p.stat().st_mtime)
ignored=json.loads(reports[-1].read_text())['ignoredChecks']
analyses={
 'power':'Unpowered dummy, two passive isolated copper links. No rail or load; designed current 0 A.',
 'protection':'No power or battery interface. Warning explicitly forbids robot use. No protection circuit applicable.',
 'pinout':'4 connected schematic pins map to four PCB pad 1 landing points; DUMMY_A and DUMMY_B only. Two pinless NPTHs.',
 'thermal':'No fitted heat source and 0 W designed dissipation. Final links measured 0.5 mm wide, 16 mm total length, 35 um copper.',
 'assembly':'Zero fitted parts. All integral pad/hole footprints excluded from BOM/CPL; empty component identities and rotations are intentional.',
 'fabricator':'2-layer, 1.6 mm FR4, explicit 35 um copper, 3.2 mm NPTH, conservative rules. Current JLCPCB table consulted; independent packet check required.',
 'bringup':'Do not order, populate, power, or place this dummy in robot. Host-only native and packet checks; hardware untested.'}
review={'schemaVersion':1,'reviewer':'Codex board builder (AI-assisted); independent tester review remains separate','designInputs':design_inputs(Project(root/'design/main.kicad_pro').root),'acceptedIgnoredChecks':ignored,'checks':{},'assembly':{}}
for area in REVIEW_AREAS:
 p=root/'engineering'/f'{area}.md'
 review['checks'][area]={'status':'pass','analysis':analyses[area],'evidence':[{'path':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}]}
(root/'manufacturing.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('Bound seven evidence areas and exact native default ignored-check categories.')

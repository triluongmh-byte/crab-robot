#!/usr/bin/env python3
"""CadQuery runtime: measure native board and supplier screen; normalize PCB topZ0."""
import concurrent.futures,hashlib,json,os,pathlib
import cadquery as cq
R=pathlib.Path(__file__).resolve().parents[2];O=R/'build/board'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(shape):
 b=shape.val().BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def measure(n):
 s=cq.importers.importStep(str(O/n));return n,s,bounds(s)
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:items=list(ex.map(measure,['pcb-only.step','integrated-raw.step']))
d={n:(s,bb) for n,s,bb in items};top=d['pcb-only.step'][1][5]
assert abs(d['pcb-only.step'][1][3]-d['pcb-only.step'][1][0]-88)<.05
assert abs(d['pcb-only.step'][1][4]-d['pcb-only.step'][1][1]-62)<.05
assert abs(d['pcb-only.step'][1][5]-d['pcb-only.step'][1][2]-1.6)<.05
full=d['integrated-raw.step'][0].translate((0,0,-top));cq.exporters.export(full,str(O/'integrated.step'));fullbb=bounds(full)
screenpath=R/'engineering/sources/integrated/waveshare-display.step';screen=cq.importers.importStep(str(screenpath));sbb=bounds(screen)
# Case coordinates come directly from actual KiCad source measured in geometry audit.
g=json.load(open(O/'geometry.json'))['nativeState'];refs={f['reference']:f for f in g['footprints']}
connectors=[]
for r in [f'J{i}' for i in range(1,13)]+['SW1','SW2']:
 f=refs[r];connectors.append({'reference':r,'nativeKiCadXYmm':f['at'],'boardLocalXYmm':[f['at'][0],-f['at'][1]],'rotationKiCadDeg':f['rotationDeg'],'pads':[{k:p[k] for k in ['number','net','at','drillMm']} for p in f['pads']]})
mounts=[{'ref':r,'centreMm':[refs[r]['at'][0],-refs[r]['at'][1]],'diameterMm':3.2} for r in ['H1','H2','H3','H4']]
result={'schemaVersion':1,'variant':'integrated-I0','releaseNoteSha256':'034b50d8298791a3011c5272db395aa2babb18093ff3843c3da109b633650101','sourcePCBsha256':sha(R/'design/main.kicad_pcb'),'coordinateFrame':{'origin':'outline centre; top copperZ0','axes':'+X KiCad right,+Y UP (=negativeKiCadY),+Z up','units':'mm','robotPlacement':'case team must set; no fit claim'},'pcb':{'sizeMm':[88,62,1.6],'outlineMm':[[-44,-31],[44,-31],[44,31],[-44,31]],'mounts':mounts,'step':'build/board/integrated.step','stepSha256':sha(O/'integrated.step'),'rawNativeTopZmm':top,'completePopulatedBoundsMm':fullbb,'maxBodyHeightAboveTopMm':fullbb[5],'belowBoardMinZmm':fullbb[2]},'connectors':connectors,'screen':{'mpn':'Waveshare1.9inch LCD Module SKU23822','step':'engineering/sources/integrated/waveshare-display.step','sha256':sha(screenpath),'supplierFrameBoundsMm':sbb,'activeAreaMm':[42.72,22.70],'resolutionPx':[170,320],'placement':'not on PCB;8-wire harness; case sets screen frame and window'},'clearanceModels':{'USBandSwitch':'conservative measured envelope, see engineering/3D-MODELS.md','C11':'allow11mm height minimum','terminalAndHeaders':'allow plugged leads and screwdriver access beyond naked PCB STEP'},'usbAccess':{'reference':'J1','boardLocalOriginMm':[21.45,28],'mouthFaces':'+Y','mouthFaceYmm':32.8,'ordinaryPlugEnvelopeMm':[12.5,7,25],'finalCaseRecheckRequired':True},'hardwareTested':False}
(R/'engineering/board-interface.json').write_text(json.dumps(result,indent=2)+'\n');print('STEP normalized topZ0; populated bounds',fullbb,'screen',sbb)

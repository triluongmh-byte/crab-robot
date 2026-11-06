"""Native geometry and contract audit; tiny exact checks, no sampling needed."""
from pathlib import Path
import json,hashlib
import wx
app=wx.App(False)
import pcbnew as k
root=Path(__file__).resolve().parents[2];source=root/'design/main.kicad_pcb'
fingerprint=hashlib.sha256(source.read_bytes()+Path(__file__).read_bytes()+(root/'PILOT_CONTRACT.json').read_bytes()).hexdigest()
report=root/'build/board/geometry.json'
if report.exists() and json.loads(report.read_text()).get('inputSha256')==fingerprint:
 print('Geometry unchanged: reused exact audit');raise SystemExit(0)
b=k.LoadBoard(str(source));M=k.ToMM
outline=sorted((round(M(p.x),6),round(M(p.y),6)) for d in b.GetDrawings() if d.GetLayer()==k.Edge_Cuts for p in (d.GetStart(),d.GetEnd()))
assert outline==sorted([(-15,-10),(15,-10),(15,-10),(15,10),(15,10),(-15,10),(-15,10),(-15,-10)]),outline
assert b.GetCopperLayerCount()==2
assert abs(M(b.GetDesignSettings().GetBoardThickness())-1.6)<1e-6
fps={f.GetReference():f for f in b.GetFootprints()}
assert set(fps)=={'J1','J2','J3','J4','MH1','MH2'}
measurements=[]
for ref,x in [('MH1',-10),('MH2',10)]:
 f=fps[ref];p=list(f.Pads())[0]
 assert p.GetAttribute()==k.PAD_ATTRIB_NPTH
 assert (round(M(f.GetPosition().x),6),round(M(f.GetPosition().y),6))==(x,0)
 assert (round(M(p.GetDrillSize().x),6),round(M(p.GetDrillSize().y),6))==(3.2,3.2)
 measurements.append({'ref':ref,'xyMm':[x,0],'npthDiameterMm':3.2})
for i in range(1,5):
 f=fps[f'J{i}'];p=list(f.Pads())[0]
 assert p.GetNumber()=='1'
 assert p.GetNetname()==('DUMMY_A' if i<3 else 'DUMMY_B')
 assert p.GetLayerSet().Contains(k.F_Cu) and p.GetLayerSet().Contains(k.F_Mask)
 assert not p.GetLayerSet().Contains(k.F_Paste)
 assert (round(M(p.GetSize().x),6),round(M(p.GetSize().y),6))==(2,3)
 assert f.GetAttributes() & k.FP_EXCLUDE_FROM_BOM
 assert f.GetFPID().GetLibNickname()=='Dummy'
text=' '.join(d.GetText() for d in b.GetDrawings() if isinstance(d,k.PCB_TEXT))
assert 'BOARD GIẢ - KHÔNG ĐẶT - KHÔNG ĐẶT VÀO ROBOT' in text
tracks=list(b.GetTracks());assert tracks
widths=[M(t.GetWidth()) for t in tracks]
assert min(widths)>=.25
assert {t.GetNetname() for t in tracks}=={'DUMMY_A','DUMMY_B'}
assert all(t.GetLayer()==k.F_Cu for t in tracks)
assert not list(b.Zones())
result={'inputSha256':fingerprint,'pass':True,'outlineMm':[30,20],'thicknessMm':1.6,'copperLayers':2,'holes':measurements,'landingPads':4,'fittedComponents':0,'nets':['DUMMY_A','DUMMY_B'],'trackWidthsMm':widths,'totalTrackLengthMm':sum(M(t.GetLength()) for t in tracks),'silkscreen':text,'hardwareTested':False}
report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))

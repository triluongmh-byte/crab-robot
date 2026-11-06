"""KiCad-bundled Python: create local integral-pad footprints and board geometry."""
import json
from pathlib import Path
import wx
_app=wx.App(False)
import pcbnew as k
io=k.PCB_IO_MGR.FindPlugin(k.PCB_IO_MGR.KICAD_SEXP)
mm=k.FromMM
V=lambda x,y:k.VECTOR2I(mm(x),mm(y))
root=Path(__file__).resolve().parents[2]
meta=json.loads((root/'build/board/instances.json').read_text())
out=root/'design'; lib=out/'Dummy.pretty';lib.mkdir(exist_ok=True)
b=k.BOARD(); b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(mm(1.6))
title=k.TITLE_BLOCK();title.SetTitle('BOARD GIẢ - KHÔNG ĐẶT - KHÔNG ĐẶT VÀO ROBOT');title.SetRevision('A');title.SetDate('2026-11-06');b.SetTitleBlock(title)
# A pad is PCB copper, not an assembled component. No paste opening.
padfp=k.FOOTPRINT(b);padfp.SetFPID(k.LIB_ID('Dummy','SolderPad_2x3mm'))
padfp.SetAttributes(k.FP_SMD | k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES)
p=k.PAD(padfp);p.SetNumber('1');p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_ROUNDRECT);p.SetSize(V(2,3));p.SetRoundRectRadiusRatio(.2);layers=k.LSET();layers.AddLayer(k.F_Cu);layers.AddLayer(k.F_Mask);p.SetLayerSet(layers);padfp.Add(p)
padfp.Reference().SetPosition(V(0,-2.1));padfp.Reference().SetTextSize(V(.8,.8));padfp.Reference().SetTextThickness(mm(.15));padfp.Value().SetVisible(False)
io.FootprintSave(str(lib),padfp)
# Bundled KiCad mounting-hole geometry copied locally, no part installed.
hole=io.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty','MountingHole_3.2mm_M3')
hole.SetFPID(k.LIB_ID('Dummy','MountingHole_3.2mm_M3'));hole.SetAttributes(k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES)
for graphic in hole.GraphicalItems():
 if graphic.GetLayer() in (k.F_SilkS,k.B_SilkS): graphic.SetWidth(mm(.15))
hole.Reference().SetTextSize(V(.8,.8));hole.Reference().SetTextThickness(mm(.15));hole.Reference().SetVisible(True);hole.Value().SetVisible(False)
io.FootprintSave(str(lib),hole)
(out/'fp-lib-table').write_text('(fp_lib_table (version 7)\n (lib (name "Dummy")(type "KiCad")(uri "${KIPRJMOD}/Dummy.pretty")(options "")(descr "Integral bare pads and KiCad NPTH hole"))\n)\n')
nets={}
for name in ['DUMMY_A','DUMMY_B']:
 n=k.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
placements={'J1':(-4,-1.8),'J2':(4,-1.8),'J3':(-4,3.8),'J4':(4,3.8),'MH1':(-10,0),'MH2':(10,0)}
for ref,(x,y) in placements.items():
 name='SolderPad_2x3mm' if ref.startswith('J') else 'MountingHole_3.2mm_M3'
 f=io.FootprintLoad(str(lib),name);f.SetFPID(k.LIB_ID('Dummy',name));f.SetReference(ref);f.SetValue('SOLDER_PAD_'+ref[1:] if ref.startswith('J') else 'NPTH_3.2mm');f.SetPosition(V(x,y))
 f.SetField('Description','Integral bare PCB solder pad; nothing fitted' if ref.startswith('J') else '')
 f.SetPath(k.KIID_PATH('/'+meta['root']+'/'+meta['symbols'][ref]))
 if ref.startswith('J'):
  for p in f.Pads(): p.SetNet(nets['DUMMY_A' if ref in ['J1','J2'] else 'DUMMY_B'])
 b.Add(f)
for (x1,y1),(x2,y2) in zip([(-15,-10),(15,-10),(15,10),(-15,10)],[ (15,-10),(15,10),(-15,10),(-15,-10)]):
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(V(x1,y1));s.SetEnd(V(x2,y2));s.SetLayer(k.Edge_Cuts);s.SetWidth(mm(.05));b.Add(s)
for txt,y,size in [('BOARD GIẢ - KHÔNG ĐẶT -',-7.6,.9),('KHÔNG ĐẶT VÀO ROBOT',-5.8,.9),('DO NOT ORDER / FIT',8,.8)]:
 t=k.PCB_TEXT(b);t.SetText(txt);t.SetPosition(V(0,y));t.SetTextSize(V(size,size));t.SetTextThickness(mm(.15));t.SetLayer(k.F_SilkS);b.Add(t)
b.GetDesignSettings().m_AuxOrigin=V(-15,10)
k.SaveBoard(str(out/'main.kicad_pcb'),b)
# Explicit standard 1 oz / 1.6 mm stackup; PCB API lacks a stackup writer.
path=out/'main.kicad_pcb';text=path.read_text();stack='''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "HASL lead-free") (dielectric_constraints no)
)'''
text=text.replace('(setup','(setup\n'+stack,1);path.write_text(text)
print('Created dummy board; unrouted draft, 4 solder pads, 2 holes.')

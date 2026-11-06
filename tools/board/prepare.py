"""Prepare the dummy-only schematic input and native project rules."""
from pathlib import Path
import json
W='BOARD GIẢ - KHÔNG ĐẶT - KHÔNG ĐẶT VÀO ROBOT'
spec={'title':W,'rev':'A','date':'2026-11-06','company':'Dummy only; no robot electronics','paper':'A4','lib':'Dummy','stem':'main','libraries':['Connector_Generic','Mechanical'],'parts':[], 'nets':{'DUMMY_A':[['J1','1'],['J2','1']],'DUMMY_B':[['J3','1'],['J4','1']]}}
for n,xy in enumerate([(76.2,76.2),(127,76.2),(76.2,111.76),(127,111.76)],1):
 spec['parts'].append({'ref':f'J{n}','value':f'SOLDER_PAD_{n}','symbol':'Conn_01x01','footprint':'Dummy:SolderPad_2x3mm','at':xy,'in_bom':False,'description':'Integral bare PCB solder pad; nothing fitted'})
for n,x in enumerate([76.2,127],1):
 spec['parts'].append({'ref':f'MH{n}','value':'NPTH_3.2mm','symbol':'MountingHole','footprint':'Dummy:MountingHole_3.2mm_M3','at':[x,149.86],'in_bom':False})
Path('tools/board/spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n')
project={'meta':{'filename':'main.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':0.2,'min_track_width':0.25,'min_via_diameter':0.6,'min_through_hole_diameter':0.3,'min_via_annular_width':0.15,'min_copper_edge_clearance':0.5,'min_hole_clearance':0.25,'min_silk_clearance':0.15,'min_silk_text_height':0.8,'min_silk_text_thickness':0.12},'rule_severities':{}}},'net_settings':{'classes':[{'name':'Default','description':'Dummy unpowered links','clearance':0.2,'track_width':0.5,'via_diameter':0.6,'via_drill':0.3,'bus_width':12,'wire_width':6}],'meta':{'version':3}},'erc':{'erc_exclusions':[]},'schematic':{}}
Path('design/main.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
Path('parts.json').write_text(json.dumps({'schemaVersion':1,'parts':[],'description':'Bare dummy PCB only: integral copper pads and NPTH holes, no purchased or fitted components; no stock claim.'},indent=2)+'\n')
p=json.load(open('product.json'));p['board']={'name':'DUMMY - not part of robot','outlineMm':[[-15,-10],[15,-10],[15,10],[-15,10],[-15,-10]],'thicknessMm':1.6,'layers':2,'copperOz':1,'mounts':[{'ref':'MH1','xMm':-10,'yMm':0,'holeDiameterMm':3.2},{'ref':'MH2','xMm':10,'yMm':0,'holeDiameterMm':3.2}],'fittedParts':0,'powered':False};p['hardwareTested']=False;p['nativePCBCheckerAppliesToRobot']=False
Path('product.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')

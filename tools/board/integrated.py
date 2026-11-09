#!/usr/bin/env python3
"""Generate the note4 integrated native design. Stable input cache; no routing here."""
import hashlib,json,os,pathlib,re,shutil,subprocess
from kicadpy import author,toolchain,verify
from kicadpy.sexp import parse,child,value
ROOT=pathlib.Path(__file__).resolve().parents[2];os.chdir(ROOT)
D=ROOT/'design';OUT=ROOT/'build/board';OUT.mkdir(parents=True,exist_ok=True)
SHARE=pathlib.Path(toolchain.BUNDLE)/'SharedSupport'
def dump(p,d):pathlib.Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def generate():
 key=hashlib.sha256(pathlib.Path(__file__).read_bytes()+pathlib.Path('tools/board/integrated_pcb.py').read_bytes()).hexdigest()
 stamp=OUT/'integrated-generation.json'
 if stamp.exists():
  old=json.loads(stamp.read_text())
  if old['key']==key and all(pathlib.Path(n).exists() and hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==h for n,h in old['outputs'].items()):print('Integrated inputs unchanged; generation skipped.');return
 parts=[];nets={};placements={};bom={};libs={}
 def add(ref,val,sym,fp,xy,rot=0,lib=None,code=None,maker=None,mpn=None,method='factory',source=None):
  if lib is None:lib={'R':'Device','C':'Device','C_Polarized':'Device','MountingHole':'Mechanical','TestPoint':'Connector','PWR_FLAG':'power'}.get(sym,'Connector_Generic')
  libs[lib]=True
  n=len(parts);schxy=[60+100*(n//9),55+38*(n%9)]
  if ref=='U1':schxy=[75,100]
  elif ref=='U2':schxy=[75,185]
  elif ref=='U3':schxy=[75,290]
  elif ref=='J1':schxy=[175,95]
  elif n<4:schxy=[175,195]
  part={'ref':ref,'value':val,'symbol':sym,'footprint':'Local:'+fp if fp else '', 'at':schxy}
  if ref.startswith(('H','TP','#')):part['in_bom']=False
  parts.append(part);placements[ref]=[*xy,rot]
  if fp and not ref.startswith(('H','TP','#')):
   bom[ref]={'manufacturer':maker,'mpn':mpn,'lcsc':code,'assembly':method,'native_footprint':'Local:'+fp,'refdes':[ref],'source':source or ('https://www.lcsc.com/product-detail/'+code+'.html' if code else ''),'checkedDate':'2026-11-09'}
 def net(n,*pins):
  for r,p in pins:nets.setdefault(n,[]).append([r,str(p)])
 def rc(ref,val,code,xy,n1,n2,rot=0):
  iscap=ref.startswith('C');fp=('C_0805_2012Metric' if code in ['C15850','C1746'] else 'C_0402_1005Metric') if iscap else 'R_0402_1005Metric'
  known=json.loads(pathlib.Path('build/board/all-knowledge.txt').read_text().splitlines()[-1])['result'].get(code,{}).get('identity') or {}
  if code=='C25092':known={'manufacturer':'UNI-ROYAL','mpn':'0402WGF220JTCE'}
  add(ref,val,'C' if iscap else 'R',fp,xy,rot,code=code,maker=known.get('manufacturer'),mpn=known.get('mpn'))
  net(n1,(ref,1));net(n2,(ref,2))
 add('U1','ESP32-S3-WROOM-1-N16R8','ESP32-S3-WROOM-1','ESP32-S3-WROOM-1',[-23,-18.25],lib='RF_Module',code='C2913202',maker='Espressif Systems',mpn='ESP32-S3-WROOM-1-N16R8')
 add('U2','TLV1117LV33DCYR','TLV1117-33','SOT-223-3_TabPin2',[-29,8],lib='Regulator_Linear',code='C15578',maker='Texas Instruments',mpn='TLV1117LV33DCYR')
 add('U3','PCA9685PW,118','PCA9685PW','TSSOP-28_4.4x9.7mm_P0.65mm',[10,0],lib='Driver_LED',code='C2678753',maker='NXP',mpn='PCA9685PW,118')
 add('J1','USB-C PB1_5V + USB','USB_C_Receptacle_USB2.0_16P','USB_C_Receptacle_HRO_TYPE-C-31-M-12',[-41,0],-90,lib='Connector',code='C165948',maker='Korean Hroparts Elec',mpn='TYPE-C-31-M-12')
 for pin in [1,40,41]:net('GND',('U1',pin))
 net('3V3',('U1',2),('U2',2),('U3',28));net('GND',('U2',1),('U3',14))
 net('PB1_5V',('U2',3))
 for pin in ['A4','A9','B4','B9']:net('PB1_5V',('J1',pin))
 for pin in ['A1','A12','B1','B12','SH']:net('GND',('J1',pin))
 net('USB_DP',('J1','A6'),('J1','B6'));net('USB_DM',('J1','A7'),('J1','B7'))
 rc('R1','5.1k','C25905',[-34,0],'USB_CC1','GND',90);net('USB_CC1',('J1','A5'))
 rc('R2','5.1k','C25905',[-34,2.5],'USB_CC2','GND',90);net('USB_CC2',('J1','B5'))
 rc('R3','22','C25092',[-35.5,-8],'USB_DM_MCU','USB_DM',90);net('USB_DM_MCU',('U1',13))
 rc('R4','22','C25092',[-34.2,-4.6],'USB_DP_MCU','USB_DP',90);net('USB_DP_MCU',('U1',14))
 rc('R5','10k','C25744',[-35,-14.5],'3V3','CHIP_EN');net('CHIP_EN',('U1',3))
 rc('C1','1uF','C52923',[-34,-11],'CHIP_EN','GND',90)
 rc('R6','10k','C25744',[-12,-8],'3V3','BTN_BOOT');net('BTN_BOOT',('U1',27))
 rc('C2','4.7uF','C1746',[-35,10.3],'PB1_5V','GND',180)
 rc('C3','100nF','C1525',[-33,12.7],'PB1_5V','GND')
 rc('C4','10uF','C15850',[-22.9,8],'3V3','GND')
 rc('C5','10uF','C15850',[-35,8],'3V3','GND',180)
 rc('C6','100nF','C1525',[-34,-22.24],'3V3','GND')
 rc('C7','10uF','C15850',[-37,-19],'3V3','GND',90)
 rc('C8','100nF','C1525',[15.5,-4.2],'3V3','GND')
 rc('C9','1uF','C52923',[18,-2],'3V3','GND')
 rc('R7','4.7k','C25900',[-2,-7],'3V3','I2C_SDA');net('I2C_SDA',('U1',11),('U3',27))
 rc('R8','4.7k','C25900',[-2,-4],'3V3','I2C_SCL');net('I2C_SCL',('U1',10),('U3',26))
 rc('R9','10k','C25744',[1,-1],'3V3','SERVO_OE');net('SERVO_OE',('U1',23),('U3',23))
 for pin in [1,2,3,4,5,24,25]:net('GND',('U3',pin))
 for i in range(8):
  ref=f'J{i+2}';add(ref,f'CH{i} GND 5V PWM','Conn_01x03','PinHeader_1x03_P2.54mm_Vertical',[-16+i*7,17],maker='Samtec',mpn='TSW-103-07-G-S',method='manual',source='https://www.samtec.com/products/tsw-103-07-g-s')
  net('GND',(ref,1));net('SERVO_5V',(ref,2));net(f'SERVO_PWM_{i}',('U3',6+i),(ref,3))
 add('J10','Waveshare23822 BL RES DC CS SCK MOSI GND 3V3','Conn_01x08','PinHeader_1x08_P2.54mm_Vertical',[6,-20],90,maker='Samtec',mpn='TSW-108-07-G-S',method='manual',source='https://www.samtec.com/products/tsw-108-07-g-s')
 for pin,n,mp in [(1,'LCD_BL',31),(2,'LCD_RES',5),(3,'LCD_DC',7),(4,'LCD_CS',6),(5,'LCD_SCLK',12),(6,'LCD_MOSI',32)]:net(n,('J10',pin),('U1',mp))
 net('GND',('J10',7));net('3V3',('J10',8))
 rc('R10','10k','C25744',[-6,-18],'LCD_RES','GND')
 rc('R11','10k','C25744',[-6,-15],'3V3','LCD_CS')
 rc('R12','330','C25104',[-6,-12],'LCD_BL','GND')
 rc('C10','100nF','C1525',[26,-16],'3V3','GND')
 add('J11','LED DIN 5V GND','Conn_01x03','PinHeader_1x03_P2.54mm_Vertical',[22,27],90,maker='Samtec',mpn='TSW-103-07-G-S',method='manual',source='https://www.samtec.com/products/tsw-103-07-g-s')
 net('LED_DIN',('U1',39),('J11',1));net('SERVO_5V',('J11',2));net('GND',('J11',3))
 add('J12','SERVO INPUT +5V GND','Conn_01x02','TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',[36,3],90,maker='Phoenix Contact',mpn='1715721 / MKDS 1,5/ 2-5,08',method='manual',source='https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-15-2-508-1715721')
 net('SERVO_5V',('J12',1));net('GND',('J12',2))
 # 1000uF servo bulk: exact knowledge identity; copied standard case land dimensions audited separately.
 add('C11','1000uF','C_Polarized','CP_Elec_10x10',[22,7],code='C970714',maker='DMBJ',mpn='RVT1C102M1010')
 net('SERVO_5V',('C11',1));net('GND',('C11',2))
 for ref,n,xy in [('SW1','BTN_BOOT',[-6,3]),('SW2','CHIP_EN',[-6,10])]:
  add(ref,'BOOT' if ref=='SW1' else 'RESET','SW_Push','SW_Push_1P1T_XKB_TS-1187A',xy,lib='Switch',code='C318884',maker='XKB Connection',mpn='TS-1187A-B-A-B');net(n,(ref,1));net('GND',(ref,2))
 for i,xy in enumerate([[-40,-13],[39,-26],[-39,26],[39,26]],1):add(f'H{i}',f'H{i}','MountingHole','MountingHole_3.2mm_M3',xy)
 for i,(n,xy) in enumerate([('PB1_5V',[-35,15]),('SERVO_5V',[35,12]),('3V3',[-24,15]),('GND',[-29,15])],1):add(f'TP{i}',n,'TestPoint','TestPoint_Pad_D2.0mm',xy);net(n,(f'TP{i}',1))
 for i,n in enumerate(['PB1_5V','GND','SERVO_5V'],1):add(f'#FLG0{i}','PWR_FLAG','PWR_FLAG','',[500,30+i*10]);net(n,(f'#FLG0{i}',1))
 # Arrange schematic groups with no overlap. Native A1 sheet; all author pins on grid.
 for i,p in enumerate(parts):
  r=p['ref']
  if r.startswith('R'):p['at']=[275+75*((int(r[1:])-1)//6),55+45*((int(r[1:])-1)%6)]
  elif r.startswith('C'):p['at']=[430+75*((int(r[1:])-1)//6),55+45*((int(r[1:])-1)%6)]
  elif r.startswith('J') and r!='J1':p['at']=[180+75*((int(r[1:])-2)//6),185+33*((int(r[1:])-2)%6)]
  elif r.startswith('SW'):p['at']=[580,60+50*int(r[-1])]
  elif r.startswith('H'):p['at']=[580,250+25*int(r[-1])]
  elif r.startswith('TP'):p['at']=[655,250+25*int(r[-1])]
  elif r.startswith('#'):p['at']=[655,40+25*int(r[-1])]
 spec={'title':'CRAB INTEGRATED ESP32-S3 + 8 SERVO V0','date':'2026-11-09','rev':'I0','company':'Circuit pilot / release4','paper':'A1','lib':'Integrated','stem':'main','libraries':list(libs),'parts':parts,'nets':nets}
 dump('design/spec.json',spec);dump(OUT/'placements.json',placements);dump('parts.json',{'schemaVersion':1,'parts':list(bom.values()),'note':'Integrated note4 V0; factory SMT, named manual THT. External Waveshare23822 screen not on PCB BOM.'})
 product={'name':'Robot Cua — integrated ESP32-S3 board V0','description':'Integrated certified radio + PCA9685, factory SMT, native USB and separate5V servo input; Waveshare23822 SPI screen fallback. Release note4 supersedes passive carrier.','board':{'sizeMm':[88,62],'thicknessMm':1.6,'layers':2,'copperOz':1,'outlineMm':[[-44,-31],[44,-31],[44,31],[-44,31]],'mounts':[{'ref':f'H{i}','positionMm':xy,'holeDiameterMm':3.2} for i,xy in enumerate([[-40,-13],[39,-26],[-39,26],[39,26]],1)]},'hardwareTested':False,'railLimitsUF':{'PB1_5V':10},'powerEntryNets':['PB1_5V','SERVO_5V'],'power':{'logicReserveA':0.56,'ldoRatedA':1,'servoSourceA':2.4,'LED_designMaxA':0.48},'assumptions':['GIẢ ĐỊNH: external WS2812 accepts direct3.3V DIN; retains colour on warm MCU reset.','PCA9685 module đã mua, chưa xác nhận đã nhận; not used in integrated variant.','Power bank operation under servo transient load requires real assembly check.','Case team must place PCB and documented Waveshare display from final STEP.'], 'releaseNoteSha256':'122b5b3d406fc1cc148b6bf5abaf6c6fc7315e933a95e5565c1b60ee86d35e08','pinChanges':{'GPIO15':'NC legacy LCD_POWER_ON','GPIO21':'PCA9685 /OE activeLOW; defaultHIGH','GPIO8':'LCD SPI SCLK formerlyWR','GPIO39':'LCD SPI MOSI formerlyD0','GPIO9,40,41,42,45,46,47,48':'NC formerlyLCD parallel bus'}}
 dump('product.json',product)
 # Refresh local footprints from bundled KiCad source and localize all STEP models.
 fpdir=D/'Local.pretty';fpdir.mkdir(exist_ok=True);md=D/'Local.3dshapes';md.mkdir(exist_ok=True)
 for name in sorted({p['footprint'].split(':',1)[1] for p in parts if p['footprint']}):
  matches=list((SHARE/'footprints').glob('*.pretty/'+name+'.kicad_mod'))
  if len(matches)!=1:raise ValueError((name,matches))
  text=matches[0].read_text().replace('(width 0.12)','(width 0.15)')
  if name=='ESP32-S3-WROOM-1':
   tree=parse(text)
   # Solid exposed pad, no open via-in-pad solder-wicking. Ground vias added outside EP.
   tree=[k for k in tree if not (isinstance(k,list) and k and k[0]=='pad' and value(k[1])=='41' and k[2]=='thru_hole')]
   text=author._dump(tree)+'\n'
  if name=='CP_Elec_10x10':
   tree=parse(text)
   for k in tree:
    if not isinstance(k,list) or not k:continue
    if k[0]=='pad' and value(k[1]) in ['1','2']:
     at=child(k,'at');at[1]='-4.5' if value(k[1])=='1' else '4.5';sz=child(k,'size');sz[1:]=['4.5','1.65']
    if k[0]=='fp_line' and child(k,'layer') and value(child(k,'layer')[1])=='F.CrtYd':
     for pt in k:
      if isinstance(pt,list) and pt[0] in ['start','end'] and abs(float(pt[1]))>5:pt[1]=str(7.1 if float(pt[1])>0 else -7.1)
   tree=[k for k in tree if not (isinstance(k,list) and k and k[0]=='fp_line' and child(k,'layer') and value(child(k,'layer')[1])=='F.CrtYd')]
   pts=[(-7.1,-5.6),(7.1,-5.6),(7.1,5.6),(-7.1,5.6)]
   for a,z in zip(pts,pts[1:]+pts[:1]):tree.append(['fp_line',['start',str(a[0]),str(a[1])],['end',str(z[0]),str(z[1])],['stroke',['width','0.05'],['type','solid']],['layer','"F.CrtYd"']])
   text=author._dump(tree)+'\n'
  # Move only off-board decorative silk to fabrication, retaining footprint identity.
  if name in ['ESP32-S3-WROOM-1','USB_C_Receptacle_HRO_TYPE-C-31-M-12']:
   tree=parse(text)
   for item in tree:
    if not isinstance(item,list) or item[0] not in ['fp_line','fp_arc']:continue
    layer=child(item,'layer')
    if not layer or value(layer[1])!='F.SilkS':continue
    ys=[float(k[2]) for k in item if isinstance(k,list) and k[0] in ['start','end','mid']]
    if (name.startswith('ESP') and min(ys)<-12.7) or (name.startswith('USB') and max(ys)>2.9):layer[1]='"F.Fab"'
   text=author._dump(tree)+'\n'
  if name.startswith('PinHeader'):text=text.replace('(drill 1)','(drill 1.02)')
  for old in re.findall(r'\$\{KICAD\d+_3DMODEL_DIR\}/([^"\n]+)',text):
   src=SHARE/'3dmodels'/old
   if not src.exists() and (md/src.name).exists():src=md/src.name
   if src.exists():
    
    if src.resolve()!=(md/src.name).resolve():shutil.copyfile(src,md/src.name)
    text=re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}/'+re.escape(old),'${KIPRJMOD}/Local.3dshapes/'+src.name,text)
  (fpdir/(name+'.kicad_mod')).write_text(text)
 # Remove obsolete carrier-only local symbols/footprints; old derived history remains untouched.
 active={p['footprint'].split(':',1)[1] for p in parts if p['footprint']}
 for p in fpdir.glob('*.kicad_mod'):
  if p.stem not in active:p.unlink()
 (D/'Carrier.kicad_sym').unlink(missing_ok=True)
 (D/'sym-lib-table').unlink(missing_ok=True)
 spec['keep_uuids_from']='design/main.kicad_sch';print(author.write(spec,D))
 toolchain.run([toolchain.executable('cli'),'sch','export','netlist','--format','kicadsexpr','-o',str(OUT/'main.sexpr.net'),str(D/'main.kicad_sch')])
 dump(OUT/'schematic-pins.json',verify.schematic_pins((OUT/'main.sexpr.net').read_text())[0])
 (D/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Local")(type "KiCad")(uri "${KIPRJMOD}/Local.pretty")(options "")(descr "KiCad bundled sources, localized models")))\n')
 tree=parse((D/'main.kicad_sch').read_text());uid=value(child(tree,'uuid')[1]);instances={}
 for n in tree:
  if isinstance(n,list) and n and n[0]=='symbol':
   props={value(p[1]):value(p[2]) for p in n if isinstance(p,list) and p[0]=='property'};instances[props['Reference']]=uid+'/'+value(child(n,'uuid')[1])
 dump(OUT/'instances.json',instances)
 pro=json.loads((D/'main.kicad_pro').read_text());base=pro['net_settings']['classes'][0];base.update(name='Default',track_width=.2,clearance=.2,via_diameter=.6,via_drill=.3)
 power=dict(base,name='LOGIC_POWER',track_width=.5);servo=dict(base,name='SERVO_POWER',track_width=1,via_diameter=1,via_drill=.5)
 pro['net_settings']['classes']=[base,power,servo];pro['net_settings']['netclass_patterns']=[{'netclass':'LOGIC_POWER','pattern':n} for n in ['3V3','PB1_5V']]+[{'netclass':'SERVO_POWER','pattern':'SERVO_5V'}]
 dump(D/'main.kicad_pro',pro);probytes=(D/'main.kicad_pro').read_bytes()
 subprocess.run([str(toolchain.executable('python')),'tools/board/integrated_pcb.py'],check=True)
 (D/'main.kicad_pro').write_bytes(probytes)
 outputs=[p for p in D.rglob('*') if p.is_file() and p.suffix not in ['.lck','.kicad_prl']]+[ROOT/'parts.json',ROOT/'product.json']
 dump(stamp,{'key':key,'outputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in outputs}})
if __name__=='__main__':generate()

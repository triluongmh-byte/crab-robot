#!/usr/bin/env python3
"""Contract-to-config/wiring check, and dummy-board sanity when output exists."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
contract=ROOT/'PILOT_CONTRACT.json'
assert hashlib.sha256(contract.read_bytes()).hexdigest()=='65b9793b07d82edc0defd9900ba1cfbee13dc730266cc0b675d897c87a75d9ea'
s=(ROOT/'firmware/crab/Config.h').read_text()
for macro,value in {'SDA':18,'SCL':17,'LED_PIN':21,'BOOT_PIN':0,'POWER_ON':15,'LCD_BL':38,'LCD_CS':6,'LCD_DC':7,'LCD_RST':5,'LCD_WR':8,'LCD_RD':9,'LCD_D0':39,'LCD_D1':40,'LCD_D2':41,'LCD_D3':42,'LCD_D4':45,'LCD_D5':46,'LCD_D6':47,'LCD_D7':48}.items():
 assert re.search(r'^#define CRAB_'+macro+r' '+str(value)+r'$',s,re.M),macro
w=(ROOT/'firmware/WIRING.md').read_text()
for token in ['GPIO18','GPIO17','GPIO21','VCC','V+','GND','CH0','CH7','BOARD GIẢ'] :assert token in w,token
pcb=ROOT/'design/main.kicad_pcb'
if pcb.exists():
 text=pcb.read_text();assert 'LILYGO' not in text and 'PCA9685' not in text,'Dummy PCB must not redefine robot wiring'
 print('PASS available dummy PCB inspected; no robot signals on it')
else:print('INFO board output not present in this role snapshot; integration must inspect the dummy PCB')
signs=[int(v) for v in re.search(r'signs\[8\]=\{([^}]+)\}',s).group(1).split(',')]
integration=json.loads((ROOT/'firmware/integration.json').read_text())
assert integration['directionSigns']==signs,'integration direction signs differ from firmware'
assert signs[::2]==[1]*4,'Hip CCW signs must stay unchanged'
mechanical=ROOT/'case/reports/mechanical.json'
if mechanical.exists():
 case=json.loads(mechanical.read_text())
 for leg,knee in zip(['FL','FR','RL','RR'],[1,3,5,7]):
  movement=case['servoSigns']['kneeLargerPulse'][leg]
  assert movement in ['foot UP','foot DOWN'],(leg,movement)
  pulseUp=1 if movement=='foot UP' else -1
  assert signs[knee]*pulseUp==1,f'{leg} swing pushes foot DOWN instead of lifting'
 print('PASS positive gait knee lift agrees with actual case pulse directions on all four legs')
else:print('INFO case sign report absent; integration must reconcile knee lift directions')
print('PASS contract hash, all GPIO definitions, wiring guide tokens')

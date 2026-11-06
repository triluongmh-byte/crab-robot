#!/usr/bin/env python3
"""Round-trip decode the actual C QR encoder using the independent ZXing decoder."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/firmware/host'
cache=Path(os.environ.get('CIRCUIT_FIRMWARE_CACHE',str(Path.home()/'.cache/autonomous-circuit/firmware')))
sys.path.insert(0,str(cache/'python-deps'))
import zxingcpp
from PIL import Image
for name,payload in [('wifi','WIFI:T:nopass;S:CuaRobot-A01F;;'),('web','http://192.168.1.42/'),('web-long','http://255.255.255.255/')]:
 target=OUT/(name+'.pbm');subprocess.run([str(OUT/'qr'),payload,str(target)],check=True)
 image=Image.open(target).convert('L');result=zxingcpp.read_barcode(image)
 assert result and result.text==payload,(payload,result)
 assert image.size==(148,148)
 print('PASS QR round trip:',payload,'148x148 px / 4-module quiet border')

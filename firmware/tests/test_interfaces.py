"""Firmware deliverable/recipe integrity. Final board audit: reconcile.py (separate).
The compiled target tests check the actual C++ constants for both configurations.
"""
import hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'PILOT_CONTRACT.json')=='7841b7b2e92a0d3f69db70868c7a9649da0c6cd1cfc6d94478ec13886894c1be'
c=(root/'firmware/crab/config.h').read_text()
signs=list(map(int,re.search(r'SIGN\[8\]=\{([^}]+)\}',c).group(1).split(',')))
integration=json.loads((root/'firmware/INTEGRATION.json').read_text())
assert signs==integration['pca9685']['servoDirectionSigns']
assert integration['releaseNoteSha256']=='122b5b3d406fc1cc148b6bf5abaf6c6fc7315e933a95e5565c1b60ee86d35e08'
assert integration['targets']['lilygo']['pins']['LCD_POWER']==15
assert integration['targets']['integrated']['pins']['PCA_OE']==21
assert 'LCD_POWER' not in integration['targets']['integrated']['pins']
if integration['integratedInterface']['status']!='reconciled':
 assert not integration['integratedInterface']['readyForFlashing']
 assert not integration['integratedInterface']['confirmedAgainstFinalNetlist']
assert 'carrierInterface' not in integration # obsolete note3 pass is historical only
ui=(root/'firmware/assets/ui.html').read_text();embedded=(root/'firmware/crab/web_ui.h').read_text();assert ui in embedded
assert sorted(map(int,re.findall(r'data-dir="(\d)"',ui)))==[1,2,3,4]
points=set(json.loads((root/'firmware/assets/font-manifest.json').read_text())['codepoints'])
core=(root/'firmware/crab/core.h').read_text()
phrases=re.findall(r'constexpr const char\* \w+="([^"]+)"',core)+['Giữ BOOT 8 giây','để xóa Wi-Fi']
assert len(phrases)>=8
for phrase in phrases:assert all(ord(c) in points for c in phrase),phrase
for asset in ['wiring.svg','integrated-wiring.svg']:ET.parse(root/'firmware/assets'/asset)
ino=(root/'firmware/crab/crab.ino').read_text();assert 'Serial.print' not in ino
net=(root/'firmware/crab/network_http.h').read_text()
assert 'putString("ssid"' in net and 'if(network.saveRequested)' in net
assert 'serviceNetwork(now)' in ino and '#include "network_http.h"' in ino
assert 'stopMotion' not in net.split('void serviceNetwork',1)[1]
setup=ino.split('void setup(){',1)[1]
assert setup.index('servos.inhibit()')<setup.index('screen.begin()')<setup.index('servos.begin()')
for doc in ['firmware/README.md','firmware/WIRING.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(root/doc).read_text()):
  if '://' in target or target.startswith('#'):continue
  resolved=((root/doc).parent/target.split('#')[0]).resolve()
  # This suite writes its own result only after all groups pass. Verify source
  # links here; tools/verify_release.py checks that final generated report.
  if resolved==(root/'firmware/TEST-RESULTS.json').resolve():continue
  assert resolved.exists(),target+' link missing'
# Binary/source/config integrity, no recompilation or hardware access.
for target,recipe_name,manifest_name,output in [
 ('lilygo','flash.json','BUILD.json','esp32'),
 ('integrated','flash-integrated.json','BUILD-integrated.json','integrated')]:
 recipe=json.loads((root/'firmware'/recipe_name).read_text())
 assert 'esp32s3:' in recipe['fqbn'] and 'PSRAM=opi' in recipe['fqbn'] and 'FlashSize=16M' in recipe['fqbn']
 flags=' '.join(recipe['compileArgs'])
 assert ('CRAB_INTEGRATED_BOARD=1' in flags)==(target=='integrated')
 build=json.loads((root/'firmware'/manifest_name).read_text())
 assert build['target']==target and build['fqbn']==recipe['fqbn'] and build['compileArgs']==recipe['compileArgs']
 expected={str(p.relative_to(root)) for p in (root/'firmware/crab').glob('*') if p.is_file()}|{'firmware/'+recipe_name}
 assert set(build['sourceInputs'])==expected, 'manifest must bind every current source'
 for name,h in build['sourceInputs'].items():assert sha(root/name)==h,name+' differs from built source'
 for name,record in build['artifacts'].items():
  artifact=root/'build/firmware'/output/name
  assert artifact.stat().st_size==record['bytes'] and sha(artifact)==record['sha256'],name
lily=json.loads((root/'firmware/BUILD.json').read_text())
board=json.loads((root/'firmware/BUILD-integrated.json').read_text())
assert lily['artifacts']['crab.ino.bin']['sha256']!=board['artifacts']['crab.ino.bin']['sha256'],'target binary selection was lost'
# Current release authority must describe exactly the delivered binaries.
candidate=json.loads((root/'firmware/FLASH-CANDIDATE.json').read_text())
assert candidate['releaseChainTip']=='4cadb190eb0b3a92a9e7805c9956f41af7b085d71a2e18de54edbae19829277c'
assert {15,16,17,18}.issubset(candidate['implementedNotes'])
evidence=json.loads((root/'firmware/OWNER-EVIDENCE.json').read_text())
assert evidence['releaseChainTip']==candidate['releaseChainTip']
assert evidence['installedChannels']==list(range(8)) and evidence['individuallyReportedOK']==list(range(8))
assert evidence['basis']=='owner report only' and not evidence['hardwareTested']
assert evidence['ownerReportedManual90PoseSet'] and evidence['runtimeConfirmationRequired']
assert not evidence['runtimeReferenceConfirmed'] and not evidence['calibrationSeeded'] and not evidence['isolationConfirmed']
assert evidence['releaseNote']==18 and evidence['servoPlugsCurrentlyConnected']
reports={r['releaseNote']:r for r in evidence['ownerReports']}
assert reports[17]['exactOwnerMessage']=='ok fen, thêm nữa là tao đã gắn tất cả servors và test từng cái oke rồi đó.'
assert reports[18]['exactOwnerMessage']=='đã nắn hết khớp về như tao nói. Mạnh mẽ code nạp rồi push nhe'
assert reports[18]['releaseNoteSha256']==candidate['releaseChainTip']
assert reports[18]['observation']=='manual 90° pose set on all joints (owner report)'
assert candidate['ownerEvidenceSha256']==sha(root/'firmware/OWNER-EVIDENCE.json')
assert integration['ownerEvidence']=='firmware/OWNER-EVIDENCE.json'
assert integration['ownerEvidenceReleaseNoteSha256']==candidate['releaseChainTip']
for target in ['lilygo','integrated']:
 record=candidate['binaries'][target]
 manifest=root/record['manifest']
 assert sha(manifest)==record['manifestSha256']
 assert json.loads(manifest.read_text())['releaseChainTip']==candidate['releaseChainTip']
 assert json.loads(manifest.read_text())['ownerEvidence']=='firmware/OWNER-EVIDENCE.json'
 assert 18 in json.loads(manifest.read_text())['implementedFirmwareNotes']
 assert sha(root/record['path'])==record['sha256']
 assert record['flashCandidate']==(target=='lilygo')
print('PASS: sealed contract, note4 target metadata, embedded UI/glyphs/SVG/guide links, earliest OE inhibit, separate recipes and two complete binary/source manifests; final board reconciliation remains separate')

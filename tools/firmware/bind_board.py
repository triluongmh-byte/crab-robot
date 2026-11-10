#!/usr/bin/env python3
"""Bind fresh exports to the reviewed interface without changing its map.

KiCad's XML contains export time/path metadata. Only that artifact hash is
refreshed, after exact native PCB identity and full pad/net parity checks.
The geometry handoff also contains a STEP-file digest with export metadata.
Its entire semantic payload remains locked; only that digest is rebound.
The normal firmware reconciler still verifies every reviewed signal/evidence.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from kicadpy.verify import pcb_pads

ROOT = Path(__file__).resolve().parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = ROOT / 'firmware/reviewed-board-interface.json'
    data = json.loads(source.read_text())
    pcb = ROOT / 'design/main.kicad_pcb'
    xml = ROOT / 'build/board/main.net'
    if sha(pcb) != data['boardInputSha256']['design/main.kicad_pcb']:
        raise SystemExit('Native PCB changed since interface review; request a new firmware/board review')
    pads, _ = pcb_pads(pcb.read_text())
    nodes = {n.attrib['ref']+'.'+n.attrib['pin']:net.attrib['name']
             for net in ET.parse(xml).getroot().findall('./nets/net') for n in net.findall('node')}
    if pads != nodes:
        raise SystemExit('Fresh XML does not match the reviewed native PCB pad/net map')
    handoff_path = ROOT/'engineering/board-interface.json'
    handoff = json.loads(handoff_path.read_text())
    semantics = json.loads(handoff_path.read_text())
    semantics['pcb'].pop('stepSha256')
    digest = hashlib.sha256(json.dumps(semantics, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if digest != data['boardGeometrySemanticsSha256']:
        raise SystemExit('Board geometry/interface semantics changed since review')
    if handoff['sourcePCBsha256'] != sha(pcb):
        raise SystemExit('Geometry handoff does not describe the reviewed native PCB')
    step = ROOT/handoff['pcb']['step']
    if handoff['pcb']['stepSha256'] != sha(step):
        raise SystemExit('Fresh STEP does not match the current geometry handoff')
    data['evidenceSha256']['engineering/board-interface.json'] = sha(handoff_path)
    data['boardInputSha256']['build/board/main.net'] = sha(xml)
    data['usbPortUpdate']['boardStepSha256'] = sha(step)
    target = ROOT / 'firmware/board-interface.json'
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print('Bound fresh XML/STEP metadata; reviewed PCB, pad/net map and geometry semantics preserved')

if __name__ == '__main__':
    main()

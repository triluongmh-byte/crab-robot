#!/usr/bin/env python3
"""Bind a fresh XML export to the reviewed interface without changing its map.

KiCad's XML contains export time/path metadata. Only that artifact hash is
refreshed, after exact native PCB identity and full pad/net parity checks.
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
    data['boardInputSha256']['build/board/main.net'] = sha(xml)
    target = ROOT / 'firmware/board-interface.json'
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print('Bound fresh XML hash; reviewed PCB, connection map and evidence hashes preserved')

if __name__ == '__main__':
    main()

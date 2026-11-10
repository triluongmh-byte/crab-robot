#!/usr/bin/env python3
"""KiCad runtime: note9 scoped J1 relocation, on a candidate; keep unrelated copper.

Run prepare, then host pinned Freerouting, then import. Never reroute the board.
"""
import json, pathlib, shutil, sys
import pcbnew as p

R = pathlib.Path(__file__).resolve().parents[2]
C = R / 'build/board/usb-relocation'
C.mkdir(parents=True, exist_ok=True)
mm = p.FromMM
v = lambda x, y: p.VECTOR2I(mm(x), mm(y))
changed = {'USB_DM', 'USB_DP', 'USB_CC1', 'USB_CC2'}

if sys.argv[1] == 'prepare':
    assessment = json.loads((R/'case/reports/assembly-access.json').read_text())
    lo, hi = assessment['usbCableAssessment']['boardRelocationCandidate']['plugCentreXRangeMm']
    assert lo <= 21.45 <= hi and assessment['usbCableAssessment']['boardRelocationCandidate']['passAll']
    for ext in ['kicad_pro', 'kicad_sch', 'kicad_pcb']:
        shutil.copyfile(R/f'design/main.{ext}', C/f'main.{ext}')
    b = p.LoadBoard(str(C/'main.kicad_pcb'))
    j = b.FindFootprintByReference('J1')
    j.SetPosition(v(21.45, -28))
    j.SetOrientationDegrees(180)
    # Remove the old USB/CC runs and only the PB1 connector-to-regulator feeder.
    removed = []
    for t in list(b.GetTracks()):
        a, z = t.GetStart(), t.GetEnd()
        ax, ay, zx, zy = map(p.ToMM, [a.x, a.y, z.x, z.y])
        if t.GetNetname() in changed:
            removed.append(t)
        elif t.GetNetname() == 'PB1_5V' and (
            isinstance(t, p.PCB_VIA) or min(ay, zy) < 10 or min(ax, zx) < -35.01
        ):
            removed.append(t)
        elif t.GetNetname() == 'GND' and max(ax, zx) < -36 and min(ay, zy) > -10 and max(ay, zy) < 10:
            # Connector shell fanout only; retained bottom plane joins remaining GND.
            removed.append(t)
    for t in removed:
        b.Remove(t)
    for t in b.GetDrawings():
        if isinstance(t, p.PCB_TEXT):
            if t.GetText() == 'CRAB INTEGRATED V0':
                t.SetPosition(v(0, -28))
            elif t.GetText() == 'USB / PB1 5V':
                t.SetPosition(v(30, -28)); t.SetTextAngle(p.EDA_ANGLE(90, p.DEGREES_T))
            elif t.GetText() == 'J10 LCD SPI 3V3':
                t.SetPosition(v(5, -24))
    # Native accepted candidate retains all planes. Router copy omits pours and locks
    # every pre-existing segment. Import will copy only newly routed scoped nets.
    p.SaveBoard(str(C/'placed.kicad_pcb'), b)
    for t in b.GetTracks():
        t.SetLocked(True)
    for z in list(b.Zones()):
        if not z.GetIsRuleArea():
            b.Remove(z)
    p.SaveBoard(str(C/'main.kicad_pcb'), b)
    assert p.ExportSpecctraDSN(b, str(C/'main.dsn'))
    print('Placed candidate: J1 (21.45,+28) board-local, mouth +Y at +32.8; removed', len(removed), 'scoped old segments')
elif sys.argv[1] == 'import':
    routed = p.LoadBoard(str(C/'main.kicad_pcb'))
    assert p.ImportSpecctraSES(routed, str(C/'main.ses'))
    p.SaveBoard(str(C/'routed.kicad_pcb'), routed)
    b = p.LoadBoard(str(C/'placed.kicad_pcb'))
    def signature(t):
        a, z = t.GetStart(), t.GetEnd()
        ends = tuple(sorted([(a.x, a.y), (z.x, z.y)]))
        return (t.GetNetname(), type(t).__name__, int(t.GetLayer()), ends, t.GetWidth())
    original = {signature(t) for t in b.GetTracks()}
    count = 0
    for t in routed.GetTracks():
        if signature(t) in original:
            continue
        if t.GetNetname() in changed | {'PB1_5V'}:
            c = t.Duplicate()
            c.SetNet(b.FindNet(t.GetNetname())); c.SetLocked(False)
            if not isinstance(c, p.PCB_VIA):
                c.SetWidth(max(c.GetWidth(), mm(.6 if c.GetNetname() == 'PB1_5V' else .2)))
            b.Add(c); count += 1
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    p.SaveBoard(str(C/'candidate.kicad_pcb'), b)
    print('Merged', count, 'scoped segments; unchanged copper preserved')
else:
    raise SystemExit('prepare | import')

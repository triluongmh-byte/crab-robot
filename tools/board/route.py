"""KiCad Python: DSN export or import of the first-pass candidate only."""
from pathlib import Path
import sys
import wx
app=wx.App(False)
import pcbnew as k
root=Path(__file__).resolve().parents[2];cand=root/'build/board/candidate';cand.mkdir(exist_ok=True)
if sys.argv[1]=='export':
 b=k.LoadBoard(str(root/'design/main.kicad_pcb'))
 k.SaveBoard(str(cand/'main.kicad_pcb'),b)
 assert k.ExportSpecctraDSN(b,str(cand/'main.dsn'))
else:
 b=k.LoadBoard(str(cand/'main.kicad_pcb'))
 assert k.ImportSpecctraSES(b,str(cand/'main.ses'))
 k.SaveBoard(str(cand/'routed.kicad_pcb'),b)
 print('Candidate ready for native check; source untouched.')

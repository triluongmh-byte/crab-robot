"""Local ink-only repair: references use the same 0.15 mm stroke as warning text."""
from pathlib import Path
import wx
app=wx.App(False)
import pcbnew as k
root=Path(__file__).resolve().parents[2];p=root/'design/main.kicad_pcb'
b=k.LoadBoard(str(p))
for f in b.GetFootprints(): f.Reference().SetTextThickness(k.FromMM(.15))
k.SaveBoard(str(p),b)
# Keep reference styling in the native local library consistent with its board instances.
for p in (root/'design/Dummy.pretty').glob('*.kicad_mod'):
 s=p.read_text();p.write_text(s.replace('(thickness 0.13)','(thickness 0.15)'))
p=root/'tools/board/build_pcb.py';p.write_text(p.read_text().replace('TextThickness(mm(.13))','TextThickness(mm(.15))'))

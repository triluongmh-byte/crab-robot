"""Preserve existing tracks and UUIDs; set only the two dummy link widths."""
from pathlib import Path
import wx
app=wx.App(False)
import pcbnew as k
p=Path(__file__).resolve().parents[2]/'design/main.kicad_pcb';b=k.LoadBoard(str(p))
for t in b.GetTracks():
 assert t.GetNetname() in ('DUMMY_A','DUMMY_B')
 t.SetWidth(k.FromMM(.5))
k.SaveBoard(str(p),b)

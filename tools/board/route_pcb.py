"""Specctra round trip on a candidate only, using the KiCad runtime."""
import sys,pathlib
import pcbnew as p
root=pathlib.Path(__file__).resolve().parents[2]
cand=root/'build/board/route'
settings=p.GetSettingsManager()
pro=str(cand/'main.kicad_pro')
settings.LoadProject(pro)
b=p.LoadBoard(str(cand/'main.kicad_pcb'))
b.SetProject(settings.GetProject(pro))
b.SynchronizeNetsAndNetClasses(False)
if sys.argv[1]=='export':
 print('export',p.ExportSpecctraDSN(b,str(cand/'main.dsn')))
else:
 print('import',p.ImportSpecctraSES(b,str(cand/'main.ses')))
 p.SaveBoard(str(cand/'main.kicad_pcb'),b)

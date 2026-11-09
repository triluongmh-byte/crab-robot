#!/usr/bin/env python3
"""Hash-cached native STEP exports, parallel foreground CLI, then measured handoff."""
import concurrent.futures,hashlib,json,os,pathlib,subprocess
from kicadpy import toolchain
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R);O=R/'build/board'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inputs=[R/'design/main.kicad_pcb',pathlib.Path(__file__),R/'tools/board/export_geometry.py']+list((R/'design/Local.3dshapes').glob('*.step'))
 key=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(inputs))).hexdigest();stamp=O/'export.stamp'
 if stamp.exists() and stamp.read_text()==key and all((O/n).exists() for n in ['integrated.step','pcb-only.step']) and (R/'engineering/board-interface.json').exists():print('STEP/handoff inputs unchanged; skipped');return
 def native(board_only):
  name='pcb-only.step' if board_only else 'integrated-raw.step';args=[toolchain.executable('cli'),'pcb','export','step','--force','--subst-models','--include-pads','--user-origin','0x0mm','-o',str(O/name)]
  if board_only:args+=['--board-only']
  args+=['design/main.kicad_pcb'];result=toolchain.run(args,timeout=180)
  if 'Could not add' in result or 'File not found' in result:raise RuntimeError(result)
  print(name,'native export complete')
 with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:list(ex.map(native,[False,True]))
 subprocess.run([os.environ['KICAD_CASE_PYTHON'],'tools/board/export_geometry.py'],check=True)
 stamp.write_text(key)
if __name__=='__main__':main()

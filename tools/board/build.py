#!/usr/bin/env python3
"""Rebuild board deliverables from the checked authored native sources; preserve copper."""
import pathlib,subprocess,sys,os
R=pathlib.Path(__file__).resolve().parents[2];os.chdir(R)
# Native design/main.* are authored inputs, including accepted local copper repairs.
# integrated.py is an explicit placement-draft generator, never the default release build.
for name in ['check.py','export.py','verify_module_orientation.py']:
 subprocess.run([sys.executable,str(R/'tools/board'/name)],check=True)
subprocess.run([sys.executable,'-m','kicadpy.verify','rotation','design/main.kicad_pro','parts.json','engineering/factory-pads.json'],check=True,stdout=open('build/board/rotation.log','w'))
subprocess.run([sys.executable,'tools/board/review.py'],check=True)
subprocess.run([sys.executable,'-m','kicadpy.publish','--manufacturing','design/main.kicad_pro'],check=True)
subprocess.run([sys.executable,'-m','kicadpy.verify','gate','.'],check=True)

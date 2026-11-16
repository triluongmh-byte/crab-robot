#!/usr/bin/env python3
"""Bracket with the two HC-SR04P modules fitted, robot frame, for review only.

The 3MF holds just the printed bracket; the sensors are bought parts. This
writes sonar_bracket_with_sensors.step (bracket orange, PCBs blue, cans grey)
without the robot body, so the sensors are easy to see. The full fit view
with frames and legs is sonar_bracket_fit_preview.step from check_fit.py.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cadquery as cq  # noqa: E402
import sonar_bracket as SB  # noqa: E402

asm = cq.Assembly(name='sonar_bracket_with_sensors')
asm.add(SB.robot_frame(), name='sonar_bracket', color=cq.Color(0.95, 0.55, 0.1))
for n, s in SB.module_dummies_robot():
    asm.add(s, name=n.replace(' ', '_'), color=cq.Color(0.1, 0.35, 0.8) if 'pcb' in n else cq.Color(0.75, 0.75, 0.78))
out = HERE / 'sonar_bracket_with_sensors.step'
asm.save(str(out))
print(out)

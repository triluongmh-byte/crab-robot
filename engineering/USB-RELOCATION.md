# Note 9 USB-C repair — 2026-11-10

Approved design: move the existing J1 to the +Y edge, keeping the 88×62×1.6 mm
outline, four mounting holes, all other connector positions, GPIO map and rails.
Case input is case/reports/assembly-access.json usbCableAssessment: the old
−X opening fails a normal 12.5×7×25 mm plug; all candidate plug centres
X=15.75,21.45,27.15 on +Y passed the preliminary solid-box test.
Board placement has no case rotation/offset per release note 9.

Chosen J1 native KiCad origin (21.45,−28), rotation 180°; board-local origin
(21.45,+28). Mouth faces board-local +Y, front face Y=+32.8 mm (1.8 mm beyond
PCB edge +31). This is the same part, pad map, SMT process and solder joints.
R1/R2 and the MCU's 22 Ω USB series resistors keep their positions. Only the
connector's affected USB/CC/PB1 feeder copper and old local shell fanout change.
Existing unrelated copper is retained. The scoped pinned-router candidate has
all existing segments fixed; only changed nets are imported, retaining planes.

Approach is fixed by the release note: changing to a narrow cable would leave
the assembly defect open; outline/mount changes are unnecessary at this stage.
No purchase-list or solder-joint change is needed because no part/joint changes.

Status: scoped copper accepted after native severity-all DRC/parity returned
zero findings. Final full release checks passed: native ERC/DRC/parity0findings,
publisher sidecar0errors/0warnings, manufacturing0findings, fab.ready=true.
The current packet path is read from boards/main.board.json. This is board
prototype readiness, not whole-team readiness or physical verification. Final board STEP and pad-position
JSON must be regenerated after acceptance; case must rerun ordinary 12.5×7×25 mm
plug checks at all three positions against that final STEP. This document does
not claim case access or physical fit has passed. No hardware has been used.


Measured electrical paths (actual copper, including MCU-side tracks and via
barrels): D+90.532mm; D−91.718mm; skew1.187mm. Estimated FR4 flight time at
6.3ps/mm is0.570/0.578ns; skew about7.5ps. Width0.2mm, minimum native
clearance0.2mm; 22Ω series resistors remain by MCU. USB is full-speed12Mbps,
not high-speed. This is a V0 prototype routing assumption: the 2-layer1.6mm
stackup and independently routed fanouts do NOT establish controlled90Ω or
USB compliance. The short-flight-time estimate is not a physical USB test.
ESP hardware guidance recommends parallel equal-length90Ω±10% routing:
https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
Remaining acceptance: professional first-board USB enumeration, flashing and
serial reliability in both plug orientations with normal cables; if unreliable,
repair the USB pair/stackup before producing more boards. Do not claim a proven
USB product from ERC/DRC alone. No rise-time or eye measurement was made.

PB1 feeder is still0.6mm or wider. Estimated20°C end-to-end resistance for
either duplicated VBUS contact route to U2 input is0.084/0.107Ω, using35µm
copper and a conservative estimated15µm via barrel. At560mA budget the longer
path drops about60mV, about72mV at70°C copper (ρ factor1.20). This retains
at least4.75−0.072−3.3−0.7=0.678V dropout reserve. The two input branches in
parallel reduce actual drop; calculation deliberately uses one branch only.
Ground planes are refilled and all shell/ground pins connect. No supply net,
input capacitance, component, manual joint or other connector changes.

Regeneration: tools/board/build.py uses native files as inputs; the new scoped
construction scripts are historical repair helpers. check_usb_move.py compares
all fixed footprints and410 retained copper items to SHA-bound pre-move
measurements in usb-relocation-baseline.json and regenerates the path audit.
No build/ binary or previous board is needed for the release audit.

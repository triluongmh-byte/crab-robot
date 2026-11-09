# Integrated V0 case handoff — final authored geometry

PCB: actual native export build/board/integrated.step. Native KiCad frame is
x right, y down, top copper z0; exported STEP x right,y UP. Board outline
88×62mm, thickness1.6mm, centred0,0. Do not reuse the old56×44carrier geometry.
Mounts are actual source positions, final JSON will reconcile STEP/native.
H1(-40,-13), H2(39,-26), H3(-39,26), H4(39,26) in KiCad coordinates; Ø3.2.

Screen: engineering/sources/integrated/waveshare-display.step is the official
Waveshare23822 1.9in 170×320ST7789V2 module, not a raw panel or LILYGO. Its
supplier coordinate bounds measured51.2173×27.3173×7mm; visible glass/display
area42.72×22.70mm. Actual STEP is source for window, connector and retention;
orient it as needed for QR and retain in the skeleton. Eight-wire supplied
GH1.25-to-female harness connects labelled J10; no rigid screen-on-PCB socket.
The screen is not yet positioned in robot frame; case sets that placement.

PCB top: antenna along top(-Y KiCad/+Y STEP) edge centredx=-23; keep nearby
conductors, motor wiring, screws and power bank away from antenna. Native
footprint contains manufacturer's keepout. USB-C J1 at(-41,0), opening toward
-X. BOOTSW1(-6,3),RESETSW2(-6,10), reachable from top. PCA at(10,0).
ServoJ2..9 x=-16,-9,-2,5,12,19,26,33; top pinGND atKiCad y17, then5V at19.54,
PWM at22.08. Allow plugged SG90 leads and bend radius/slack. J11LED at(22,27)
point1DIN then+5V,GND along+X. J12 screw terminal(36,3), rotated90°, wire entry
+X, pluspin1 andGNDpin2; top screwdriver access required. USB and servo5V
positive rails remain separate; commonGND now on PCB, no Dupont GND link.

Tallest component is screw terminal (13.845mm above top copper; exact STEP wins),
C11 bulk cap about10.2mm, headers post8.5mm. Do not put ribs in plugged-wire
space. engineering/board-interface.json binds actual PCB and STEP hashes, every connector
pad and the full populated envelope. Board tails extend3.455mm below top
copper, including1.6mm board thickness; reserve wire/lead space accordingly.
Raw native STEP is normalized using actual top copper; no frame guess.
No current body fit, physical fit, print or printed-part status is claimed.

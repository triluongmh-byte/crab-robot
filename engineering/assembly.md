# Assembly — integrated V0

Factory assembles all29 SMT references: U1ESP32-S3-WROOM-1-N16R8,
U2TI TLV1117LV33DCYR,U3NXP PCA9685PW,118,J1USB-C,R1..R12,C1..C11,
SW1/SW2. There are15 unique stocked SMT codes. Only11 THT connectors are
manual in the packet; ask the assembler to fit them too if their quote allows.
The user should request a fully assembled board from a soldering service,
not attempt the ESP exposed pad,0.5mm USB pins or TSSOP by hand.

Every potential remaining joint (37 total), one physical pin=one joint:
- J2.1,J2.2,J2.3 =CH0 brownGND/red5V/orangePWM.
- J3.1,J3.2,J3.3 =CH1 same order.
- J4.1,J4.2,J4.3 =CH2 same order.
- J5.1,J5.2,J5.3 =CH3 same order.
- J6.1,J6.2,J6.3 =CH4 same order.
- J7.1,J7.2,J7.3 =CH5 same order.
- J8.1,J8.2,J8.3 =CH6 same order.
- J9.1,J9.2,J9.3 =CH7 same order.
- J10.1BL,.2RES,.3DC,.4CS,.5SCK,.6MOSI,.7GND,.8VCC3V3.
- J11.1LED-DIN,.2LED5V,.3LEDGND.
- J12.1SERVO+5V,.2GND screw terminal.
Four M3 NPTH holes and four bare testpoint pads require no soldered part.
Supplied Waveshare lead plugs in. If owned LED bar has three bare solder pads
rather than a fitted lead, a service must also solder barDIN,5V,GND: three
conditional external joints, not hidden in the37 PCB joints. No solder to
power-bank USB ports, servo leads, LILYGO or external PCA is needed.

Native-vs-factory orientation measurement is build/board/rotation.log.
TI SOT223 offset180°; every other SMT part offset0° (measured, not guessed).
Known passives/USB/switch offsets were checked against kicadpy.knowledge;
new ESP/PCA/TI/22Ω identities and factory pads were fetched independently.
C11 local lands were corrected to actual factory centres±4.5mm,4.5×1.65mm;
measured mean pad-position error0.0001mm. C11 positive pin1 is left in native
footprint; package polarity stripe is negative pin2. U1 pins1/40/EP41GND;
factory nine sub-pads all numbered41 are ground subdivisions, no extra GPIOs.
U3 pin1A0 orientation is checked against NXP TSSOP top view. USB mirrored
A/B numbering is checked through actual pad nets, never inferred by drawing.

ESP local land pattern has a solid3.9mm EP with windowed paste and no open
via-in-pad holes; external thermal/ground vias use0.3mm drills. C11 pads extend
beyond body, courtyard enlarged accordingly. USB locating pegs/oval shield
holes are preserved; no drill, pad, paste, mask or clearance was relaxed.
All components on top. Assembly drawings/CPL and per-ref MPN are in the
publisher packet. Before payment, assembler must confirm sourced part identity,
stock and placement preview; no ordering, upload or payment took place.

The raw unmodified `kicadpy.verify rotation` flags U1 POOR MATCH (0.591mm):
it centres all49 supplier physical lands against41 native logical pads, so
nine small GND lands bias the centroid relative to one solid GND pad41.
`tools/board/verify_module_orientation.py` compares every numbered pad1..41,
using only the centroid of the nine supplier pad41 lands for the EP centre.
It tests0/90/180/270deg and fits translation, with no input mutation. Offset0
has max0.021879mm /mean0.011740mm error across all41 logical pads; other
rotations exceed19mm maximum error. ESP datasheet land/pin drawing agrees.
The raw warning remains in rotation.log; build/board/module-orientation.json
binds this resolution to actual PCB and untouched factory-input hashes.
This resolves orientation only, never a substitute for native/fab checks.

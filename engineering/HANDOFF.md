# Board handoff — note9 USB repair complete, 2026-11-10
- Contract SHA256:7841b7b2e92a0d3f69db70868c7a9649da0c6cd1cfc6d94478ec13886894c1be.
- Effective note9 tip034b50d8…; frozen contract/notes unchanged; board scope only.
- design/main.kicad_sch/.pcb/.pro: real connected native circuit, accepted copper/rules.
- design/spec.json/Integrated.kicad_sym: authored net table and flattened library.
- design/Local.pretty/.3dshapes + tables: actual local packages/models; provenance in sources.md.
- product.json:88×62×1.6mm,2layers1oz; separatePB1_5V/SERVO_5V,commonGND.
- parts.json:40populated refs,29factorySMT/11manualTHT; unchanged by note9.
- manufacturing.json: source/evidence hashes,7reviews and measured assembly rotations.
- engineering/power,protection,pinout,thermal,assembly,fabricator,bringup.md:
  calculations, primary pin tables/reset states,37named PCB joints and physical checks.
- MUA-THEM-PCB.md: Vietnamese buy/service list unchanged; PCA bought, receipt unconfirmed.
- DEVIATIONS.md: documented SPI display fallback,GPIO21/OE and USB prototype limit.
- sources.md + sources/integrated/: primary documents/vendorSTEP; factory-pads.json is input.
- 3D-MODELS.md: USB/switch are conservative envelopes, not detailed socket solids.
- USB-RELOCATION.md: approved repair scope, DC/path evidence, USB/case limits.
- usb-relocation-baseline.json: pre-move geometry/copper hashes, immutable audit input.
- usb-relocation-audit.json: generated source-bound path/DC/preservation measurements.
- J1 native(21.45,-28),rotation180°; board-local(21.45,+28),mouth+Y atY32.8.
- Case approved centreX15.75..27.15; selected21.45. Other footprints/nets unchanged.
- board-interface.json/case-interface.md: measured final pins,frames,mounts,STEP hash.
- Final STEP build/board/integrated.step; native source hash5992e36582a47ea3…
- Populated bounds[-44,-31,-3.455]..[44,32.8,13.845]mm; nakedPCB88×62.
- H1(-40,13),H2(39,26),H3(-39,-26),H4(39,-26),board-localYup,Ø3.2 unchanged.
- Case must import final STEP and test ordinary12.5×7×25mm plug atall3positions.
- Keep do-not-buy-cable warning until case recheck; no narrow-cable substitution.
- firmware-interface.md: native GPIO19/20USB unchanged; no source/binary rebuild.
- I2C18SDA/17SCL;1LED;0BOOT;21/OE high/reset thenFULL_OFF before enable low.
- SPI8SCLK/39MOSI;5RES/6CS/7DC/38BL;15NC;9,40–42,45–48NC; LCD stays180°.
- PCA0x40 CH0..7hipFL,kneeFL,hipFR,kneeFR,hipRL,kneeRL,hipRR,kneeRR.
- tools/board/build.py L1–12: release FROM native sources; preserves copper.
  Full check: "$KICAD_HARNESS_PYTHON" tools/board/build.py
- check.py L11–55: independent pin/rail/outline+XML parity; cached/allCPU.
  Fast audit: "$KICAD_HARNESS_PYTHON" tools/board/check.py
- check_usb_move.py L7–56: fixed-footprint/410retained-copper hashes and Dijkstra DC/USB paths.
  Fast repair audit: "$KICAD_HARNESS_PYTHON" tools/board/check_usb_move.py
- native.py L6–26: focused cachedERC/DRC; append erc or drc for a local repair.
- export.py L8–20/export_geometry.py L10–25: cached nativeSTEP then measuredJSON.
  Export: "$KICAD_HARNESS_PYTHON" tools/board/export.py
- review.py L7–41: binds current native ignored categories/evidence/assembly hashes.
- verify_module_orientation.py L6–36: all41logical pads resolves raw U1rotationwarning.
- relocate_usb.py prepare/import; usb_obstacles.py,usb_paths.py,finish_usb.py:
  historical scoped candidate helpers in build/board/usb-relocation; NOT release inputs.
- integrated*.py/route*.py/repair*.py: historical placement/construction; never rerun on release.
- Publisher owns boards/main.board.json and current preview/reports/fab packet.
- Full suite passed; gate:fab.ready=true,sidecar0errors/0warnings,native0,manufacturing0.
  Evidence:build/board/note9-release.log; final gate command:kicadpy.verify gate .
- USB paths90.532/91.718mm,skew1.187mm; max estimatedPB1drop60mV@560mA20°C.
- USB90Ω/compliance not established; first-board both-orientation enumeration/flash required.
- Other physical assumptions: bank surge,LED3.3VDIN,displayrevision,thermal,QR,solder quality.
- hardwareTested=false; no whole-team/body-fit/print/firmware/motion readiness claim.
- No user blocker. No commit/push/order/upload/print/flash/hardware operation performed.

# Source build validation — 2026-11-10

**Full empty-clone build passed, exit 0**, for source commit `20816fd07cb060d4e8dfa51b26529e8a7771d999`. `./build.sh` recreated the deliverables from committed source in a new empty temporary clone; tracked source remained unchanged. The following commit updates documentation/reference images only, including the owner's LILYGO wiring clarification and PCA arrival. It changes no runtime firmware, PCB, CAD or build implementation. The host suite was rerun after the guide/image update; guide links and both QR decodes passed, with unchanged compiled groups reused.

| Check | Result |
|---|---|
| Native ERC/DRC, parity and manufacturing gate | PASS; zero findings, errors and warnings |
| Populated native PCB STEP and manufacturing exports | Regenerated from the authored side-entry USB PCB |
| Frozen r1 geometry | Twelve historical parts and baseline base source-recreated with exact hashes; two clamp bars parked under retired references |
| Current production set | Ten prints: two new open frames, eight reusable leg parts; no clamp bars |
| Mechanical/native case and actual insertion/tool access | PASS against the final published PCB; no virtual board accepted |
| Complete lead-motion and USB routes | PASS; eight servo leads, two routes each; full 252-pose sampling and four knee service loops |
| Ordinary USB-C access | PASS for 12.5 × 7 × 25 mm head, Ø4.5 mm cable; head projects about 20 mm beyond +Y body side |
| Offline Bambu slicing and plate checks | PASS; two named plates, 5.29 h / 106.15 g total |
| Both firmware targets | Compile PASS; separate complete LILYGO/integrated image sets |
| Firmware host suite | All six groups PASS, including independent Apple Vision QR decoding at LCD scale |
| Native-board firmware reconciliation | Reconciled; no findings |
| Strict complete-packet and freshness checks | PASS; no stale native inputs |

Plate 1 contains `frame_lower` and `frame_upper`: 3.70 h, 67.37 g. Plate 2 contains the eight leg pieces already reported printed: 1.59 h, 38.78 g. Estimates are offline slicer predictions, not measured printing times. The saved owner profile is preserved; Bambu also emits its bed-temperature/profile and unsupported traditional-timelapse annotations. No printer is contacted or operated.

Fresh XML and STEP export hashes are rebound only after the exact reviewed PCB/pad-net map and complete geometry-handoff semantics match. Negative checks also rejected a changed connector position and a false STEP digest. Static manufacturer and orientation evidence remains locked.

## Outputs and reproduction

Run the repository-root `./build.sh` with macOS, KiCad 10.0.5, CadQuery 2.7.0/OCP 7.8.1.1, Bambu Studio CLI, Arduino CLI 1.5.1/ESP32 core 2.0.14, clang, Node, Pillow and Swift/Apple Vision. Set `KICAD_HARNESS_PYTHON` and `KICAD_CASE_PYTHON` to the supplied interpreters. The build fetches hash-pinned manufacturer inputs into an ignored cache and installs no software.

Generated outputs include the native manufacturing packet under `boards/`, `build/board/integrated.step`, case STEP/STL under `case/robot/` and board-frame copies under `case/out/`, scoped reports, `case/print/production.3mf`, separate `test-only.3mf`, `test-saddle.3mf` and `mating-test.3mf`, `case/overview.html`, and both firmware image sets under `build/firmware/`. These outputs, vendor PDFs and raw reports are deliberately excluded from Git.

The current overview CAD and exported views were inspected. Live interaction with the embedded Harness viewer could not be completed because CUA coordinate input returned `noWindowsAvailable`; that live interaction check is not claimed.

## What remains physical

The integrated PCB has not been manufactured, powered or flashed. The two new frames are unprinted. Actual plug passage, tolerances, retention/strength, wire flexibility, temperature, radio range, bank shutoff/surges, LED data level and walking remain first-prototype checks in the [assembly checklist](case/CHECKLIST-RAP.md). Ask the assembler to check soldering/mounting insulation, regulator temperature and USB enumeration/flashing in both plug orientations. USB impedance is not controlled or certified; the module ground stitching and thermal behaviour still need the first-board test.

Watch the nominal clearances on the first print: hip body to bar 0.65 mm, USB head underside to rail 0.65 mm, USB cable to fixed frame 0.35 mm, and foot to frame 0.23 mm at the extreme ±30-degree sweep. Keep the cable projection free. These measurements are CAD evidence, not physical-fit claims.

The owner's old LILYGO QR result, existing orange-body assembly and report of both module LEDs lighting do not validate the new controller/frame. See [owner evidence](references/OWNER-PRINTS.md), [the original-module wiring guide](firmware/WIRING.md#original-lilygo-and-bought-pca9685) and [what to buy after ordering](docs/AFTER-ORDER.md). No new hardware flash, motor movement, print job, order or payment was performed.

# Source build validation — 2026-11-10

**Full empty-clone build passed, exit 0**, for source commit `b0b893cc74817dd86ca38eef1212a54a7e610c45`. A new empty temporary clone ran the complete `./build.sh`; tracked source remained unchanged. This includes the accepted direct-AP fix, default unknown/continuous with all sixteen PCA outputs off, explicit positional selection, and the manually opened one-servo neutral/speed experiment. Both hardware targets compile. Tests exercise actual HTTP handlers and PCA register output, single-channel/count bounds, the 2000 ms cap, 500 ms lease, release/session/inhibit/fault behavior and retained positional startup. They are host tests, not physical motor observations.

The preceding AP implementation `766b942e2ef2e7c7274b86ea3052b3c3aa781c32` and mechanical implementation `20816fd07cb060d4e8dfa51b26529e8a7771d999` also passed separate full empty-clone builds. PCB, frame, plates, wiring and GPIO assignments remain unchanged by these firmware updates; this latest run regenerated and checked them again for source publication. The next documentation-only commit records this result. Generated binary hashes are tied to each build's manifest; byte-identical binaries across different build paths are not claimed.

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
| Firmware host suite | All seven groups PASS, including real HTTP handlers for both targets and independent Apple Vision QR decoding at LCD scale |
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

## Current owned-hardware limitation

Default-off startup and the bounded single-servo experiment are implemented and host-checked. They do not supply missing angle feedback: the owner's continuous SG90s cannot hold joint angle or execute the positional walking gait. Positional startup/gait/centring require an explicit compatible-positional setting, and reset returns to unknown/off.

There is no established servo supply in the photographed inventory; no exposed-cell/module wiring or purchase is introduced. Prior reverse polarity leaves component health uncertain. Actual supply, neutral stability, emitted frequency, stop response and walking remain untested. The [test guide](firmware/SERVO-TEST.md) records timing, I²C/OE and client-stall limits; software full-off is not a supply disconnect or guaranteed brake.

The owner renewed original-LILYGO flash authorization. Physical motor isolation confirmation and a new full-flash readback/verify with recovery command remain prerequisites; no device write or motor operation is claimed by this source-build result.

## Continuous 360° manual-reference update — fresh source build pending

The new runtime has independent firmware and integration approval in native r018 for the manual-reference/calibration/budget work. It was imported byte-for-byte into this source repository, retaining the portable build adapters. Focused public core, driver, HTTP and web checks passed for both profiles, including independent QR decoding. Final owner-evidence/release metadata and a complete new empty-clone `./build.sh` proof are still pending; the preceding source-build record does not validate this update. No new candidate has been flashed by this publication step.

## Publication checkpoint —2026-11-11: scoped firmware proof and full-build manual step

The earlier full empty-clone success above applies to the named older commit. A later empty-clone run of source8ee1855 executed `./build.sh` and failed at `tools/case/print_check.py` with `print-check passed: False errors:0`. The updated official case checker requires explicit joint/wire/fit intent declarations and leaves the result unverified/manual-review required, including thin-feature review. The official tool checkout changed during that run; a later unmodified pin was retained locally. No checker was patched and no full-build pass is claimed for the current publication.

**Manual step still required:** maintainers must provide/review the case intent and measured-feature evidence required by the current official checker, then rerun `./build.sh` in an empty clone. The source publication includes this limitation; generated case outputs are not committed to cover it.

The latest hips-only firmware passed scoped `core drivers http web` host regressions and the LILYGO target compiled. A fresh source clone of this publication is checked separately for those firmware dependencies; no new full CAD/plate build is required or claimed for this checkpoint. The previous case/source proof does not certify physical motion. Both360° whole-robot trials failed the owner's practical test, as recorded in [the experiment status](firmware/EXPERIMENT-STATUS.md). Wait for parts before resuming loaded joint experiments.

## Positional180° update —2026-11-12

The owner reports replacement180° servos delivered at home and servo power disconnected at the company bench. The LILYGO release is now180-only at the final output/HTTP boundary, with explicit enable/disable, eight directions after staged enable, a conservative initial pulse span, post-trim clamps, and a separate positional trim store. The previous360° web/API modes are removed; their failed physical trials remain historical evidence.

Scoped core, actual PCA register output, real HTTP and shipped-web-script checks passed for both host pin profiles. They cover startup off,300ms enable intervals, all8 directions, slew/limits, release/deadman, assembly-centre/trim/save/disarm/re-arm, ordered requests, legacy route/output refusal, AP/QR and saved-network behavior. The LILYGO target compiled. Its full four-image set was written and byte-verified on the identified owner's original ESP32-S3; matching USB returned after watchdog reset and its serial listener was restored. Wi-Fi NVS regions were preserved. No movement commands or physical new-servo tests were performed.

The degree mapping is an unmeasured conservative assumption, not a new physical calibration. Actual supplied motors, horn fit, joint direction, clearance, supply behavior and floor walking await the bench. The manual full-CAD-build step above remains outstanding; this firmware-only work makes no new case/PCB/plate claim. Source publication is checked from a fresh clone for the scoped firmware dependencies before push.

## Normal-speed positional update —2026-11-13

The owner now reports slow movement with180° servos and requests normal speed. The base gait period changes from6seconds to1second, the default speed factor from0.4 to0.65 (approximately1.54seconds/cycle), and nominal joint slew from30 to180°/s. Joint amplitudes, final pulse/trim limits, stored trims, GPIO assignments, startup-off/staged enable and deadman behavior are unchanged. Status reports `positional180-v2`.

Scoped core, actual PCA driver, HTTP and shipped-web-script checks pass; a regression verifies the normal cycle rate and release settling. The LILYGO target compiles. Publication is checked again in a fresh clone for these firmware dependencies. This is software timing evidence, not a measured servo speed or a successful floor-walking result. The earlier full-CAD-build manual step remains outstanding.

## Held-control and tempo update —2026-11-13

The direction pad is fixed on mobile layouts and holds one pointer across status polls. Actual shipped-script tests cover unchanged disabled attributes during polls, hold renewals, unrelated finger release, context-menu/scroll prevention, global release, cancellation/capture loss, readiness loss and delayed responses. These are simulated DOM events; real iPhone/Safari touch behavior is not claimed. The base gait period is0.65seconds, giving1Hz Normal and approximately1.54Hz Fast at unchanged amplitude, pulse span and nominal180°/s slew. Core, PCA register, HTTP and web checks pass; the LILYGO firmware compiles. A fresh-clone firmware proof is required for publication; the earlier full-CAD/manual step remains unchanged.

## Crawl progress trial —2026-11-13

The owner reports leg motion with no body progress. `positional180-v4` implements three-stance-foot crawl with distinct lift/return/lower phases and shared20ms pose frames. Host tests now check recovery order, lift before return, Forward/Backward inversion,8directions, at least3 nominal contact feet, and actual PCA register output at Fast with zero trims. The updated ideal gait report uses18° hip/25° knee amplitudes. These are source/model assertions, not measured foot contact, traction, stability or successful walking. Pulse/trim limits, staged startup,180°/s slew, direct AP and release/deadman remain in force. The earlier full-CAD/manual gate remains outstanding; only firmware is being rebuilt/published.

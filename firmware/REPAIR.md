# Firmware tester repair — 2026-11-06

- Finding: the old FL/FR/RL/RR phase table `{0, pi, 3pi/2, pi/2}` lifted both feet on one side together.
- Reproduced before fixing production code: `python3 tools/firmware/check.py core` failed the new `bothSides` assertion at direction 1, sample 181/720, grounded mask 10 (FR + RR only).
- Correction: `crab/config.h::PHASE` is now `{0, pi, pi, 0}`. FL + RR alternate with FR + RL. Joint amplitudes, slew, ramps, period, pins, signs and wiring are unchanged.
- `tests/test_core.cpp::simulation` infers contact from production knee angles (0.0001 degree roundoff tolerance), asserts support on both sides/front/rear and at least two grounded feet. CSV records each grounded mask; report counts each support pattern.
- Corrected result: all 720 samples × 8 directions pass. Each direction has 359 samples on FR+RL, 359 on FL+RR, 2 with all feet down, 0 with support on only one side.
- `tools/firmware/check.py::gait_report` regenerates `GAIT-REPORT.json` from this test's output and adds its source digest. Full host checks and native build results are recorded in `TEST-RESULTS.json` and `BUILD.json`.
- No contract or release-note amendments were needed. This is a firmware timing repair within the sealed behavior. At that repair checkpoint board/case outputs were absent; they are present for the D7 repair below.
- `hardwareTested=false`. Ideal diagonal contact does not prove physical stability, ground contact, load capability or walking; the physical checklist remains required.

## Case D7 direction repair — 2026-11-06

- Lead finding: the provisional rear knee signs did not match the real mirrored mounting. Case `DEVIATIONS.md` D7 and `model.py::corner_place` show FR/RL are single mirrors and RR a double mirror.
- Reproduced before production correction: `test_case_knee_lift` failed for RL with lift **−1.67992 mm**, using actual emitted pulse, independent mounting parity and the case foot vector (15 mm outward, 64.6 mm below the knee).
- Corrected `cfg::SIGN` to `{1,1,1,-1,1,-1,1,1}`: hip signs stay +1; knee signs FL +1, FR −1, RL −1, RR +1. No pins, rails, channel assignments, gait timing, amplitudes or limits changed. WIRING.md remains valid.
- Regression: a −15° knee command must raise every foot by 5.5–6.5 mm at zero trim. The previous rear signs fail this check; corrected pulses pass. `test_interfaces.py` also checks the integration manifest matches the production table.
- `INTEGRATION.json` resolves the former placeholder and binds case evidence hashes. This implements the sealed contract instruction to reconcile signs at integration, so no contract deviation is needed.
- Fast repair check: `python3 tools/firmware/check.py core interfaces`; final suite: `python3 tools/firmware/check.py`; native binary: `python3 tools/firmware/build.py` (content cached, all cores, shared toolchain, no upload).
- `hardwareTested=false`; the pulse/geometry check is not a real SG90 motion or floor-walking test. Confirm knee lift with the body supported as part of physical assembly.

Final checks: full host suite passed; native ESP32-S3 compile uses 792045 bytes program / 45856 bytes static RAM. `BUILD.json` source and artifact hashes verified; application binary SHA256 `6012e726cb39b88fe32f697708a0a4e6dbe93c6608663ed52633e301ee19dc8b`. Existing read-only `kicadpy.verify gate .`: native findings 0, sidecar errors/warnings 0, manufacturing findings 0.


## Release note 3 carrier integration repair — 2026-11-09

- Lead finding: WIRING/README still claimed no carrier netlist, and the interface test rejected any real WS2812 carrier. Replaced the draft using current `build/board/main.net`, PCB pads and `engineering/carrier-wiring.md` / `pinout.md`.
- Final guide: screen up, USB toward `USB <`, J1=P1, J2=P2; J3 SDA/SCL/VCC/GND; J4 PCA output V+/GND; J5 LED DIN/5V/GND. OE open, LILYGO 5V isolated. Linked buy list and all 33 joints. Handwired text byte-preserved against HEAD.
- Reconciled GPIO18/17/1 and all six nets; no remap, application edit, binary rebuild or contract deviation. INTEGRATION.json no longer describes the current board as a dummy; carrier placement in printed body remains unclaimed.
- Replaced dummy assertion with 33-pad XML/PCB equality, exact six-net map and isolated NC checks; verified documentation evidence hashes/links and every BUILD.json source/artifact hash. Full-suite report binds final carrier inputs.
- Fresh native parity: 33 schematic pins and PCB pads, 0 differences/hollow symbols. Read-only gate: 0 native/manufacturing findings, fab.ready=true. Logs in `build/firmware/carrier-*-check.log`, evidence in CARRIER-CHECK.json. Final firmware host suite recorded in TEST-RESULTS.json.
- No hardware accessed/flashed, no motors run. LED data level, clone labels, actual walking and carrier body fit remain physical checks; hardwareTested=false. Local checks do not decide whole-product readiness.

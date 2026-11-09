# Source build and remaining blocker

This branch is a **work-in-progress integrated controller**, not an order-ready robot packet. Main is unchanged. The current native PCB passes electrical/manufacturing checks, and both firmware targets compile, but its case insertion/tool-access check fails. Do not use the automatic team-ready flag to override that failure.

## Required repair

`case/DEVIATIONS.md` D18 requests actual PCB corner notches, moved mounting holes and a recessed USB connector. Those changes exist only as a virtual fit proposal, not routed copper. The current PCB cannot be lowered into the base, and only one of its four screws is reachable. The U1 courtyard/antenna envelope also needs correction at the board handoff so the temporary 0.6 mm nut-seat floor can be restored. A new design-team run must repair the actual native PCB, rebuild case/plates, refresh firmware reconciliation, and pass `case/reports/assembly-access.json` for the **published** board.

The bridge currently has no internal-finding reroute operation after its erroneous candidate-ready result. A fresh owner message is required as a routing trigger; authorization for the repair already exists. This is a tool limitation, not a request for a new engineering decision.

## Toolchain

macOS, KiCad 10.0.5 and the hash-pinned model library, CadQuery 2.7.0 / OCP 7.8.1.1, Bambu Studio CLI, Arduino CLI 1.5.1 with ESP32 core 2.0.14, Pillow, clang/clang++, Node, Swift and Apple Vision. `KICAD_HARNESS_PYTHON` must import kicadpy/Pillow; `KICAD_CASE_PYTHON` must import CadQuery/OCP/numpy/matplotlib/kicadpy. The original owner PETG settings are a source input at `case/print-settings.json`.

Run `./build.sh` in a normal macOS toolchain process. A restricted agent sandbox can block Bambu startup or Apple Vision inference; those host checks need normal macOS process access. The script fetches two hash-pinned manufacturer reference inputs; it never installs software, flashes, prints, places an order or pays.

## Pipeline

1. Fetch verified manufacturer inputs and recreate component models from pinned KiCad assets/measured box inputs.
2. Preserve authored native copper; regenerate XML, STEP, ERC/DRC, orientation evidence and manufacturing packet.
3. Bind the current board handoff and source-recreate the frozen r1 parts and baseline base. Full STL/STEP hashes guard the frozen geometry; only explicit STEP timestamp/product-name metadata is restored.
4. Regenerate robot-frame CAD (`case/robot/`), board-frame native copies (`case/out/`), mechanical/native checks, offline Bambu plates and standalone assembly overview.
5. Regenerate embedded font/UI assets; bind reviewed PCB pins to the fresh XML export only after exact PCB identity/parity checks; compile both hardware targets, reconcile the board and run host/QR/vendor-display tests.
6. Require actual-board insertion/tool access, print/native checks, firmware evidence and freshness. A virtual fit proposal never satisfies the release check.

The last stage deliberately rejects the current candidate. No check is suppressed or replaced by a successful seated-pose result. Generated reports, packets, CAD, firmware images and caches remain ignored.

## Outputs

- `boards/main.board.json`, `boards/main_review/<current revision>/manufacturing/`: native reports, Gerbers/drills, BOM, CPL and manual-assembly list.
- `build/board/integrated.step`: actual populated PCB export.
- `case/robot/`, `case/out/`, `case/reports/`: CAD in the two documented frames and scoped checks.
- `case/print/production.3mf`, `test-only.3mf`, `mating-test.3mf`: offline arranged projects; no printer job is sent.
- `case/overview.html`: standalone assembly viewer generated from this build's meshes.
- `build/firmware/{integrated,esp32}/`: separate complete binary sets. `firmware/BUILD*.json`, `BOARD-RECONCILIATION.json`, `GAIT-REPORT.json` and `TEST-RESULTS.json` are regenerated evidence.

No manufactured board, new physical fit, temperature, radio range or walking test is claimed. The old LILYGO QR confirmation does not validate this PCB.

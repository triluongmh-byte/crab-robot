# Case HANDOFF (A1V4-r3: integrated board on the skeleton) — read first

Py = `"$KICAD_CASE_PYTHON"`, export `MPLCONFIGDIR=build/case/mpl`. All in the contract robot frame (mm, +X front).
Full rebuild + checks: `Py case/build.py` (4 min cold, cached when inputs are unchanged, all cores).
Fast: `Py case/build.py --only-parts --parts=base,lid` (8 s); `Py tools/case/mech_check.py --coarse --force` (60 s); `Py tools/case/make_print.py` (needs Bambu CLI); frozen check `Py tools/case/plate2_freeze.py` (<1 s); fit of a board file `python3 tools/case/board_fit.py <enclosure.json> --zb 25.6` (<1 s).

## Status — NOT ASSEMBLABLE yet (case/reports/assembly-access.json)
Seated-pose checks and the native check pass; the board's fab.ready is true. But the published 88x62 board cannot be installed: its corners are under the frozen cap-screw corner blocks and J1's nose hits the rear wall; only H1 has a straight tool path. Needs a board revision (DEVIATIONS D18), proven by `Py tools/case/assembly_access.py`: notch 4 corners (|x|>39.7, |y|>26.2), holes H1 (-36,13), H2 (36,24), H3 (-36,-24), H4 (36,-24), J1 nose at x >= -43.7. Then repin the contract with `python3 tools/case/board_import.py <enclosure.json>` and run the full build.
Frames: `case/robot/` = sealed robot-frame exports (build, checks, print plates, overview read this); `case/out/` = rigid board-frame copies (what the tile's native checker and print validator read), made by `tools/case/export_board_frame.py`. Native check: `Py tools/case/case_check.py` runs the unmodified `kicadpy.case check .` on case/out against the current boards/main.enclosure.json (report in case/reports/case-check.json; re-run after any change to case/out or the contract). Key decisions: DEVIATIONS D11–D19 (D19: base slit for the U1 contract box, board at z 22.8, deck wells/grooves).

## Do not change: plate 2 is frozen
`case/frozen-plate2-A1V4-r1.json` holds STL/STEP/3MF-mesh hashes of 2 caps + 4 thighs + 4 feet and the test coupons. `build.py` never rebuilds them and stops if their bytes differ. `case/ref/baseline-A1V4-r1/base.step` is the r1 base used by the zone diff in mech_check (belly z ≤ 18.5 and hip blocks |x| ≥ 40 must stay equal). Plate 2 is printing by owner report only; never record it from a printer status.

## Files and key places
- `case/board_placement.json` — board source file, placement (dx, dy, rot, zBottom 22.8), height/box overrides with evidence, display placement (cx −9.3, cy 20.35, ledge 44.0), plug assumptions.
- `case/ref/board-published.enclosure.json` — pinned copy of the board contract. `waveshare-23822-display.step` for the display.
- `case/model.py` — loader lines 40–100 (`BOARD_*`, `board_xy`, `DISP`, `LID_SCREWS`). `SLOT_*`, `USB_TUNNEL`, `disp_back_boxes`; `_seat_block`, `board_blocks`, `board_screw_cuts` (seat, hex nut well, head relief), `lid_pads`, `lid_pad_cuts`, `lid` (LED tie slots, −Y opening, RESET/BOOT notch, display pocket + window + tie slots, J12 screw holes), `base`, `internal_structures`, `internal_cuts` (board slots, USB tunnel).
- `case/hardware.py` — screw/nut instances C1–4, B1–4 (M3x6, board, nut in hex well), L1–3 (M3x8, self-tap Ø2.7 pilot, no nut), SG90 bag screws. 11 M3, 8 nuts.
- `case/build.py` — `electronics_items`, `FROZEN`, `shape_for`, `main`.
- `case/assembly_steps.json` — Bước 1–8 text.
- `tools/case/mech_check.py` → reports/mechanical.json, sections.csv. `_rays`, `MEMBERS`, `interface_checks`, `frozen_zone_job`.
- `tools/case/board_fit.py` → box fit of the board contract against the current base (`Py tools/case/board_fit.py <contract>`, < 2 s; reports/board-fit.json).
- `tools/case/export_board_frame.py`, `tools/case/case_check.py`, `tools/case/assembly_access.py` (insertion + screw tool-path sweep, also run from mech_check) — see Status.
- `tools/case/print_check.py` → print-check.json via `check-print` on an identical scratch copy.
- `tools/case/make_print.py`, `plate2_freeze.py`, `render_overview.py` + `overview_template.html`, `export_images.sh`, `shoot_overview.sh`, `quick_views.py`, `write_fastener_map.py`.

## Current results (full sampling, published board) — refreshed by the last full build
- Native case check on the published board (board frame, U1 false courtyard removed via interfaces.json): see case-check.json. mechanical.json passed, ±30° sweep 252 poses, 0 collisions, min leg-to-body 0.23 mm; body 125 × 75 × 46.5; 12 parts, 11 M3; slicer 6.11 h, 158.4 g (plate 1 4.19 h, plate 2 frozen and equal to r1).

## Open assumptions
- Skeleton strength and fit unproven until the owner tests them. Board plugs modelled 16.5 mm above the board, USB-C plug ≤ 11.4 mm wide (GIẢ ĐỊNH). Heights of C11 etc. come from the board team's table.
- Display module (turned 180° at x −9.3, y 20.35) is case-owned, retained by 2 ties; firmware must flip the panel orientation (D15). Sign table unchanged (hips +1; knees FL +1, FR −1, RL −1, RR +1).
- BOM.md/CHECKLIST-RAP.md/README.md live in case/ for the lead to integrate.

# Case HANDOFF (r001-v1). Read this first.
Python for CAD: `$KICAD_CASE_PYTHON`. Everything is modelled assembled in the contract body frame
(origin at the footprint centre, z=0 under the bottom, +X front, +Y left). Print turns live in `printRotateDeg`.
Full pipeline: `tools/case/run_all.sh` (full) / `tools/case/run_all.sh --coarse`. Each step skips itself when unchanged.

## Files and key features
- `case/geometry.py`: every solid and number.
  - Constants L14-69 (LID_* L37-41, LILY_Z0/Z1, HEADER_ROWS, TRENCH_Y L42-45): contract numbers, SG90 nominal, screw/nut positions, leg targets.
  - `LEGS` L65-70: per-leg sign, hip shaft, angle, PCA channels.
  - `femur_local` L154-177: hip horn groove, knee SG90 box. `_tibia_pre`/`tibia_local` L180-206: knee horn groove.
  - `_hip_pocket_quadrant` L240-261: pocket walls, nut slots, cable gaps. `bottom` L263-329: tunnel, shelf, cradle rib to z 37.5, +X end stop y 11.5-21 (D5), Dupont trenches (D4), PCA rim, LED bridge, strap slots.
  - `clamp_bar` L331-348 (lid-boss pockets), `lid` L350-378 (window, poke holes, 0.8 mm diffuser, M3x20 boss blocks + counterbores D6, 1.8 mm LILYGO/PCA pockets D4).
  - `lilygo_ref`/`modules_ref`/`keepouts` L380-411 (Dupont wire + PCA lead keep-outs): device envelopes and plug zones. `fasteners` L424+: S01–S08 instance map.
- `case/build.py`: `PARTS` table L18-37 (names, roles, print rotations), `tibia_rotation` L40, `main` L94 (cached,
  parallel export to case/out, parts.json, `verification.nativePCBCheckerApplies=false`), `write_fastener_map` L131.
  Fast: `"$KICAD_CASE_PYTHON" case/build.py` (about 8 s, skipped when unchanged).
- `case/coupon.py`: C01 TEST ONLY (pocket + M3/nut + horn groove + slimmest post). `case/refs.py`: servos, horns, modules, hardware.
- `tools/case/mech_check.py`: `static_pairs` L51 (part/device/keepout/screw interference), `sweep_sample` L82
  (hip × knee ±30°, all legs in phase), `mirror_report` L124 (STEP mirror error), `sections` L171, `fastener_report` L201, gates in `main` L213+: body height <= 47, nut slot paths open (probe of the P01 STEP), lid boss joint >= 30 mm².
  Fast: `... mech_check.py --coarse` (about 25 s). Full: 5° (about 140 s). Writes `case/reports/mechanical.json`.
- `tools/case/plates.py`: Bambu 3MF writer (`write_3mf` L146), named plates from `PLAN` L28, CLI slice (`slice_project` L195),
  limits and report. Reads `print/events.jsonl` (`ledger` L57). Layout only: `--no-slice` (1 s). Full: about 15 s.
- `tools/case/render_overview.py` + `overview_template.html` → `case/overview.html` (WebGL, Đủ bộ/Bước 1-9, Vít/tán, Chi tiết).
  Steps are the `steps` list in `render_overview.py`. Fast: `"$KICAD_CASE_PYTHON" tools/case/render_overview.py` (about 4 s).
- Final gate: `"$KICAD_HARNESS_PYTHON" -m kicadpy.case check-print .` → `case/reports/print-check.json`.
- Docs: README.md (numbers, servo signs), CHECKLIST-RAP.md, BOM.md, DEVIATIONS.md, PRINTED-INVENTORY.md, fastener_map.csv.

## Current results
12 printed parts, 8 M3 screws (4× M3×12 bar, 4× M3×20 lid+bar; heads sit in lid counterbores at z 44, top z 47.0) + 8 nuts. 2 plates: 4h27 and 2h30, 6.96 h and 186.9 g in total (Bambu CLI).
Mirror error 0 mm / 0°. Sweep ±30° at 5° steps, no collision, minimum clearance 3.3 mm (femur to lid).
Knee neutral: r = 30, z = 40, shaft z = 45.5. Foot r = 58, bottom z = −27.

## Open assumptions (GIẢ ĐỊNH)
- LILYGO z 22.8-45.8 in a lid pocket; shell underside z 37.5 and header rows y 5-9.5 / 28.5-33 are GIẢ ĐỊNH (D4).
- SG90, PCA, LED and pack sizes are nominal and unmeasured. The coupon checks the SG90 pocket and horn groove.
- Horn outline: single-arm SG90 horn, hub r 3.8, arm 17.5 mm tapering 6 → 4.2, 1.8 thick (groove 2.2 deep, +0.2 clearance).
- The USB-C L-plug head fits x −40..−33, z 32..40, with the cable dropping through the shelf hole at x −47..−40.6.
- PCA retention is rim + lid (D1). Pack retention is a strap through the floor slots at x 50..54 plus a 1.2 mm groove under the shelf.
- Wire paths in the overview are illustrative. The real wiring is `firmware/WIRING.md`.
- Plate names use U+2215 '∕' instead of '/': Bambu Studio drops a plate name containing '/' (tested via CLI round trip; plates.py now fails if names are lost).
- Firmware owns the knee sign fix (lead finding): gait '+knee = lift' needs FL -1, FR +1, RL +1, RR -1. The case report (kneeLargerPulse) is correct and unchanged.

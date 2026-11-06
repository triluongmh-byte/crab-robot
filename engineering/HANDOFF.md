# Board handoff — 2026-11-06
Contract SHA256: 65b9793b07d82edc0defd9900ba1cfbee13dc730266cc0b675d897c87a75d9ea.
Scope is only an isolated unpowered dummy PCB, never ordered or put in the robot.
No lead release notes were supplied. No deviations, cross-team pin/rail changes or user blockers.

## Owned files and features
- design/main.kicad_sch + Dummy.kicad_sym: 4 passive single-pad symbols and 2 pinless mounting holes; global labels DUMMY_A/B. Generated from tools/board/spec.json.
- design/main.kicad_pcb: 30×20×1.6 mm, 2 copper layers; holes (±10,0), Ø3.2 NPTH; four 2×3 mm front solder lands; two 8 mm long, 0.5 mm wide front tracks. Warning silk and title block match contract.
- design/main.kicad_pro: normal native minimum rules and Default class. design/main.kicad_dru lines 1–7 explicitly enforce 0.25 mm track / 0.20 clearance / 0.50 edge floor.
- design/Dummy.pretty, fp-lib-table, sym-lib-table: project-local footprints and flattened symbols; no external library dependency at review time.
- product.json: preserves shared requirements, adds dummy board geometry; hardwareTested=false.
- parts.json: empty purchased-part inventory; pads and holes are substrate features.
- manufacturing.json: exact source hashes, seven evidence areas, untouched native default ignored-check list; zero fitted components.
- engineering/{power,protection,pinout,thermal,assembly,fabricator,bringup}.md: scoped evidence and no-power handling; assembly documents local library provenance and default ignored categories.
- engineering/DEVIATIONS.md: none. This file: role map and fastest checks.
- boards/main.board.json and boards/main_review/: publisher-owned current schematic/PCB/GLB, native reports and Gerber/drill packet. Never edit them.

## Tools and fastest checks
- tools/board/prepare.py lines 1–23: initial spec, rules, product/parts setup. Initial generation only; do not rerun to repair existing copper.
- tools/board/build_pcb.py lines 1–59: initial library, placement, outline, silk, stackup. Initial generation only.
- tools/board/route.py lines 1–18: first-pass DSN/SES candidate; finish_routes.py lines 1–11 changes widths only and preserves tracks/UUIDs.
- tools/board/measure.py lines 1–44: exact native outline/hole/layer/pad/net/width/warning audit, hash-cache unchanged geometry; run with KiCad Python.
- tools/board/check.py check() lines 16–30: author/netlist/native-geometry/netlist-export/STEP checks. Thread pool uses os.cpu_count(); cached passes require unchanged inputs and existing outputs.
- Fast suite: "$KICAD_HARNESS_PYTHON" tools/board/check.py
- tools/board/review.py lines 1–24: bind seven evidence notes and design hashes; run after native/product/parts changes before publication.
- Final publication: "$KICAD_HARNESS_PYTHON" tools/board/review.py then "$KICAD_HARNESS_PYTHON" -m kicadpy.publish --manufacturing design/main.kicad_pro
- Exact native/packet result: "$KICAD_HARNESS_PYTHON" -m kicadpy.verify gate .
- Freshness: "$KICAD_HARNESS_PYTHON" -m kicadpy.verify stale .
- build/board/{author,netlist,geometry,netlist-export,step}-check.json: full suite results; main.net: actual XML netlist; geometry.json: measured geometry; main.step: bare-board solid.

- tools/board/fix_silk.py: local reference-ink repair, no copper changes. References and warnings now all use 0.15 mm strokes.

## Status and assumptions
Author check, parity (4 pins, 0 differences, 0 hollow), exact geometry and native XML/STEP exports pass. Final severity-all native and packet results are in the publisher's current reports, not the earlier draft. The draft's missing links/footprint fields/thin silk were repaired together. Final tracks measured 0.5 mm × 8 mm each, no vias or zones. Geometry is exact; no physical fit, current, temperature or robot behavior was tested. Integration readiness remains the lead/tester's decision. Robot wiring and firmware belong to the other teams; this schematic intentionally does not represent them.

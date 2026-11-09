# Board handoff — integrated I0, 2026-11-09
- Contract SHA7841b7b2e92a0d3f69db70868c7a9649da0c6cd1cfc6d94478ec13886894c1be.
- Effective release4 SHA122b5b3d…; contract/notes unchanged; no other domain edited.
- design/main.kicad_sch/.pcb/.pro: authored native circuit, accepted copper/rules.
- design/spec.json + Integrated.kicad_sym: author net table and flattened symbols.
- design/Local.pretty/.3dshapes + lib tables: local actual packages and models.
- product.json: effective88×62×1.6mm2layer1oz board, separate5V rail requirements.
- parts.json: exact40populated refs;29factory SMT /11manual THT;15SMT codes.
- manufacturing.json: source/evidence hashes, seven reviews, measured rotations.
- engineering/power,protection,pinout,thermal,assembly,fabricator,bringup.md:
  calculations, source tables, reset state,37named PCB joints and physical tests.
- engineering/sources.md + sources/integrated/: primary docs/vendorSTEP/provenance.
- factory-pads.json is static measurement INPUT; sourcing-snapshot.json dated stock.
- 3D-MODELS.md discloses USB/switch measured clearance envelopes (not detailedSTEP).
- MUA-THEM-PCB.md: Vietnamese final buy/service list; PCA bought, receipt unconfirmed.
- firmware-interface.md: GPIO18SDA/17SCL/1LED/0BOOT preserved; NEWGPIO21 /OE.
- SPI screen:8SCLK/39MOSI,5RES/6CS/7DC/38BL;15NC;9,40–42,45–48NC.
- PCA0x40, CH0..7hipFL,kneeFL,hipFR,kneeFR,hipRL,kneeRL,hipRR,kneeRR.
- R9pulls/OE high in reset/blankflash; firmwareFULL_OFF before enable low.
- No firmware written/remapped/rebuilt by board team; firmware team owns target.
- board-interface.json + case-interface.md: actual pins/frames/mounts/access/hashes.
- build/board/integrated.step: actual KiCad export normalized topCuZ0,+Yup.
- Screen officialSTEP: engineering/sources/integrated/waveshare-display.step.
- Populated PCB envelope[-45.8,-31,-3.455]..[44,31,13.845]mm; PCB88×62.
- H1(-40,13),H2(39,26),H3(-39,-26),H4(39,-26) in board-localYup;Ø3.2.
- Four available holes need not all use screws; case owns≤12M3 total/placement.
- No robot-body fit/printed-part/physical motion claim. Screen is8-wire harness.
- tools/board/build.py L1–13: release outputs FROM authored native, preserves copper.
- tools/board/check.py geometry L11–43/netlist L44–47/main L48–55:
  independent pads/rails/outline + realXML/nativeparity; hash-cached/allCPU.
- Fast audit: "$KICAD_HARNESS_PYTHON" tools/board/check.py
- export.py main L8–20 + export_geometry.py L10–26: nativeSTEP and measuredJSON;
  "$KICAD_HARNESS_PYTHON" tools/board/export.py (cached, parallel foregroundCLI).
- models.py L1–24: optional missing-model envelopes; KICAD_CASE_PYTHON runtime.
- review.py L1–39: final evidence hashes/assembly rotations from rotation.log.
- native.py L1–24: focused ERC/DRC only, cached; use relevant check during repairs.
- integrated.py L1–170/integrated_pcb.py L1–62 are PLACEMENT-DRAFT generators.
  Do not run on accepted copper; main.* native files are release-build inputs.
- route/finish/repair*.py record construction/local repairs, not release entrypoint.
- verify_module_orientation.py main L6–36: all41logical pad numbers resolves raw
  U1 rotation warning; run hostPython tools/board/verify_module_orientation.py.
- repair_entry_width.py L1–19: PB1 feeder13tracks widened0.6mm, other copper kept;
  local DRC pass; only rerun for that scoped repair, not release regeneration.
- Full release: "$KICAD_HARNESS_PYTHON" tools/board/build.py
- Final gate: "$KICAD_HARNESS_PYTHON" -m kicadpy.verify gate .
- Publisher owns boards/main.board.json/main_review previews/reports/fab packet.
- Native focused ERC/DRC and independent pad/rail/parity audit passed before packet.
- Final publisher gate: fab.ready=true; sidecar0errors/0warnings, native0findings,
  manufacturing0findings. See build/board/final-publish.log; not teamReady.
- Tool limit: native power heuristic missesPB1_5V name; independent exact-net cap
  sum verifies4.8uFnominal/5.28worst<10. Checker unmodified; see power.md.
- Open physical assumptions: bank transients, WS2812DIN3.3V, displaymodule revision,
  assembled thermal/USB/QR, soldering/wire quality. hardwareTested=false.
- Supplier docs/model inputs may be omitted from git where publishing rules require;
  primary URLs retained; native local models and checked sources are build inputs.
- No user blocker, push/commit/order/upload/print/flash/hardware action performed.

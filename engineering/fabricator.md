# Fabricator review — integrated V0

88×62×1.6mm rectangular FR4,2layers1oz(35um each),1.53mm core, explicit
stackup, HASL. Minimum project trace0.2mm, default clearance0.2mm,
minimum through drill0.3mm, via0.6/0.3mm, copper-edge0.5mm, holes0.25mm.
Power: PB1≥0.6mm,servo branches≥1mm and trunk2mm. Native filled top3V3,
bottomGND with local bottom3V3 heat island; antenna rule area forbids copper
on both layers. Eight servo headers1.02mmPTH, terminal manufacturer's exact
PTH, USB shield oval plated slots and peg NPTH preserved, four M3Ø3.2NPTH.

No via-in-pad filling or blind/buried vias required. The module EP isSMD
with paste windows. Normal top stencil, assembler panel tooling/fiducials
on sacrificial5mm rails as needed; no removable tooling is placed in robot
outline. Exact THT connectors are off-factory manual unless quote adds them.
The assembler must quote ESP certified module, not a bare RF IC substitution.

Run unmodified publisher --manufacturing: native ERC/DRC/parity --severity-all,
independent factory-floor copy, Gerber/drill parsing, pads/mask/paste, stackup,
BOM/CPL and hash-bound seven-area review. Fab readiness comes only from that
output. No local tally or earlier carrier result can substitute for it.

Tile's existing ignored DRC categories remain: missing_courtyard,
track_not_centered_on_via,tuning_profile_track_geometries,
footprint_filters_mismatch,footprint_type_mismatch. Existing ignored ERC:
single_global_label,four_way_junction,simulation_model_issue,footprint_filter.
They are unchanged baseline defaults: global-label net table deliberately
uses singleton flags/labels, SPICE not deliverable, symbol footprint filters
are library graphic metadata while actual pad parity and explicit BOM package
are checked. Physical footprint geometry/courtyard, copper shorts, electrical
connections, manufacturing floor and all warning severities remain active;
there are no DRC exclusions and no added ignored category.

Factory packet never authorizes an order. No hardware, impedance coupon,
assembly yield, case fit or physical performance has been tested.

#!/usr/bin/env bash
# Full case pipeline, in dependency order. Each step skips itself when its inputs are unchanged.
#   tools/case/run_all.sh            full (5 deg sweep + Bambu slice)
#   tools/case/run_all.sh --coarse   repair loop (15 deg sweep)
set -euo pipefail
cd "$(dirname "$0")/../.."
: "${KICAD_CASE_PYTHON:?set KICAD_CASE_PYTHON (CadQuery python of the tile)}"
: "${KICAD_HARNESS_PYTHON:?set KICAD_HARNESS_PYTHON}"
"$KICAD_CASE_PYTHON" case/build.py --no-print-binding
"$KICAD_CASE_PYTHON" tools/case/mech_check.py ${1:-}
"$KICAD_CASE_PYTHON" tools/case/plates.py
"$KICAD_CASE_PYTHON" case/build.py            # adds printProject binding to parts.json
"$KICAD_CASE_PYTHON" tools/case/render_overview.py
"$KICAD_HARNESS_PYTHON" -m kicadpy.case check-print .
python3 -c "import json;r=json.load(open('case/reports/print-check.json'));print('check-print passed' if r['passed'] else r['errors'])"

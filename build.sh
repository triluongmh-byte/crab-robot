#!/usr/bin/env bash
# Recreate the checked design from source. Never installs, flashes, prints or orders.
set -euo pipefail
cd "$(dirname "$0")"
: "${KICAD_HARNESS_PYTHON:?Missing KICAD_HARNESS_PYTHON: use the KiCad Harness host Python}"
: "${KICAD_CASE_PYTHON:?Missing KICAD_CASE_PYTHON: use the Harness CadQuery Python}"
for tool in "$KICAD_HARNESS_PYTHON" "$KICAD_CASE_PYTHON"; do
  [[ -x "$tool" ]] || { echo "Missing executable: $tool" >&2; exit 1; }
done
for tool in python3 node clang clang++ arduino-cli; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool (no automatic install)" >&2; exit 1; }
done
[[ -x /Applications/BambuStudio.app/Contents/MacOS/BambuStudio ]] || {
  echo "Missing Bambu Studio CLI at /Applications/BambuStudio.app/Contents/MacOS/BambuStudio" >&2; exit 1;
}
export CIRCUIT_FIRMWARE_CACHE="${CIRCUIT_FIRMWARE_CACHE:-$HOME/.cache/autonomous-circuit/firmware}"
export ARDUINO_DIRECTORIES_DATA="${ARDUINO_DIRECTORIES_DATA:-$CIRCUIT_FIRMWARE_CACHE/arduino}"
[[ -d "$ARDUINO_DIRECTORIES_DATA/packages/esp32" ]] || {
  echo "Missing shared Arduino ESP32 core: $ARDUINO_DIRECTORIES_DATA/packages/esp32" >&2; exit 1;
}
echo "1/5 Dummy board: native exports, STEP, ERC/DRC and packet"
"$KICAD_HARNESS_PYTHON" tools/board/check.py
"$KICAD_HARNESS_PYTHON" -m kicadpy.publish --manufacturing design/main.kicad_pro
"$KICAD_HARNESS_PYTHON" -m kicadpy.verify gate .
echo "2/5 Case: CAD, mechanical checks, native Bambu plates, overview and print check"
bash tools/case/run_all.sh
echo "3/5 Assembly images from the current exported meshes"
"$KICAD_CASE_PYTHON" tools/render_assembly_images.py
echo "4/5 ESP32-S3 binary and production host tests"
python3 tools/firmware/build.py
python3 tools/firmware/check.py
echo "5/5 Verify all final artifact bindings"
"$KICAD_HARNESS_PYTHON" - <<'PY'
import json
from pathlib import Path
from kicadpy.parallel import check_plates
r=Path.cwd()
assert json.loads((r/'boards/main.board.json').read_text())['fab']['ready'] is True
for p in ['case/reports/mechanical.json','case/reports/print-check.json','case/print/production-check.json']:
    assert json.loads((r/p).read_text())['passed'] is True,p
assert json.loads((r/'build/firmware/host/report.json').read_text())['pass'] is True
check_plates(r)
for p in ['case/overview.html','case/print/production.3mf','case/print/TEST-ONLY-coupons.3mf',
          'build/firmware/esp32/crab.ino.bin','build/board/main.step',
          'case/images/assembled.png','case/images/exploded.png','case/images/top.png','case/images/front.png']:
    assert (r/p).is_file(),p
print('PASS: native board, case, plate bindings, firmware, images and overview; hardwareTested=false')
PY
"$KICAD_HARNESS_PYTHON" -m kicadpy.verify stale .

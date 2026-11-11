#!/usr/bin/env bash
# Regenerate deliverables; never installs tools, flashes, prints or places orders.
set -euo pipefail
cd "$(dirname "$0")"
: "${KICAD_HARNESS_PYTHON:?Set KICAD_HARNESS_PYTHON to the KiCad Harness host interpreter}"
: "${KICAD_CASE_PYTHON:?Set KICAD_CASE_PYTHON to the pinned CadQuery interpreter}"
for executable in "$KICAD_HARNESS_PYTHON" "$KICAD_CASE_PYTHON"; do
  [[ -x "$executable" ]] || { echo "Missing interpreter: $executable" >&2; exit 1; }
done
for executable in node clang clang++ swiftc arduino-cli; do
  command -v "$executable" >/dev/null || { echo "Missing tool: $executable; install the documented toolchain first" >&2; exit 1; }
done
[[ -x /Applications/BambuStudio.app/Contents/MacOS/BambuStudio ]] || {
  echo "Missing Bambu Studio CLI at /Applications/BambuStudio.app/Contents/MacOS/BambuStudio" >&2; exit 1;
}
"$KICAD_HARNESS_PYTHON" - <<'PY'
import importlib.util
for module in ['kicadpy','PIL']:
    if importlib.util.find_spec(module) is None: raise SystemExit('Missing host Python module: '+module)
from kicadpy import toolchain
version=toolchain.run([toolchain.executable('cli'),'version']).strip()
if version!='10.0.5': raise SystemExit('Expected KiCad 10.0.5, found '+version)
PY
"$KICAD_CASE_PYTHON" - <<'PY'
import importlib.util
for module in ['cadquery','OCP','numpy','matplotlib','kicadpy']:
    if importlib.util.find_spec(module) is None: raise SystemExit('Missing case Python module: '+module)
import cadquery,OCP
if cadquery.__version__!='2.7.0' or OCP.__version__!='7.8.1.1':
    raise SystemExit('Expected CadQuery 2.7.0 / OCP 7.8.1.1 for the frozen print geometry')
PY
export CIRCUIT_FIRMWARE_CACHE="${CIRCUIT_FIRMWARE_CACHE:-$HOME/.cache/autonomous-circuit/firmware}"
export ARDUINO_DIRECTORIES_DATA="${ARDUINO_DIRECTORIES_DATA:-$CIRCUIT_FIRMWARE_CACHE/arduino}"
[[ -d "$ARDUINO_DIRECTORIES_DATA/packages/esp32" ]] || {
  echo "Missing shared Arduino ESP32 core at $ARDUINO_DIRECTORIES_DATA/packages/esp32" >&2; exit 1;
}
mkdir -p build/board build/case/mpl
export MPLCONFIGDIR="$PWD/build/case/mpl"
echo '1/7: Verified manufacturer inputs and pinned component models'
"$KICAD_HARNESS_PYTHON" tools/fetch_sources.py
"$KICAD_CASE_PYTHON" tools/board/prepare_models.py
echo '2/7: Native board, STEP, ERC/DRC, manufacturing packet'
"$KICAD_HARNESS_PYTHON" tools/board/build.py
echo '3/7: Current board-to-case binding and source-recreated frozen parts'
"$KICAD_HARNESS_PYTHON" tools/case/bind_case.py
"$KICAD_HARNESS_PYTHON" tools/case/rebuild_frozen.py --output case/robot
echo '4/7: Case CAD, mechanical/native checks, plates and assembly overview'
"$KICAD_CASE_PYTHON" case/build.py
echo '5/7: Both firmware targets, host tests and final board reconciliation'
"$KICAD_HARNESS_PYTHON" tools/firmware/embed_assets.py
"$KICAD_HARNESS_PYTHON" tools/firmware/bind_board.py
"$KICAD_HARNESS_PYTHON" tools/firmware/build.py --target all
"$KICAD_HARNESS_PYTHON" tools/firmware/reconcile.py
"$KICAD_HARNESS_PYTHON" tools/firmware/candidate.py
"$KICAD_HARNESS_PYTHON" tools/firmware/check.py
echo '6/7: Complete product packet checks, including actual PCB insertion'
"$KICAD_HARNESS_PYTHON" tools/verify_release.py
"$KICAD_HARNESS_PYTHON" - <<'PY'
from pathlib import Path
from kicadpy.parallel import check_plates
check_plates(Path.cwd())
PY
echo '7/7: Artifact freshness'
"$KICAD_HARNESS_PYTHON" -m kicadpy.verify stale .

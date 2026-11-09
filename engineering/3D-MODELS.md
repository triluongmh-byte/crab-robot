# Model provenance and geometric limits

PCB STEP is exported from the current actual KiCad board; no guessed outline
or reused case reference is substituted. Supplier screen STEP is the official
Waveshare archive (SHA-bound in board-interface.json), used separately because
screen is on its8-wire harness. Case owns its robot-frame placement.

Most component STEP files are bundled native KiCad assets. This machine's
bundle lacks HRO USB and XKB switch models referenced by its own footprints.
The official current KiCad model URLs returned404; the tool was not patched.
For these two assets, tools/board/models.py exports conservative clearance
solids: USB X/Y from its native F.Fab contact/body envelope, Z from the actual
supplier OBJ; switch from actual supplier OBJ bounds. These are explicitly
clearance envelopes, not detailed manufacturer component STEP. USB opening
face/direction is from the actual footprint. Use clearance bounds and access
instructions, not the solid box as a picture of the socket's hollow port.
Supplier mesh/source JSON is retained, with hashes in build/board/model-C*.json.

**JLCEDA/EasyEDA Official Library** — https://lceda.cn/ and https://easyeda.com
C165948 OBJ uuid617b05f9bba7410b96c001093d8189e4:
https://modules.easyeda.com/3dmodel/617b05f9bba7410b96c001093d8189e4
C318884 OBJ uuid91b67c1735f643ffb2e7226c23dd3492:
https://modules.easyeda.com/3dmodel/91b67c1735f643ffb2e7226c23dd3492
Original supplier metadata and copyright notices remain in sources/integrated/.
No OBJ author instruction was treated as electrical evidence.

Bulk capacitor native STEP is a matching standard10mm case; allow at least
11mm height for exact DMBJ part/tolerance. Terminal nativeSTEP is exact5.08mm
Phoenixfamily. Header nativeSTEP matches2.54mm Samtec mechanical reference;
allow plugged connectors and wire slack beyond these naked-board bodies.
These limits are explicitly handed to case. No physical fit is claimed.

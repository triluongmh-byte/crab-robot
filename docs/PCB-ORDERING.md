# Requesting a PCB assembly quote

The current prototype uses the side-entry USB-C PCB and two open frames. See [build validation](../BUILD-VALIDATION.md) for desktop checks and the remaining first-board tests.

This is an **integrated controller prototype**, not a socket carrier. The ESP32-S3 module and PCA9685 are assembled on the custom PCB. Do not substitute the original LILYGO/PCA module bill of materials.

Run `./build.sh` and use its **current** manufacturing packet. `design/main.kicad_pcb` is the authored PCB, `parts.json` identifies exact parts and assembly methods, and the generated `boards/` tree contains the manufacturing exports and reports. Never quote from a stale packet left over from a failed build.

| Setting | Value |
|---|---|
| Size | 88 × 62 mm |
| Layers | 2 |
| Material / thickness | FR-4, 1.6 mm |
| Copper | 1 oz |
| Assembly | Top side |
| SMT placements | 29, using 15 unique sourced codes |
| Through-hole connectors | 11, request hand assembly if not included |
| Remaining PCB joints without THT assembly | 37 |

Provide Gerbers, drill files, BOM and corrected placement/CPL files together. The manufacturing evidence records a **180° assembly offset for the TI SOT-223 regulator**, with the other SMT offsets 0°. Use the exported CPL; do not re-create it by guessing from a board picture. The raw orientation tool's ESP32 exposed-pad warning is resolved by the separate numbered-pad audit documented in `engineering/assembly.md`; keep that evidence available to the assembler.

Ask the assembler to confirm the exact module **ESP32-S3-WROOM-1-N16R8**, TI **TLV1117LV33DCYR**, NXP **PCA9685PW,118**, USB-C part and capacitor polarity against the BOM and placement preview. Stock was checked on 2026-11-09; it is not a stock or price guarantee. Obtain a fresh quote before paying. The through-hole connector table is in [AFTER-ORDER.md](AFTER-ORDER.md).

Request an electrical inspection and first-power check from the assembly service: rails/common ground, no positive bridge between the two 5 V inputs, blank/reset servo output disabled, USB programming in both connector orientations, display/QR and regulator temperature. The engineering bring-up and thermal documents give the detailed checks for the service.

The design has not yet been tested as a manufactured board. CAD and firmware build results support making a prototype; they do not establish production yield or loaded robot behavior. This repository contains no order, payment or manufacturing confirmation.

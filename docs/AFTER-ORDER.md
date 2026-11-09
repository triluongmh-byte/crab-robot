# What to buy after ordering the integrated controller

**Draft for the pending board revision. The current PCB does not assemble into the case; do not order it. See the WIP notice in the root README.**

Order **PCBA**, with the components assembled, rather than an empty PCB. This controller carries the ESP32-S3-WROOM-1-N16R8, PCA9685 and 3.3 V regulator itself. Your LILYGO board and separate PCA9685 module remain useful for the original modular robot; neither plugs into this controller.

## Include in the assembly quote

The manufacturing BOM specifies 29 factory SMT placements. Also ask the assembler to install these 11 through-hole connectors; they can be a separate hand-assembly service:

| References | Quantity | Part |
|---|---:|---|
| J2–J9 | 8 | Samtec TSW-103-07-G-S, 1×3 male header, 2.54 mm |
| J10 | 1 | Samtec TSW-108-07-G-S, 1×8 male header, 2.54 mm |
| J11 | 1 | Samtec TSW-103-07-G-S, 1×3 male header, 2.54 mm |
| J12 | 1 | Phoenix Contact 1715721, two-position 5.08 mm screw terminal |

If the assembler omits these, buy the exact connectors and have a soldering service fit them: **37 PCB solder joints** (27 on the nine 3-pin headers, 8 on the LCD header, 2 on the terminal). The ESP module, USB-C connector and PCA chip are intended for factory assembly.

## External parts

| Item | Quantity | Purchase condition |
|---|---:|---|
| Waveshare **1.9inch LCD Module, SKU 23822** | 1 | ST7789V2, 170×320, with its supplied 8-wire cable. Buy the assembled module, not an FPC-only screen. The LILYGO screen stays on its old board. |
| USB-A to USB-C **data** cable | 1 | For programming and power-bank port 1. USB-C plug body must be **at most 11.4 mm wide × 7 mm thick × 15 mm long** to pass the rear tunnel. Reuse a cable only if it meets both requirements. |
| Three female-to-female 2.54 mm leads | 1 set | J11 → LED bar DIN / 5V / GND, if the bar has fitted pins. If it has bare pads, have the service solder three leads to it instead. |
| Small cable ties | 3 minimum | 2.5 mm wide, at least 150 mm long: two LCD, one LED; keep spares for cables. |
| Case fasteners | 11 screws + 8 nuts | Candidate: 4× M3×20, 4× M3×6, 3× M3×8; confirm after the fit repair and check your existing bag. |

Reuse the eight SG90 servos with horns/screws, WS2812 eight-LED bar, two-output 5 V power bank and USB-to-terminal power adapter if already owned. Ownership of everything except the reported LILYGO and ordered PCA module has not been confirmed. The separately ordered PCA module is **not an extra purchase for this variant**.

See the [complete external-parts BOM](../case/BOM.md) for power-bank, adapter, wire and strap dimensions.

The LCD's small connector is identified by the manufacturer as **MX1.25**, not JST-GH. Prefer the supplied cable; do not buy a cable solely from a similar connector photo. Connect by printed signal names, not wire colors.

## What still needs hands-on work

The assembler should check soldering, power rails, USB in both orientations, reset/BOOT, idle servo outputs and regulator temperature before the first loaded test. The PCB mounting holes have no copper-free annulus; the service must inspect insulation under the mounting hardware and prevent hardware from bridging exposed copper. Do not scrape solder mask or rely on overtightened metal hardware.

The owner then fits the board/screen, plugs the labeled cables, flashes the **integrated** firmware, scans the QR and centers the servos before attaching horns. CAD checks and compiled firmware do not establish physical fit, motor direction, radio performance, power-bank surge behavior, LED input compatibility or temperature. These are first-prototype checks, not completed tests.

Primary product references: [Waveshare module](https://www.waveshare.com/1.9inch-LCD-Module.htm), [module documentation](https://www.waveshare.com/wiki/1.9inch_LCD_Module), [Samtec headers](https://www.samtec.com/products/tsw), [Phoenix terminal](https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-15-2-508-1715721).

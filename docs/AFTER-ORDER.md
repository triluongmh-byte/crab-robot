# What to buy and ask the assembler to fit

Order **assembled PCBA** for the integrated controller. The ESP32-S3 module, PCA9685, regulator and USB-C belong on that one PCB. Read the current [build validation](../BUILD-VALIDATION.md) before using a manufacturing packet; no order has been placed by the project.

## Include in the assembly quotation

The BOM specifies 29 factory SMT placements. Also request installation of these eleven through-hole connectors:

| References | Quantity | Specified part |
|---|---:|---|
| J2–J9 | 8 | Samtec TSW-103-07-G-S, 1×3 male header, 2.54 mm |
| J10 | 1 | Samtec TSW-108-07-G-S, 1×8 male header, 2.54 mm |
| J11 | 1 | Samtec TSW-103-07-G-S, 1×3 male header, 2.54 mm |
| J12 | 1 | Phoenix Contact 1715721, two-pole 5.08 mm screw terminal |

If the PCBA service covers only SMT, have a soldering service fit these connectors: **37 PCB joints**: 27 on nine three-pin headers, eight on the LCD header and two on the power terminal. The factory handles the ESP module, PCA chip and USB connector. If the LED stick has bare pads, ask for its three leads to be soldered as an additional external job; a prewired/prepinned stick avoids that job.

## External parts and assembly supplies

Reuse suitable owned items. The photographs establish eight mechanically installed servos and the printed leg parts; ownership of the remaining items for this integrated variant is not established.

| Item | Quantity | What to select |
|---|---:|---|
| Waveshare **1.9inch LCD Module, SKU 23822** | 1 | Assembled ST7789V2, 170×320 module with its supplied eight-wire cable |
| USB-A to USB-C **data/sync** cable | 1 | For programming and bank port 1. The ordinary-plug check uses a 12.5 mm wide × 7 mm thick × 25 mm long housing at the PCB's +Y side. Cable diameter ≤4.5 mm. Use a cable within the checked size; bank-end right-angle USB-A housing ≤22 mm long |
| LED harness | 3 wires | J11→DIN/5V/GND; female-to-female 2.54 mm leads if the LED bar has fitted pins, or have the service attach leads |
| Thin zip ties | At least 11, plus spares | 2.5 mm wide, ≥150 mm: two LCD, one LED, eight for knee-lead strain relief |
| Frame/PCB hardware | 7 screws and 4 nuts | Four M3×6, three M3×12, four M3 nuts; verify the lengths in your existing bag |
| Correct servo screws | 16 tab + 8 horn-arm + 8 centre | Reference lengths 8/6/4 mm respectively; use the right types. See [the mechanical BOM](../case/BOM.md) for stock shortages. Spare centre screws are not horn-arm replacements |
| JR-compatible three-wire male/female servo extensions | As needed | Approximately 20 cm for a stock lead that cannot reach an alternate route without tension; keep added connectors on the fixed frame side |
| Hook-and-loop bank strap | 1 | 10–12 mm wide, ≥420 mm long, removable for charging |
| Closed two-output 5 V power bank and USB-to-terminal adapter | 1 each if not already owned | Use [the mechanical dimensions and selection criteria](../case/BOM.md), including the bank and adapter envelopes |
| WS2812 eight-LED stick and red/black 22 AWG power wire | As needed | Reuse suitable stock; obtain the correct prewired stick/harness rather than fine soldering at home |

The new frame reuses four thighs and four feet. Both interfering clamp bars are retired. Only its two structural frames are new prints; the small TEST ONLY saddle coupon is separate. See [the owner inventory and photos](../references/OWNER-PRINTS.md).

The separately bought PCA9685 breakout and LILYGO remain useful for the original modular robot. This custom controller already contains both controller functions, so those breakouts are not additional purchases for this variant. The original LILYGO firmware and its wiring table remain available.

## Before the first loaded test

Ask the assembler to inspect soldering and mounting insulation, check the rails, test USB enumeration/flashing in **both plug orientations**, verify BOOT/RESET and idle servo outputs, and check the regulator temperature. USB line impedance and real operating temperature remain unmeasured; the board's geometry/electrical checks do not replace this first-board test. Inspect insulation around mounting hardware and exposed copper rather than relying on solder mask alone.

The owner then follows the illustrated guide: fit the board/display, plug the labelled leads, use the **integrated** firmware target, scan the QR and centre the unloaded servos before attaching horns. Real fit, retention, wire flexibility, motor directions, radio range, bank shutoff/surges, WS2812 data level, floor grip and walking are still first-prototype checks. The owner's earlier LILYGO QR success does not validate this new PCB.

Use the display module's supplied cable. The manufacturer's catalogue uses inconsistent MX/GH connector names; a matching-looking loose eight-pin lead is not a verified replacement. Connect by the printed signal names.

Primary references: [Waveshare module and included cable](https://www.waveshare.com/product/1.9inch-lcd-module.htm), [module documentation](https://www.waveshare.com/wiki/1.9inch_LCD_Module), [Samtec headers](https://www.samtec.com/products/tsw), [Phoenix terminal](https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-15-2-508-1715721).

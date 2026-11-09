# Planned case and external-parts BOM

**Draft: the current PCB needs the D18 repair before ordering or printing the new base/lid.** Quantities below describe the present candidate, not confirmed ownership or a finished physical assembly. Buy only missing items after checking your existing kit.

| Item | Quantity | Match / size condition |
|---|---:|---|
| Integrated controller PCBA | 1 | Pending actual PCB fit revision; ESP32-S3 + PCA9685 onboard. SMT plus connector assembly as specified in [AFTER-ORDER](../docs/AFTER-ORDER.md). |
| Waveshare 1.9inch LCD Module, SKU 23822 | 1 | ST7789V2, 170×320, 51.2×27.3 mm module, supplied 8-wire cable. |
| SG90 servo with horn/screw bag | 8 | Four hip and four knee servos. Each bag needs a single-arm horn, two mounting screws and a center screw; the robot uses 24 bag screws. Two spare servos are optional. |
| M3×20 screws | 4 | C1–C4 clamp bars. |
| M3×6 screws | 4 | B1–B4 PCB retention; final revised holes/tool paths must pass. |
| M3×8 screws | 3 | L1–L3 lid, forming threads in the printed pilots. |
| M3 hex nuts | 8 | Four clamp nuts and four board nuts. |
| Cable ties | 3 minimum | Width 2.5 mm, length at least 150 mm: two LCD, one LED. Keep spare ties for cable dressing. |
| WS2812 eight-LED stick | 1 | About 53–56 mm long, input DIN / 5V / GND. |
| Thin 5 V power bank with two USB-A outputs | 1 | Maximum 100×65×15 mm, at most 120 g, ports on the short edge; at least 2.4 A per port. Prefer one that stays on with a small load. Actual combined-load/surge behavior still needs testing. |
| USB-A to USB-C data cable | 1 | Right-angle USB-A plug body at most 22 mm long. USB-C body at most **11.4 mm wide × 7 mm thick × 15 mm long**. Confirm reach after J1 moves. Charge-only cables cannot program the board. |
| USB-A male to two-pole screw-terminal adapter | 1 | Smaller than 22×20×15 mm, labeled positive/negative. |
| Servo-supply red/black wire | 1 pair | 22 AWG, approximately 30 cm each; cut/route to the final assembly. |
| LED cable | 1 three-wire set | Female-to-female 2.54 mm if the LED stick has pins; have the service solder three leads if it has bare pads. |
| Hook-and-loop strap | 1 | Width 10–12 mm, length at least 42 cm, retaining the power bank. |
| PETG | As generated slicer report | Bambu A1, 0.4 mm nozzle, owner settings in `print-settings.json`; do not treat a slicer estimate as an actual print. |

A straightened paper clip can reach BOOT/RESET through the access notch. Foam tape is optional if the real display/LED retention needs adjustment after fit testing.

The original LILYGO board and separately ordered PCA9685 module are not fitted in this integrated variant. Keep them for the original modular build. Receipt of the ordered PCA and completion/fit of plate 2 have not been confirmed.

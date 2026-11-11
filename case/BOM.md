# Mechanical parts and remaining purchases

For electronics assembly and the exact through-hole service, use [AFTER-ORDER.md](../docs/AFTER-ORDER.md). The integrated PCB replaces the LILYGO development board and separate PCA9685 breakout; the original modular firmware/wiring remains available.

## Current production parts

| Item | Quantity | Status |
|---|---:|---|
| `frame_lower`, `frame_upper` | One each | New r5 structural parts; unprinted |
| `thigh_FL/FR/RL/RR`, `foot_FL/FR/RL/RR` | Eight total | Reuse existing prints; exact physical source revision unmeasured |
| Previous `cap_front`, `cap_rear` | Two | Printed, removed for servo interference, unused; not in Print all |
| SG90-class servos and matching one-arm horns | Eight owned | Keep the confirmed continuous 360° units for the experimental controller. The legacy angular gait requires a separate positional configuration; no replacement purchase is selected. |
| M3×6 screws / M3 nuts | Four / four | PCB mounts B1–B4 |
| M3×12 screws | Three | Frame joints J1–J3; printed self-tapping pilots, no nuts |

Confirm the screw lengths in the owned stock; the existence of an M3 assortment does not establish every length.

## Required servo type

**Current owned assembly:** keep the eight confirmed continuous-rotation SG90s; no 180° purchase is selected. On 2026-11-11 the owner reported each installed servo worked when tested individually and all hips/elbows were manually placed at the 90° reference. Use the [360° manual-reference experiment](../firmware/CONTINUOUS360.md), which commands bounded, single-channel, estimated-angle jogs after observed calibration. It does not establish loaded walking or angle holding.

The retained positional angular gait is a different configuration and requires compatible positional servos. Continuous PWM servos control speed/direction; a manual reference and time estimate do not add position feedback. Do not enable the positional setting for the owned continuous motors.

The frame and leg geometry is retained. The owner's current body is the earlier manually cropped/drilled print; the new r5 frame remains unprinted. Servo dimensions, supply capacity and loaded clearance remain unmeasured. No replacement, reprint, order or full-robot motion is implied by the individual tests.

Reference: [Adafruit's explanation of continuous-rotation control](https://learn.adafruit.com/adafruit-motor-selection-guide/continuous-rotation-servos).

## Servo screws — count by type

The model uses **32 servo screws**, not 32 interchangeable screws:

| Function | Count | Reference length | IDs |
|---|---:|---:|---|
| Hip and knee mounting tabs | 16 | 8 mm | T*-1/2 and K*-tab1/2 |
| Horn-arm attachment into printed legs | 8 | 6 mm | H*-arm and K*-arm |
| Horn centres into servo output shafts | 8 | 4 mm | H*-ctr and K*-ctr |

These are factory/reference dimensions, not measurements of the owner's bags. Use the proper type at each location and confirm engagement with the coupon. **Do not substitute centre screws for horn-arm self-tapping screws.** If ten bags contain two mounting screws and one centre screw each, they provide twenty mounting/arm candidates and ten centre screws: even if the former suit both uses, four appropriate self-tapping screws are still missing. Obtain matching replacements of the correct types/lengths; do not count the two spare centre screws as replacements. Keep useful screws from the old body only after checking that they match the required type and length.

## Bought external items

| Item | Quantity / selection criterion |
|---|---|
| Assembled integrated controller PCB | One; follow the PCBA quote and through-hole service guide |
| Waveshare 1.9-inch ST7789 LCD module **23822**, with supplied eight-wire cable | One, reference module 51.2 × 27.3 mm; not a bare FPC panel |
| WS2812 eight-LED stick | One, approximately 53–56 mm; 5V/GND/DIN |
| Closed power bank, two USB-A outputs | Reference envelope **100 × 65 × 15 mm**, mass ≤120 g; outputs on a short edge, each rated at least 2.4 A. Load capacity and low-load shutoff remain bench checks |
| USB-A to USB-C **data/sync** cable | Approximately 30 cm; bank-end right-angle USB-A housing ≤22 mm long; USB-C housing **≤12.5 mm wide, ≤7 mm thick, ≤25 mm long**, cable diameter ≤4.5 mm; PCB +Y side entry |
| USB-A male to two-pole screw-terminal adapter | One, ≤22 × 20 × 15 mm, clearly marked polarity |
| Thin 2.5 mm zip ties, ≥150 mm long | At least eleven: two LCD, one LED, two per knee-lead loop; keep spares |
| Hook-and-loop strap | 10–12 mm wide and ≥420 mm long; removable bank retention |
| LED three-wire harness and red/black servo-power wires | Match the wiring guide; approximately 30 cm, 22 AWG power wire |
| Matching servo-screw replacements | Count the three types above before ordering |
| JR-compatible three-wire male/female servo extensions, approximately 20 cm | Optional, only for stock leads that cannot reach the chosen open route without tension; keep added connectors on the fixed frame side |

Choose a USB-C head within the checked dimensions; a product photograph or “slim” label does not establish its size. The USB-A/servo load, WS2812 data level, bank behaviour and real connector sizes still require the documented first-prototype checks. Nothing has been ordered by the project.

Reference only: [TowerPro lists a 25 cm lead and JR plug for its SG90 Digital](https://towerpro.com.tw/product/sg90-7/). This does not identify the owner’s servo clone or establish its cable length. The longest current fixed route is 252 mm before the remaining plug approach and any moving loop; check reach before fastening ties and use a suitable extension where needed.

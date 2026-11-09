# Assembly BOM

[Tiếng Việt](BOM.vi.md).

Updated 9 November: the LILYGO is owned and displays QR/web; the PCA9685 is still missing. See the [PCA buying and wiring guide](docs/PCA9685-WIRING.md). Screw and material quantities below belong to the 6 November closed-body source baseline, not skeleton r2. Other owned items are **ASSUMED** from the original request/photos; check before buying duplicates. Do not buy components for the dummy board.

| Category | Item / quantity | Search terms and identification |
|---|---|---|
| Owned | LILYGO T-Display-S3 non-touch ×1 | Integrated screen, ESP32-S3; 29 April 2024 schematic; soldered headers labeled 17, 18, 1, 21, 3V, GND. LED pin depends on firmware version. |
| Owned, assumed | SG90 ×8 installed +2 spare | 180° positional servos, not continuous rotation; keep single-arm horns and supplied screws. |
| **To buy** | **PCA9685 ×1, headers soldered** | Search **“PCA9685 16 channel servo driver I2C pre soldered”**; sixteen three-pin sockets numbered 0–15, V+/GND screw terminal, VCC/GND/SDA/SCL control pins. Both headers and terminal must be fitted. |
| Owned, assumed | KK10 WS2812 eight-pixel bar ×1 | Eight addressable LEDs with **DIN/5V/GND** input; not a two-wire white LED strip. |
| Owned, assumed | 4 M3×12, 4 M3×20, 8 M3 nuts | Baseline quantities; no washers/standoffs. M3×6/M3×8 remain spare; use SG90 bag screws for the servos. |
| To buy if missing | Two-port 5 V USB power bank ×1 | Search “slim 5000mAh dual USB-A 2.4A power bank”. **≤100×65×15 mm, ≤120 g**, both outputs usable together, ≥2.4 A per port; ports on a short edge; enclosed product, no loose cells. |
| To buy if missing | USB-A → USB-C data cable ×1 | Short cable, preferably a 90° USB-C plug. Unplug its A end for flashing instead of pulling the board out. |
| To buy if missing | USB-A to 5 V screw-terminal adapter ×1 | Search “USB 5V screw terminal adapter”; positive to PCA V+, ground to PCA GND. Compact, no soldering of power leads required. |
| To buy if missing | Female-to-female Dupont wires ×7 | Search “Dupont female female 10cm”; four LILYGO–PCA wires and three LED connections. If the LED has bare pads, ask the shop to solder its three IN wires. |
| To buy if missing | Male-to-male Dupont wires ×4 | For the current flashed-board power arrangement: two parallel leads per polarity between the USB adapter and PCA terminal. |
| To buy if missing | 2.5×100 mm cable ties | Baseline uses one LED tie; skeleton r2 uses two. Keep extras for wire routing. |
| To buy if missing | Releasable battery strap ×1 | Baseline: width ≤4 mm, length ≥25 cm. Skeleton r2 needs its own ≥42 cm strap per the workspace assembly guide. |
| To buy if missing | PETG and tools | Baseline: about 187 g production parts +26 g test pieces; 2.5 mm hex key for M3 socket heads (**ASSUMPTION**) and small Phillips screwdriver for SG90 screws. |
| Optional | Shop-soldered LED input wires | Needed only if the LED has bare pads; no extra power circuit or electronic components. |

Check horn/module fit with both test sets. If the power bank shuts off, choose a suitable bank or reduce motion speed as described in the firmware guide; do not build a custom power circuit. [Baseline wiring, in Vietnamese](firmware/WIRING.md) · [Baseline mechanical BOM, in Vietnamese](case/BOM.md).

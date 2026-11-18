# 🛠️ Build guide

This is how the crab in the [README](../README.md) photos was put together: a LILYGO T-Display-S3 and a PCA9685 on a printed open frame.

[Parts](#1-parts) · [Print](#2-print) · [Flash](#3-flash-the-lilygo) · [Wire](#4-wire) · [Centre the servos](#5-centre-the-servos-before-the-legs-go-on) · [Assemble](#6-assemble) · [Calibrate](#7-calibrate-and-drive)

> ⚠️ Unplug **every** supply before you change a wire. Never force a leg by hand or by motor against the frame.

## 1. Parts

| Qty | Part | Note |
|---|---|---|
| 1 | LILYGO T-Display-S3, non-touch | Brain, Wi-Fi and the eye screen |
| 1 | PCA9685 16-channel servo board | Drives CH0–CH7 |
| 8 | SG90 **positional 180°** servos | Not the 360° continuous kind: [why](../firmware/EXPERIMENT-STATUS.md) |
| 2 | HC-SR04P ultrasonic modules (3.3 V-capable) | The sonar eyes |
| 1 | WS2812 strip, 8 LEDs | Lamp |
| 1 | 1000 µF capacitor, ≥ 10 V | Across the servo supply |
| 1 | 5 V supply | A power bank, or [2 × 18650 + LM2596 / UBEC](../firmware/BATTERY-AUTONOMY.md#battery-now-with-parts-already-owned) |
| — | Dupont leads, 2 zip ties (2.5 mm), a rubber band, cyanoacrylate (502) glue | M2 self-tappers for the sonar head are optional |

## 2. Print

All parts are PETG on a Bambu A1 with a 0.4 mm nozzle (repo profile `case/print-settings.json`). The generated `.3mf` files are not in Git; run the script named in each row to make them.

| Part | Source | Make it with |
|---|---|---|
| Body: `frame_upper` only (`frame_lower` is not used) | [case/](../case/README.md) | `./build.sh`, then plate 1 of `case/print/production.3mf`, with `frame_upper` selected |
| 4 thighs + 4 feet | [case/](../case/README.md) | Plate 2 of the same project |
| Screen stand | [case/screen_stand/](../case/screen_stand/README.md) | `python3 case/screen_stand/make_3mf.py` (1 h 09 min, 5.6 g) |
| Front sonar head | [case/sonar_front/](../case/sonar_front/README.md) | `python3 case/sonar_front/make_3mf.py` (37 min, 8.6 g, no support) |

## 3. Flash the LILYGO

Build the **`lilygo`** target and upload it over USB-C. Follow [firmware/README.md → Flashing](../firmware/README.md#flashing). Every later update can go [over Wi-Fi](USER-GUIDE.md#update-firmware-over-wi-fi-ota).

## 4. Wire

Follow the **[wiring guide](../firmware/WIRING.md)**. It has photos of the real pins. Keep the **[one-page wiring card](images/wiring-quick-reference.svg)** next to the robot.

| Lead | LILYGO | Goes to |
|---|---|---|
| A | `3V` | PCA `VCC` (3.3 V logic) |
| B | `G` | PCA `GND` |
| C | `18` | PCA `SDA` |
| D | `17` | PCA `SCL` |
| E | `1` | LED `DIN` |
| F | `5V` | PCA `V+` terminal (feeds the LILYGO from the servo supply) |
| Sonar, left | `10` / `11` | `Trig` / `Echo`; `VCC` to `3V`, `GND` to `G` |
| Sonar, right | `12` / `13` | Same |

- **Supply:** 5 V into the PCA `V+` / `GND` terminal, with the 1000 µF capacitor across it (long leg on `V+`).
- **USB-C:** unplug it while lead F is fitted.
- **Servos:** CH0/CH1 front-left hip/knee, CH2/CH3 front-right, CH4/CH5 rear-left, CH6/CH7 rear-right. Orange goes to `PWM`, red to `V+`, brown to `GND`. See [which servo goes where](USER-GUIDE.md#which-servo-goes-where).
- **`VCC` and `V+`:** `VCC` is 3.3 V logic and `V+` is the 5 V servo supply. Never join them.

## 5. Centre the servos before the legs go on

1. Plug the servos in with **no horns or legs on**.
2. Power up, open the crab's page, then tap **☰ → Ráp → Giữa thô · 1500 µs** (rough centre). Wait about 3 s.
3. Power off and fit each horn so that its leg will sit on the diagonal.

Details: [first power and centring](../firmware/WIRING.md#first-power-and-centring).

## 6. Assemble

1. **Hip servos.** Pass each plug down through an open bay, then screw each servo through its two tabs onto the frame saddles. Use the screws that come with the servo, and do not drill the tabs.
2. **Legs.** Fit the thighs and feet onto the knee servos and horns at the centred position. Leave a loop of knee lead, at least 40 mm, so the leg can swing.
3. **Electronics.**
   - Seat the PCA9685 and the wiring on the frame, away from the LILYGO's antenna end.
   - Hold loose bundles with tape or ties. The bundle in the photos is about 45 mm tall.
4. **Screen stand.** Snap it onto the raised rim on the front (+Y) side of `frame_upper`. Drop the LILYGO in, screen forward, and loop a rubber band over the two back posts.
5. **Sonar head.**
   1. Push both modules in from behind, header down. Screw or glue them.
   2. Zip-tie the plate to the front (+Y) side rail under the screen.
   3. Plug the left module into GPIO10/11 and the right one into 12/13. To check, cover one sensor and watch which reading on the drive page changes.
6. **Hand check.** With the power off, move each joint gently through its range. Nothing should bind or pull a wire.

The full CAD walkthrough, with the screw IDs and insertion steps, is in [case/README.md → Assembly order](../case/README.md#assembly-order). It was written for the future integrated board, so take the servo and leg steps from it.

## 7. Calibrate and drive

1. **☰ → Ráp → Tư thế đứng** (standing pose).
2. Trim each hip to an even diagonal and each knee until all four feet touch the floor and the body is level.
3. Tap **Lưu tâm** (save centres), then **Xong ráp** (done). See [Calibration](USER-GUIDE.md#calibration-ráp).
4. Optional: restore a saved settings file with `tools/firmware/restore_settings.py`. See [Saving and restoring settings](USER-GUIDE.md#saving-and-restoring-settings).
5. Put the crab on the floor and [drive it](USER-GUIDE.md#open-the-controls), then try [🤖 Tự đi](USER-GUIDE.md#tự-đi-auto-mode).

If it walks backwards, see the `FRONT_IS_CH46` note under [which servo goes where](USER-GUIDE.md#which-servo-goes-where). If it resets while walking, the supply is sagging: see [known issues](USER-GUIDE.md#known-issues).

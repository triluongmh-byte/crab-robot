# Battery power and self-driving parts

**Status, 2026-11-14:**
- **Auto mode (Tự đi) is in the firmware** from `positional180-v22`. It waits for the two ultrasonic sensors from round 1. Without them the button stays greyed out.
- **The battery (round 2) is a plan.** Nothing in this round has been bought or fitted yet.

The robot still runs on the [two-port USB power bank wiring](WIRING.md#2-connect-power--two-different-pca-labels).

[Back to wiring](WIRING.md) · [Back to README](../README.md)

The parts come in **two buying rounds**:

1. **Round 1** is what turns the toy into a robot, for under 100k VND.
2. **Round 2** is a power kit that only works as a whole, so it is bought in one go.

## Round 1: sensors, about 75–95k VND

| Part | Qty | Notes |
|---|---|---|
| **HC-SR04P** (or RCWL-1601) ultrasonic module | 2 | 3.3 V parts. Skip the 5 V SRF04 / HC-SR04. Two at the front are enough; see below |
| **1000 µF electrolytic capacitor**, 10 V or more | 1–3 | Across PCA `V+`/`GND`. It softens the brownouts with the current power bank too. Long leg +, striped side − |

With round 1 fitted, Auto mode runs on the power bank as it is now. It still has the trailing USB cable, and brownouts become rarer but do not go away.

### Why two sensors and not four

- **Auto mode mostly walks forward and turns** (↖ ↗ arcs). Two sensors angled about 25° left and right see what is ahead and which side is freer.
- **Reversing is short and blind.** The robot backs off for 1.5 s along ground it has just crossed.
- **Four sensors would take 8 of the 9 free header GPIOs.** That leaves nothing for battery sense or a speaker, and the round of pings gets twice as slow.

For safer reversing, a third sensor can go at the back later. For table edges, the better buy is a **VL53L0X** pointing down. It shares the PCA's I²C bus, so it needs no GPIO.

### Wiring the sensors

| Sensor | VCC | GND | TRIG | ECHO |
|---|---|---|---|---|
| Front left | LILYGO `3V` | `G` | GPIO10 | GPIO11 |
| Front right | LILYGO `3V` | `G` | GPIO12 | GPIO13 |

- **Mounting.** Fit both on the front of the body (the Tiến side), angled about 25° outwards, eyes level and clear of the legs' swing.
- **A 5 V HC-SR04 instead of the P version** needs 5 V on VCC and a 1k (series) / 2k (to GND) divider on ECHO. The ESP32-S3 cannot take a 5 V ECHO.
- **Pull-downs.** The firmware sets ECHO with a pull-down. An unplugged sensor never answers, so **Tự đi** stays greyed out and the page says **Chưa thấy cảm biến siêu âm**.

### How Auto mode behaves

| It sees | It does | Eyes |
|---|---|---|
| Nothing within 45 cm | Walks forward (**Tiến**) | Happy, bouncing |
| One side nearer than 45 cm | Veers away (↗ or ↖) while walking forward | Looking the way it goes |
| Anything nearer than 25 cm | Stops for 0.6 s | **Surprised** |
| …then | Backs off 1.5 s, swinging its nose to the freer side, then arcs that way for 1.4 s | Normal |
| Clear road for a while | Every 8–16 s it wanders off in an arc, or stands still and looks around | Idle glances |
| 5 obstacles in a row without 4 s of clear walking | Gives up and stands: **Kẹt rồi, nhờ giúp** | **Sad** |
| A sensor goes silent for 0.7 s | Stops: **Mất cảm biến siêu âm** | **Sad** |

Rules that keep it safe:
- **It never starts by itself.** Boot, a brownout reset and every reboot come up in Manual.
- **Back to Manual on any of these:**
  - **DỪNG**
  - any drive button
  - an emotion from `/emo`
  - **Ráp**
  - holding **BOOT**
  - opening the page on another phone (a new page session)
- **A stalled loop stops the crab.** The firmware drives Auto through the same 0.5 s deadman as the web page, so if the loop hangs, the crab stops and Auto ends.
- **The phone does not have to stay awake.** Locking the phone, switching apps or opening the ☰ menu does not stop Tự đi; only DỪNG does.

The distances live in `firmware/crab/config.h` (`AUTO_STOP_CM`, `AUTO_SLOW_CM`, timings). They are first guesses and still need tuning on the floor.

## Round 2: battery power, about 600k VND

**Buy all of these together.** A LiPo without the balance charger, the UBEC or the battery-sense resistors is useless or unsafe.

| Part | Notes |
|---|---|
| 2S LiPo 7.4 V 1500 mAh 30C, **15 × 35 × 72 mm**, T-plug | Chosen pack. It fits the power bank's slot (100 × 65 × 15 mm, case D5) with 30 mm spare beside it |
| B3 balance charger (2S/3S) | Charges through the white balance lead. It stays on the table, not on the crab |
| UBEC 5 A (2–6S), **jumper on 5 V** | Servo branch. 6 V would overdrive the WS2812 lamp on the same rail |
| LM2596 adjustable buck | Logic branch. **Set it to 5.0 V with a multimeter before connecting it** |
| T-plug lead pair (male + female, 16 AWG) | Do not cut the battery leads: cutting both wires at once shorts the pack |
| Rocker switch 6 A | In the red lead, after the T-plug. Needs a ~21 × 15 mm cut-out in the body |
| 100k + 33k resistors | Battery-sense divider |

Do not use a 1S 3.7 V pack or a single 18650 for the servos. SG90 servos need 4.8–6 V; at 3.0–4.2 V they are weak and the brownouts get worse.

### Planned power wiring

```text
2S LiPo 7.4V ─T-plug─ switch ─┬── UBEC 5 V, ≥3 A ───► PCA9685 V+ (8 servos) + LED 5V
                              │                       └ 1000 µF across V+/GND, at the PCA
                              ├── LM2596 5.0 V ─────► LILYGO header "5V"
                              └── 100k / 33k ───────► LILYGO GPIO2 (battery sense, ADC1)
All GNDs common: battery −, UBEC −, buck −, LILYGO G/GND, PCA GND.
```

**Fitting it in the body:**
- The pack slides into the power bank slot, held by the existing strap.
- A piece of foam behind it stops it sliding, because it is 28 mm shorter than the slot.
- The UBEC and LM2596 sit in the 30 mm gap beside the pack. The LM2596 is about 14 mm tall in a 15 mm slot, so set its voltage before fitting it.
- Leave the T-plug and the balance lead at the front so the pack can come out for charging.
- Never squeeze the pack. If it swells, stop using it.

### Powering the LILYGO without USB

The LM2596 has no USB socket, so it feeds the LILYGO's **header `5V` pin** and **`G`/`GND`**.

The LILYGO schematic (`engineering/sources/schematic.txt`) shows the path:
- USB-C VBUS → 2 A fuse → the `+5V` net.
- The header `5V` pin is on that `+5V` net.
- `+5V` feeds the AP2112K 3.3 V LDO.

Feeding the `5V` pin is therefore the same as powering the board by USB.

1. **Set the buck to 5.0–5.1 V with a multimeter before connecting it.** Adjustable modules ship at arbitrary voltages; 9–12 V on that pin destroys the board.
2. **Never have the battery switched on while a computer USB cable is plugged in.** The header `5V` pin and USB VBUS are joined through the fuse only, with no blocking diode, so the battery would feed the computer's port. To flash: switch the battery off first, then plug in USB. This joins the existing rule of removing servo power before reset or flashing.
3. **Never feed the `3V` pin.** That bypasses the LDO.

### Battery sense (firmware still to do)

The 100k (top) / 33k (bottom) divider maps 8.4 V full charge to about 2.08 V at GPIO2. GPIO2 is on ADC1, which still works while Wi-Fi is on.

Planned behaviour, which needs the round 2 parts:
- At about 3.5 V per cell (7.0 V pack) the crab stops walking and ends Auto with sleepy, "hungry" eyes.
- Below that level the servos do not arm.

## Pin budget

The current build uses GPIO 17 and 18 (I²C), 1 (LED) and 21 (PCA OE). The header GPIOs still free are 2, 3, 10, 11, 12, 13, 16, 43 and 44.

| Use | GPIO | Status |
|---|---|---|
| Ultrasonic left TRIG / ECHO | 10 / 11 | In firmware v22 |
| Ultrasonic right TRIG / ECHO | 12 / 13 | In firmware v22 |
| Battery sense | 2 | Round 2 |
| Speaker (MAX98357A BCLK / LRC / DIN) | 16 / 43 / 44 | Later |
| Spare | 3 | |

## Later

- **Speaker.** A MAX98357A + 8 Ω speaker for robot chirps.
- **Camera.** A XIAO ESP32S3 Sense (camera + mic) streaming MJPEG into the control page. Power it from the logic branch.
- **Voice.** The phone is the brain: speech recognition → Claude API with tools (walk, emote, eyes) → speech out. The API key never goes into the firmware or the crab's web page.

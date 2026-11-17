# Battery power and self-driving parts

**Status, 2026-11-17:**
- **Auto mode (Tự đi) is in the firmware** from `positional180-v22`. Since v32 it also has a radar page (`/radar`) with live stop/veer thresholds and a log.
- **Round 1 is bought:** both HC-SR04P modules and the 1000 µF capacitors. The front sonar head (`case/sonar_front`) is being printed.
- **Round 2 changed:** the owner reuses **two 18650 cells in series (2S)** instead of buying the LiPo, plus a 2S balancing BMS. Already bought: the LM2596 and the rocker switches. Still to buy: see the table below.

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

- **Auto mode mostly walks forward and turns** (↖ ↗ arcs). Two sensors turned 12° left and right (the V head in `case/sonar_front`) see what is ahead and which side is freer.
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

## Round 2: battery power (2× 18650, 2S)

The owner reuses two 18650 cells (owner, 2026-11-17) instead of buying the 2S LiPo. This saves about 150k VND.
- The pack voltage is the same: 7.4 V nominal, 8.4 V full, so everything downstream is unchanged, including the battery-sense divider.
- With 2500 mAh cells it holds about 18 Wh, against 11 Wh for the LiPo 1500.
- It weighs about 90 g, against 80 g for the LiPo.
- Do not use three cells (3S, 12.6 V). That adds about 45 g for 8 small servos to carry, and the divider would have to change to 100k / 22k.

### Parts

| Part | Status | Notes |
|---|---|---|
| 2× 18650 Li-ion cell | **Owner has them** (reused) | Same type and age. Measure each one and discard any below 2.5 V, dented, leaking or getting hot. When full, they should be within 0.05 V of each other |
| BMS 2S **with balancing**, "7.4V 20A Cân bằng" | To buy (~42k) | **Not the 4A version:** servo peaks would trip it and drop power. Balancing keeps both cells at the same voltage |
| Li-ion charger **8.4 V 1 A** (CC/CV, red/green LED) | To buy (~50–70k) | Plugs into the BMS P+/P−. A plain 8.4 V adapter does not limit the current, so do not use one |
| Nickel strip spot-weld, or a 2-cell holder | To do (~10–20k at a shop) | A shop spot-welds the two cells into one block with 3 leads (−, middle, +). **Never solder directly onto an 18650.** Spring holders can lose contact while the crab walks |
| UBEC 5 A (2–6S), **jumper on 5 V** | To buy (~130k) | Servo branch. 6 V would overdrive the WS2812 lamp on the same rail |
| LM2596 adjustable buck | **Bought** | Logic branch. **Set it to 5.0 V with a multimeter before connecting it** |
| T-plug lead pair (male + female, 16 AWG) | To buy (~35k) | The pack comes off for charging without unsoldering |
| Rocker switch 6 A (3-pin) | **Bought** (5 pcs) | Use the middle pin and one outer pin, in the + lead after the BMS |
| 1000 µF 16 V capacitor | **Bought** (4 pcs) | Across PCA `V+`/`GND`. Long leg +, striped side − |
| 100k + 33k resistors | To buy (a few hundred đồng) | Battery-sense divider. Optional: the crab runs without it, but it cannot tell when the pack is low |

No longer needed: the 2S LiPo 1500 mAh and the B3 balance charger.

Do not use a 1S 3.7 V pack or a single 18650 for the servos. SG90 servos need 4.8–6 V; at 3.0–4.2 V they are weak and the brownouts get worse.

### Why both a UBEC and the LM2596

The pack and the switch are shared, and the line splits into two branches after the switch.

| Load | Current | Fed by |
|---|---|---|
| 8 servos + lamp | 3–4 A at the peaks | UBEC 5 A |
| LILYGO + sonars | about 0.5 A | LM2596 |

- The LM2596 is rated 3 A but gets hot above about 2 A, so it cannot carry the servos.
- Splitting the branches keeps servo current spikes from resetting the board, which is the old brownout.
- At its peak the whole crab draws about 4 A from the pack. The BMS is rated 20 A and 18650 cells give 5–10 A.
- Expected run time is about 1.5–2 h, depending on the cells.

### Planned power wiring

```text
cell 1 −  ─────────────► BMS B− (0V)
cell 1 + / cell 2 − ───► BMS BM (4.2V, balance)
cell 2 +  ─────────────► BMS B+ (8.4V)

BMS P+ ─T-plug─ switch ─┬── UBEC 5 V, 5 A ───► PCA9685 V+ (8 servos) + LED 5V
                        │                      └ 1000 µF across V+/GND, at the PCA
                        ├── LM2596 5.0 V ────► LILYGO header "5V"
                        └── 100k / 33k ──────► LILYGO GPIO2 (battery sense, ADC1)
BMS P− = common GND: UBEC −, buck −, LILYGO G/GND, PCA GND.
Charger 8.4 V Li-ion ──► BMS P+ / P− (switch off while charging).
```

The PCA's other supply pin, **VCC** (3.3 V logic), stays wired to the LILYGO as it is now.

Pad names vary between BMS boards. Check the back of the board before soldering.

### Fitting it in the body (to design)

The two cells side by side make a block of about 37 × 65 × 18.5 mm.
- That is thicker than the old power bank slot (15 mm), and the owner runs frame_upper only.
- Where the pack goes, and a holder for it, still has to be designed once the cells are welded.
- The UBEC and LM2596 go next to it. Set the LM2596 to 5.0 V before fitting it.
- Leave the T-plug reachable so the pack can come off for charging.

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

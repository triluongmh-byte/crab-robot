# Battery power and self-driving parts (plan)

**Status: plan, parts not bought or fitted yet (2026-11-14).** Nothing here is in the firmware yet. The current robot still uses the [two-port USB power bank wiring](WIRING.md#2-connect-power--two-different-pca-labels). This page records what to buy and how it will be wired, so the parts fit the pins the firmware will use.

[Back to wiring](WIRING.md) · [Back to README](../README.md)

## Why change the power

The power bank's servo port sags under walking load, and that causes brownouts. A self-driving robot that resets mid-walk is worse than a remote-control one. Power is step 0, before sensors or the Auto mode.

**Do not use a 1S 3.7 V LiPo for the servos.** SG90 servos need 4.8–6 V. At 3.0–4.2 V they are weak and jittery, and the brownouts get worse.

## Planned power wiring

Use one 2S LiPo (7.4 V nominal, 1000–1500 mAh) split into two branches. The servo branch and the logic branch each get their own regulator, so a servo current spike cannot pull the ESP32 down.

```text
2S LiPo 7.4V ──┬── switch ──┬── UBEC 5–6 V, ≥3 A ───► PCA9685 V+ (8 servos) + LED 5V
               │            │                         └ 1000 µF 10 V across V+/GND, at the PCA
               │            └── buck 5.0 V, ≥1 A ───► LILYGO header "5V" (+ camera board later)
               └── 100k / 33k divider ──► LILYGO GPIO2 (battery sense, ADC1)
All GNDs common: battery −, UBEC −, buck −, LILYGO G/GND, PCA GND.
```

A 2S 1000 mAh pack weighs about 60–80 g, which is lighter than the 120 g power bank. Charge it only with a 2S balance charger.

### Powering the LILYGO without USB

A buck module without a USB socket feeds the LILYGO through its **header `5V` pin** and **`G`/`GND`**.

The LILYGO schematic (`engineering/sources/schematic.txt`) shows how this works:
- USB-C VBUS → 2 A fuse → the `+5V` net.
- The header `5V` pin is on that `+5V` net.
- `+5V` feeds the AP2112K 3.3 V LDO for the ESP32.

So feeding the `5V` pin is the same as powering the board by USB.

Three rules:

1. **Set the buck to 5.0–5.1 V with a multimeter before connecting it.** Adjustable modules such as the LM2596 or MP1584 ship at arbitrary voltages, and 9–12 V on that pin destroys the board.
2. **Never have the battery switch on and a computer USB cable plugged in at the same time.** Between the header `5V` pin and the USB port there is only the fuse, with no blocking diode, so battery current flows back into the computer's port. To flash: switch the battery off first, then plug in USB. This joins the existing rule of removing servo power before reset or flashing.
3. **Never feed the `3V` pin.** That bypasses the LDO, and a small overshoot kills the ESP32.

### Battery sense

A 100k (top) / 33k (bottom) divider maps 8.4 V full charge to about 2.08 V at GPIO2. GPIO2 is on ADC1, which still works while Wi-Fi is on.

The planned firmware behaviour, not built yet:
- Stop walking and show sleepy, "hungry" eyes at about 3.5 V per cell (7.0 V pack).
- Refuse to arm the servos below that level.

## Planned sensors

Two ultrasonic sensors at the front, angled about 25° left and right, so the robot knows which side is freer.

Prefer the **HC-SR04P** or **RCWL-1601**, which run at 3.3 V. A 5 V SRF04 or HC-SR04 drives ECHO at 5 V, which the ESP32-S3 cannot take. If you use one, put a 1k (series) / 2k (to GND) divider on ECHO.

| Sensor | VCC | TRIG | ECHO |
|---|---|---|---|
| Left | LILYGO `3V` (3.3 V part) | GPIO10 | GPIO11 |
| Right | LILYGO `3V` (3.3 V part) | GPIO12 | GPIO13 |

The firmware will fire the two sensors alternately so they do not hear each other, and take the median of three readings because the body bounces while walking. Soft things such as curtains and sofas absorb the sound and read badly.

A forward-looking sensor cannot see a table edge. An optional **VL53L0X** time-of-flight sensor pointing down can share the PCA's I²C bus (GPIO18 SDA, GPIO17 SCL) to catch drops.

## Pin budget

The current build uses GPIO 17 and 18 (I²C), 1 (LED) and 21 (PCA OE). The header GPIOs still free are 2, 3, 10, 11, 12, 13, 16, 43 and 44.

| Use | GPIO |
|---|---|
| Battery sense | 2 |
| Ultrasonic left TRIG / ECHO | 10 / 11 |
| Ultrasonic right TRIG / ECHO | 12 / 13 |
| Speaker (MAX98357A BCLK / LRC / DIN), later | 16 / 43 / 44 |
| Spare | 3 |

## Shopping list

| Part | Notes |
|---|---|
| 2S LiPo 7.4 V, 1000–1500 mAh | With a JST or XT30 lead; check the size fits the body |
| 2S balance charger | Never charge a LiPo unattended |
| UBEC 5 V (or 6 V), ≥3 A | Servo branch |
| Buck 5 V, ≥1 A | Logic branch. A USB-socket version is optional; the header `5V` pin works |
| 1000 µF 10 V capacitor | Across PCA V+/GND |
| Switch | In the battery lead |
| 2 × HC-SR04P (or RCWL-1601) | 3.3 V parts; skip the 5 V SRF04 |
| Later: MAX98357A + 8 Ω speaker | Robot sounds |
| Later: XIAO ESP32S3 Sense | Camera and mic, streams to the phone over its own Wi-Fi |
| Optional: VL53L0X | Table-edge detection on I²C |

## Order of work

0. Power: 2S pack, UBEC, buck, battery sense.
1. Two ultrasonic sensors and **Auto mode**. Auto is a state machine, no ML model:
   - Wander until something is closer than about 25 cm.
   - Then stop with surprised eyes, back off, scan, and arc toward the freer side.
   - The web UI gets a Manual/Auto toggle and a STOP button. Any manual drive command returns to Manual.
2. Speaker for robot sounds.
3. Camera board streaming MJPEG into the control page.
4. Voice: the phone is the brain. Speech recognition → Claude API with tools (walk, emote, eyes) → speech out. The API key never goes into the firmware or the crab's web page.

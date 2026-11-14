# Driving and servo command log

On desktop, Forward/Backward/Left/Right and Stop stay on the left. The right sidebar scrolls independently and contains status, enable/disable, speed, lights, Wi-Fi, assembly and the servo table. Its contents can grow without moving the driving buttons. On mobile, only the driving pad and compact readiness indicator remain visible; tap **☰** for the sidebar. Opening it stops any held direction. Close it with ☰, the backdrop or Escape.

Hold a direction to move; release, cancellation, focus loss or a lost connection stops the command. Assembly still locks driving until **Xong ráp**. The first enable takes about3seconds. The sidebar's **Dáng đi** selector chooses the diagonal trot (default) or the owner's front/rear pairs; changing it stops walking, like speed; the servos stay enabled.

## What the servo table means

| Column | Meaning |
|---|---|
| CH / joint | Existing channel mapping, CH0–CH7 |
| Góc | Nominal angle of the emitted command, about the90° centre, after mirror/trim/limits/slew |
| Xung µs | Last pulse width requested and acknowledged by the PCA driver |
| PWM |12-bit count written to PCA9685; quantization means its nominal pulse differs slightly from the requested width |
| Tắt xung / Chưa xác nhận | Disabled or no acknowledged state; angle and pulse cells show — |

The SG90 connections provide no position feedback. These values do not measure actual shaft angle, force, foot contact or XYZ position. They use the existing unmeasured pulse-to-degree assumption. They are useful for checking which channels the firmware commands and whether left/right or front/rear pairs follow the expected sequence.

The read-only `/api/servos` response marks `kind: commanded` and `feedback: false`. The driver records values only after acknowledged writes; a failed off attempt marks the state unknown. Reading telemetry performs no I²C transactions or motor commands. The table updates twice per second while the sidebar is visible; closing the mobile menu pauses those requests. Status history stores only the latest30 entries in browser memory and is cleared when the page reloads. Passwords are not logged.

## Validation

Host driver tests compare snapshots to actual PCA writes, including disable/failure states; HTTP tests check null inactive/unknown fields and that reading does not arm or write. The shipped-script tests cover the four buttons, menu stop/close, telemetry and lost connections. Optional isolated Chromium tests hold real browser touch/mouse input across a long status update, compare button rectangles, and check independent sidebar scrolling at1280×800,390×844,320×568 and700×390. This does not claim a physical iPhone/Safari or floor-walking test.

With Playwright supplied separately and an installed Chromium/Chrome executable, run:

```sh
PLAYWRIGHT_MODULE=/path/to/playwright \
CRAB_TEST_CHROME=/path/to/chrome \
node firmware/tests/test_layout.js /private/tmp/crab-layout-results
```

The test uses a fresh headless profile and mocked API routes; it never calls the robot or uses an existing browser profile. The repository build installs no browser dependencies.


**2026-11-14 (`positional180-v22`):** a **🤖 Tự đi** (Auto) button sits above the pad. It is enabled when both front ultrasonic sensors answer and the servos are armed. **DỪNG** or any drive button returns to Manual. Leaving the page, phone sleep and the ☰ menu only release a held button and no longer send a stop on their own, so Auto keeps walking. See [BATTERY-AUTONOMY.md](BATTERY-AUTONOMY.md).

**2026-11-14 (`positional180-v21`):** the pad has eight buttons. The four corners walk forward or back while turning the body (↖ ↗ ↙ ↘, `dir` 5–8). The Wi-Fi password field is plain text, and **Tìm Wi-Fi** fills the name from the first network found.

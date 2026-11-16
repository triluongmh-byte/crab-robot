# Crab firmware —180° positional release

This release is for the owner's replacement **positional180° SG90-class servos**. On November13 the owner reports movement from the replacement180° motors, but finds it too slow. Their current power state and physical calibration are unconfirmed. The earlier360° experiments failed loaded tests and are [archived as unsuccessful](EXPERIMENT-STATUS.md).

**Current behavior:** since `positional180-v13` the servos arm automatically at boot (`cfg::AUTO_ARM`), eight channels 300 ms apart; keep hands clear when plugging in. (Older text below describing PWM off at boot is history.) Saved Wi-Fi/direct AP and capped-brightness LEDs remain available. Use **Bật servo180°** to enable channels one at a time,300ms apart; approximately3seconds enables all eight. The left driving panel then offers Forward, Backward, Left and Right; settings and logs live in the right panel, hidden behind ☰ on mobile. **Ngắt servo** disables every output. The default gait is the diagonal trot and the default speed is **Bình thường**: about 1.23 seconds per cycle; **Chậm** is 2.0 seconds and **Nhanh** is 0.8 second. Releasing a direction or missing its heartbeat500ms stops walking and settles gently towards standing; it does not disconnect the servo supply.

The360°/single-servo speed-test pages and HTTP routes are removed from this release. The unknown actuator value is retained only as the explicit PWM-off state and cannot start the old hips-only/timed gait. Historical helper sources remain in the repository, but the final actuator output boundary emits only positional pulses.

Start with the [tomorrow setup steps](POSITIONAL180.md). The screen/web UI remain Vietnamese, work directly on the crab's own Wi-Fi and use no cloud or downloaded browser dependencies.

## Choose the correct target

| Hardware | Target | Complete image directory |
|---|---|---|
| Original LILYGO T-Display-S3 non-touch + external PCA9685 | `lilygo` | `build/firmware/esp32/` |
| Custom ESP32-S3-WROOM-1-N16R8 + PCA9685 PCB, Waveshare 23822 LCD | `integrated` | `build/firmware/integrated/` |

Run the repository-root `./build.sh` to build and check both. To compile one target after its source dependencies are prepared:

```sh
python3 tools/firmware/build.py --target lilygo
```

The recipes are [flash.json](flash.json) and [flash-integrated.json](flash-integrated.json). Do not interchange images. The integrated board uses SPI SCLK8/MOSI39, CS6/DC7/RES5/BL38 and PCA OE GPIO21; GPIO15 is NC. LILYGO retains its parallel display and LCD power GPIO15. Both use SDA18/SCL17, LED GPIO1 and BOOT GPIO0. See [hardware.h](crab/hardware.h), [config.h](crab/config.h) and [wiring](WIRING.md).

## Flashing

For this owner's original LILYGO, standing update permission and the required verified local recovery procedure are recorded in [FLASH-POLICY.md](FLASH-POLICY.md). It does not authorize the new custom PCB or motor operation.

Follow the English [integrated flashing guide](../docs/INTEGRATED-FIRMWARE.md) for the future custom PCB, after professional assembly inspection. It has not been flashed or run on manufactured hardware.

For the currently owned LILYGO, remove all servo plugs from the PCA9685 and disconnect its servo V+ input. Connect only the LILYGO to the computer with a USB data cable. Do not use the photographed unidentified cell/module setup as a verified servo supply. Choose the actual LILYGO serial port, then run:

```sh
arduino-cli upload \
  --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,PSRAM=opi,DebugLevel=none' \
  --port YOUR_LILYGO_PORT \
  --input-dir build/firmware/esp32 firmware/crab
```

If necessary, hold BOOT, press/release RESET, then release BOOT to enter the downloader. Upload the complete built image set; do not write the application binary alone at address zero. No build/check command flashes or moves hardware.

## Direct connection and setup

Join `CuaRobot-XXXX`, keep the connection without internet and open **http://192.168.4.1/**. Optional home Wi-Fi remains under **Wi-Fi**; successful setup saves credentials. Keep BOOT pressed for about8seconds while the app runs to forget Wi-Fi. The new trim store is separate (`cua-180-v1`) so old experiment-era trims are not silently reused. Wi-Fi is retained in its existing store.

Open **Ráp** for unloaded centring, horn alignment and small trims; it locks walking until **Xong ráp**. **Giữa thô** requests nominal1500µs; **Tư thế đứng** reapplies saved trims. Always remove servo power before changing plugs or fastening horns, and do not mix old continuous motors into the replacement set.

## Conservative angle assumptions

GPIO assignments and PCA nominal50Hz configuration are unchanged. The nominal mapping now assumes1000µs across180° (about5.556µs/degree), centred at1500µs, as a deliberately small initial excursion. It is not a measured calibration. If the received unit spans180° over2000µs, actual excursions will be about half the nominal target. Pulse timing varies between brands and individual servos; [Adafruit describes calibration and the need to approach travel limits gradually](https://learn.adafruit.com/16-channel-pwm-servo-driver/using-the-adafruit-library).

The gait requests hip amplitude25° and knee lift30° nominal. Final mirror-plus-trim output is clamped symmetrically to±25° nominal on hips and±35° on knees, inside the owner's hand-reported30/60° hip and40° knee clearances. Trims are bounded to±12° nominal and cannot bypass the final clamp. Nominal slew is capped at180°/s (previously30°/s), and all eight joints receive one shared pose every20ms after startup (sequential I²C register writes, not an atomic hardware latch). Mirroring uses the existing mechanism's `cfg::SIGN`; actual mounting direction still needs the first unloaded bench check. Neither these bounds nor host tests prove collision-free loaded movement on the drilled body.

## Validation scope

Host core, actual PCA register output, real HTTP handlers and the shipped web script are checked for boot-off, explicit enable/disable, sequential startup,8 core directions and4 main UI buttons, release/deadman, raw centre/trim, post-trim pulse limits, removed360 routes and unchanged AP/QR/Wi-Fi behavior. The LILYGO target is the one to flash to the owned modules. Physical stopping, horn fit, power under load and stable walking remain unverified by this update.

The full repository CAD/source-build manual step remains documented in [BUILD-VALIDATION.md](../BUILD-VALIDATION.md); this firmware update does not change printed parts or the PCB.

## Normal-speed update —2026-11-13

The owner reports the previous setting is too slow and explicitly requests normal speed. The base gait period is now1second, default factor0.65, with the existing0.4/0.65/1 factors preserved. This changes tempo and joint slew only: pulse calibration, gait amplitudes, joint/trim limits, motor directions, sequential enable, BOOT/stop behavior, Wi-Fi and the `cua-180-v1` trim store are unchanged. The status version is `positional180-v2`. The larger software speed allowance is not a measurement of the delivered servo's physical speed or loaded walking.

## Stable hold and faster tempo —2026-11-13

The owner reports the page jumps during a held arrow and requests more speed. On narrow screens the direction pad and speed selector now stay fixed at the bottom, clear of scrolling content. Holding uses one captured pointer, prevents touch scrolling/text selection/long-press menus on the pad, ignores another finger's release, and stops on the owning finger's release, cancellation, capture loss or page exit. Polling avoids rewriting unchanged status text and direction-button attributes. Losing readiness still stops the held command.

The base period is0.65seconds with the existing0.4/0.65/1 factors: Slow1.625seconds, Normal1second, Fast0.65seconds per cycle. Nominal slew remains180°/s; angles, trims, output limits, enable/disable and500ms deadman are unchanged. Profile: `positional180-v3`. Host tests simulate hold renewal across polls and release paths. Actual phone touch behavior and physical speed still require the owner's check.

## Forward/back progress repair —2026-11-13

The owner reports moving legs without forward body progress. This is not evidence of swapped arrow labels. Release `positional180-v4` replaces the two-foot diagonal trot with a four-step crawl: FL, RR, FR, RL, recovering one foot at a time. Each recovery holds the hip while lifting, sweeps at full knee lift, and holds the hip again while lowering. Three other legs remain in nominal stance. All eight outputs sample a common pose every20ms; the previous round-robin output could leave joints sampled70ms apart. Startup still enables one channel every300ms. Nominal hip/knee amplitudes rise from12/15° to18/25°; final post-trim limits remain25/35°, with the same small pulse scaling, trim store, directions,180°/s slew and500ms deadman.

These changes address plausible timing/clearance causes; the physical cause is not proven without observing this robot. The fast step lasts0.65seconds per recovered leg; it is not a0.65second full four-leg cycle. See [crawl validation and the floor check](CRAWL.md). The owner's [TikTok reference](https://www.tiktok.com/@gocmaker.diy/video/7685032192547835157) was inspected in frame sequences: it mostly shows bobbing/leg motion in place, not an unambiguous forward/back demonstration. No servo variant, firmware or calibration is inferred from that clip.

## Owner-requested paired push —2026-11-13

The owner explicitly replaces the one-leg crawl with front and rear pairs. Front hips CH0/CH2 push backwards with knees CH1/CH3 down, then hold the hips while lifting both knees, return the hips forwards while raised, and hold the hips while lowering. Rear hips CH4/CH6 and knees CH5/CH7 follow the same sequence half a cycle later. Backward reverses only the hip translation; knee lifting is preserved. The first Forward pose starts the front hips at neutral so its first travel is towards the rear. The rear pair is phased into recovery while the front pair pushes.

At Fast each pair spends900ms pushing,225ms lifting,450ms returning and225ms lowering; the rear pair is offset900ms. Normal scales these times by1/0.65. Hip demand uses the full nominal±25° axial stroke, with30° knee lift and unchanged25°/35° final output limits after trim,180°/s slew and20ms shared frames. This increases stroke, not motor torque; the pulse-to-angle calibration and power under load remain unmeasured. Trim can clip an endpoint at the unchanged final limits.

This release is `positional180-v5`; [the trial guide](CRAWL.md) describes the current paired gait. It follows the owner's requested pairing rather than claiming three-foot support: at parts of the cycle only a front or rear pair is nominally grounded. That support line does not prove pitch balance or floor progress. Host tests cover the exact group/order, knee lift before hip return, Forward/Backward inversion, emitted pair pulses and final limits; physical walking still awaits the owner.

## Separate controls and servo command log —2026-11-13

The owner identifies the changing status block as the source of control movement and requests driving on the left, with logs/settings on the right and a hidden mobile menu. Release `positional180-v6` uses two independent scroll/layout regions. Only four main arrows and Stop remain on the driving pad. Status, enable/disable, speed, lights, Wi-Fi, assembly and telemetry are in the sidebar; ☰ opens it on narrow screens and stops a held command. Closing the menu restores focus without scrolling. The paired gait, limits, pins, timings and default-off behavior are unchanged.

`GET /api/servos` reports the last acknowledged PWM command for each channel, copied under the motion mutex and serialized after releasing it. It makes no I²C transactions and cannot arm or move the robot. Unknown or inactive channels return null angles/pulses. The UI labels nominal command angles about90°, requested pulse widths and PCA counts; these are not measured SG90 positions or XYZ coordinates. Polling is500ms while the sidebar is visible and paused while the mobile menu is closed. The status history is held only in browser memory. See [the web-control guide](WEB-CONTROL.md).

## Diagonal trot default —2026-11-13

Release `positional180-v7` makes a diagonal trot the default gait (FL+RR / FR+RL, stance 0.56, linear stance, about 12% four-foot overlap). The owner's front/rear pairs remain selectable from **Dáng đi** in the sidebar (`POST /api/gait` with `value=trot|pairs`; `GET /api/status` reports `gait`). Like speed, selecting a gait stops walking and briefly blanks the outputs; the servos stay enabled, resume standing on the next frame, and the choice resets to trot on reboot. Host simulation now also checks yaw: the trot is yaw-free in all directions, while pairs yaw during sideways moves, matching the rotation seen in the owner's video. A Fast-speed tracking test keeps every joint within 2.5° of its target under the 180°/s slew. Amplitudes, limits, trims, pins, signs, enable/deadman behaviour and speed factors are unchanged. See [the gait trial guide](CRAWL.md). Physical walking still awaits the owner.

## Faster servos —2026-11-13

The owner reports the trot works but moves too slowly. Release `positional180-v8` raises the joint slew limit from 180°/s to 450°/s and shortens the base cycle from 1.8 s to 1.0 s. Fast is now 1.0 s per cycle, Normal 1.54 s (was 2.77 s) and Slow 2.5 s (was 4.5 s). Every joint still tracks its target within 2.5° at Fast in host tests for both gaits; SG90 no-load speed is about 600°/s. Angles, limits, trims, gait shapes, pins and safety behaviour are unchanged. Faster moves draw more peak current from the power bank, so watch for PCA9685 or brown-out resets.

## Snappier servos and knee-flick trial —2026-11-13

Release `positional180-v9` raises the slew limit to 600°/s (about SG90 no-load speed) and shortens the base cycle to 0.8 s: Fast 0.8 s, Normal 1.23 s, Slow 2.0 s. Firmware cannot add torque; stronger joints need a higher supply voltage within the servo rating, or MG90S-class servos. A third **Dáng đi** option, **Búng gối** (`flick`), holds the hips with the front feet forward and rear feet back, and flicks the diagonal knees for Forward/Backward (Left/Right still trot). See [the gait trial guide](CRAWL.md). Host tests cover the flick pose, waveform direction, diagonal pairing and tracking at Fast.

## Emotion studio —2026-11-13

Release `positional180-v10` adds an emotion page at `/emo`, linked as **🎭 Cảm xúc** from the control page. It has built-in emotions, a keyframe editor with live preview, mirroring and LED colour, and emotions saved on the robot. The firmware gains a pose mode under the walking lease and deadman (`/api/pose`), RGB LED colour within the brightness cap (`/api/led`) and a bounded NVS list (`/api/emotions`). Releasing a pose relaxes to standing at 120°/s. See [EMOTIONS.md](EMOTIONS.md). Host tests cover pose timing, clamps, lease, deadman, relax, cancel and assembly blocking; endpoint validation; GRB colour; and the page's unit mapping, presets and playback timeline.

## Real front, 90° flick and speed slider — 2026-11-13

Release `positional180-v11` makes these changes:

- **Channel positions.** The owner found CH0 physically at the **rear right**. The firmware CAD frame (CH0 = front left) is treated as rotated 180° (`cfg::FRONT_IS_CH46`), so the real legs are:
  - CH0/1: rear right
  - CH2/3: rear left
  - CH4/5: front right
  - CH6/7: front left

  Drive commands are rotated into the CAD frame, so Forward now heads towards CH4/CH6. The calibration labels and the emotion page use these physical positions. CH0 is the owner's observation; CH2/4/6 follow from the 180° assumption.
- **Knee flick.** Hips go to 90° nominal; a 30–90° slider adjusts this live. The knee timing is set by each leg's geometry; see [CRAWL.md](CRAWL.md).
- **Speed.** Speed is a 20–100% slider, default 90%; the API accepts decimals 0.2–1.
- **Status panel.** The **Trạng thái** tab now lists firmware, PCA9685, servo, mode, gait, speed, light and Wi-Fi.
- **Arm button.** The greyed **Bật servo** button now reads "✅ Servo đang bật" when the servos are already on. That is why it was disabled.

## Wi-Fi drops fix — 2026-11-13

The owner reported that the page sometimes keeps loading. Pinging the robot showed 60% loss with up to 800 ms latency, while the LAN gateway showed 0% loss.

Release `positional180-v12` makes two changes:

- **Radio sleep.** Wi-Fi modem sleep is disabled (`WiFi.setSleep(false)`).
- **Status after a slow connect.** A saved-network attempt that was marked failed but then connected anyway is now adopted as online. Before, the robot kept the wrong status and called `WiFi.disconnect()` on the working link every 30 s.

## Auto-arm, heading trim, live emotion sliders — 2026-11-13

Release `positional180-v13` makes three changes.

**Auto-arm.** Servos now arm at boot (`cfg::AUTO_ARM`), at the owner's request. This replaces the earlier "PWM off at boot" policy. The arm path is the same as **Bật servo**: the eight channels come on 300 ms apart. **Ngắt servo** still turns all pulses off until the next arm or reboot.

**Bù lệch trái ↔ phải.** This slider trims heading, from −30% to +30%. It is saved on the robot (`/api/balance`, Preferences `balance`). At +N%:
- the physical right hips (CH0, CH4) get N% more stroke;
- the left hips (CH2, CH6) get N% less.

Use it when Forward drifts towards the slower side.

**Emotion sliders.** Moving a slider on `/emo` now starts live preview on its own. Before, the sliders only changed numbers until **Xem trực tiếp** was pressed.

## Higher knee lift — 2026-11-13

The owner reported that the feet scraped the table while the hips swung back, which pushed the robot backwards.

Release `positional180-v14` changes the knee lift:

- The default lift is now 45° nominal, up from 30°.
- A new **Độ nhấc gối** slider sets the lift from 20° to 60°. It is saved on the robot (`/api/knee`, Preferences `knee`) and applies to every gait.
- The knee output limit is now ±65° nominal.
- The trot lift at 100% speed still tracks within 2.5°.

## Calibration steps that actually move — 2026-11-13

The owner reported that the calibration buttons did nothing. The firmware was applying the trims (CH0 −3° read back as 1483 µs), but a 1° nominal step is about 5.6 µs. That is roughly one PCA9685 count, inside the SG90 deadband.

Release `positional180-v15` changes the calibration buttons:

- **Step size.** Each joint now has −3, −1, +1 and +3 buttons. A 3° step is at least 3 counts.
- **Range.** The trim range widens from ±12° to ±30° nominal.
- **No blanking.** A trim no longer blanks every PWM output, so the servos stop twitching on each press.

## Front flipped again — 2026-11-13

The owner turned the robot around. With v16, Forward/Backward and Left/Right were both reversed. Release `positional180-v17` sets `cfg::FRONT_IS_CH46=true` again, so the front is the CH4/CH6 end. The labels follow this layout:

| Leg | Hip | Knee |
|---|---|---|
| Rear right | CH0 | CH1 |
| Rear left | CH2 | CH3 |
| Front right | CH4 | CH5 |
| Front left | CH6 | CH7 |

The emotion page and the **Bù lệch** right side (CH0/CH4) also follow it. The setting is a single constant; flip it if the front changes again.

## Pet eyes, lamp colour, calibration names — 2026-11-13

Release `positional180-v18` makes three changes.

**Screen: pet eyes.** The screen shows two white eyes on black, drawn as shapes (`eyes.h`).
- Idle, they blink every 2.5–5.5 s and glance sideways now and then.
- While walking or performing an emotion, they become happy arcs.
- Wi-Fi status is one small line at the bottom.
- The QR join screen remains only for first setup, when no Wi-Fi is saved.
- Only black and white are used, so colour byte order cannot be wrong.

**Lamp colour.** A colour picker sits beside **Bật / tắt đèn**. The picked colour is saved on the robot (`/api/lightcolor`, Preferences `led`) and used whenever the lamp is on. Emotion colours (`/api/led`) stay temporary.

**Calibration names.** The calibration labels use the owner's names (CH6 = rear-right hip). These labels are independent of the Forward direction, which stays rotated by `FRONT_IS_CH46`.


## Emotion page leg names — 2026-11-13

In release `positional180-v19`, the emotion page sliders use the same leg names as the calibration menu: front left CH0/1, front right CH2/3, rear left CH4/5, rear right CH6/7. The owner reported that the previous mapping did not match the robot.

## Owner settings backup — 2026-11-13

`firmware/settings/owner-2026-11-13.json` records the tuned settings read from `/api/status` on v19:

- trims `[24,-18,-30,30,-18,30,27,-21]`
- speed 90%
- knee lift 35°
- heading trim +4
- flick hip 90°
- gait trot
- lamp `#ff0f0f`

Restore them after a reflash or erase with:

```sh
python3 tools/firmware/restore_settings.py firmware/settings/owner-2026-11-13.json --host <robot-ip>
```

Add `--dry-run` to list the requests without sending them. The robot keeps the trims, knee lift, heading trim and lamp colour across reboots. Speed, gait and flick hip are not saved on the robot: they reset to their defaults (90%, trot, 90°) at boot, which happen to equal these values.

## Screen status line fits one row — 2026-11-14

In release `positional180-v20`, the bottom line under the eyes always fits on one row. The owner's photos showed `Sai mật khẩu hoặc mất sóng  CuaRobot-XXXX 192.168…` cut off. The firmware now shows `message  address` when it fits, otherwise only the address (the part needed to reach the crab), otherwise only the message.

## Coloured eyes, moods, Wi-Fi join fix, QR guide, turning arcs — 2026-11-14

Release `positional180-v21`, for the owner's list of small issues:

- **Eye colour matches the lamp.** The eyes are drawn in the lamp's colour at full brightness: the saved lamp colour, or an emotion's colour while it plays. With the lamp off they are white. After an emotion ends, the lamp and the eyes go back to the saved colour about 1.5 s later.
- **Livelier eyes.** Nine moods: normal, happy, sad, angry, sleepy, surprised, love, asleep and wink.
  - Idle: blinks, sometimes double. Glances left, right, up and down move smoothly. Every 15–30 s there is a short smile, a wide-eyed look, a wink or a heart.
  - After 1 minute without a command the eyes get sleepy; after 3 minutes the crab sleeps ("z Z"). The next command wakes it with a short surprised look.
  - Walking: happy bouncing eyes that look towards the travel side.
  - Each built-in emotion on `/emo` has its own mood. Custom frames can pick one under **Mắt**.
- **Home Wi-Fi join fix (bug).** At home, the office Wi-Fi (saved) was not found, and `WiFi.status()` kept reporting `NO_SSID_AVAIL` from that attempt; Arduino-ESP32 2.0.14 does not reset it in `WiFi.begin()`. Pressing **Kết nối** then failed the new attempt on that stale value 0.5 s later and called `WiFi.disconnect()` on it.
  - Failures now come only from the current attempt's disconnect event: 201 means not found; 202, 15 and 204 mean a wrong password.
  - A router that a scan misses is scanned again for the whole 18 s attempt.
  - A wrong password is reported after one retry as **Sai mật khẩu Wi-Fi**. A network that never appears is reported as **Không thấy Wi-Fi này**.
- **Wi-Fi form.** The password is shown as plain text so typos are visible. After **Tìm Wi-Fi** the first network fills the name field. Both fields have phone autocapitalise and autocorrect turned off.
- **QR guide without Wi-Fi.** Whenever the crab is not on a Wi-Fi network and no phone is connected to its own Wi-Fi, the screen shows the join QR with three steps: scan the QR, open 192.168.4.1, choose the home Wi-Fi. The first connection attempt after boot still shows the eyes. Once a phone joins the crab's Wi-Fi, the eyes come back with the address on the bottom line.
- **Eight moves.** Four corner buttons turn the body while walking, like a car: ↖ forward-left, ↗ forward-right, ↙ back-left (the tail swings left) and ↘ back-right (`/api/move` `dir` 5–8).
  - Half of each hip stroke (`cfg::ARC_YAW`) turns the body.
  - In flick mode the arcs use the trot.
  - Changing between the 90° flick stance and the trot now ramps down first instead of whipping the hips across.

Host tests cover all of this: the stale-status regression, rescans, the wrong-password retry, the turn direction and travel of all four arcs in the equal-reach model, arc tracking at Fast, the flick-to-trot ramp, mood drawings, eye colour byte order, eye timing (wrap-safe), the QR guide text widths, the 8-button UI, the Wi-Fi form and emotion moods. The eye look direction assumes the screen faces outwards like a face (`cfg::EYE_LOOK_SIGN`). The colours on the real panel, the turn radius on the floor and the home Wi-Fi join still need the owner's eyes.

## Tự đi: Auto mode with two ultrasonic sensors — 2026-11-14

Release `positional180-v22`. The owner wanted a robot that walks by itself instead of a remote-control toy. Two HC-SR04P sensors at the front (left TRIG/ECHO GPIO10/11, right GPIO12/13; LILYGO target only) drive a small state machine in `crab/autopilot.h`. No ML model is involved. Parts and wiring are in [BATTERY-AUTONOMY.md](BATTERY-AUTONOMY.md) (round 1).

- **Sensors.**
  - Pings alternate left and right every 50 ms. Echo edges are timestamped in a GPIO interrupt, so the motion task's I²C frames cannot stretch a reading.
  - Each side keeps the median of its last three readings.
  - An echo beyond 250 cm, or one that never falls, counts as clear.
  - No rising edge at all means no sensor, and a side silent for 0.7 s ends Auto.
- **Behaviour.**
  - Cruise forward. Veer with ↗/↖ when one side is under 45 cm.
  - Under 25 cm: stop for 0.6 s with surprised eyes, back off 1.5 s swinging the nose towards the freer side (↙/↘), then arc that way for 1.4 s.
  - Every 8–16 s it wanders in an arc or stands and looks around.
  - Five obstacles without 4 s of clear walking in between: it stops with sad eyes and **Kẹt rồi, nhờ giúp**.
- **Safety.**
  - `Motion::autoDrive` refreshes the same 0.5 s deadman as the page.
  - `motion.autoMode` is cleared by any stop, manual command, pose, new page session, Ráp, inhibit or the deadman, and the autopilot follows it.
  - Boot always comes up in Manual. `/api/auto` needs the owner token, both sensors answering and all 8 servos armed outside Ráp.
- **Page.**
  - A **🤖 Tự đi** button above the pad shows the state and both distances.
  - **DỪNG** sends stop and ends Auto. Blur, phone sleep and the ☰ menu no longer send a stop unless a drive button is held, so Auto keeps going while the phone sleeps.
  - The **Trạng thái** tab lists the mode (**Lái**: Tay / Tự đi) and the sensor distances.
- **Status.** `/api/status` adds `autoSupported`, `auto`, `autoState` (`off`, `cruise`, `halt`, `backoff`, `turn`, `look`), `autoNote` and `sonarOk`, plus `sonar: [left, right]` in cm, or `null` when a side is silent (400 = clear).
- **Screen.** The bottom line shows **Đang tự đi**, or why Auto stopped, for 5 s.

Host tests cover all of this:
- the median filter, ping outcomes and staleness
- every autopilot transition, its turn directions, stuck, wander and lost sensor
- Motion takeover and the deadman
- the interrupt-timed driver, including alternation, out-of-range and an absent sensor
- `/api/auto` gating and status
- the page toggle, including that DỪNG ends Auto and blur, sleep and the menu do not
- the face-line widths

The thresholds are first guesses; tune them on the floor (`AUTO_*` in `config.h`).

## One gait, and no brownout boot loop — 2026-11-15

Release `positional180-v23`, from the owner's regrouped backlog:

- **Only the trot is left.** The owner found that only **Chéo** (diagonal trot) actually walks, so the front/rear pairs (v5) and knee-flick (v10–v11) gaits are removed.
  - Gone from the page: the **Dáng đi** selector and the **Góc hông búng** slider.
  - Gone from the API: `/api/gait` and `/api/flickhip` (now 404) and the `gait` / `flickHip` status fields.
  - This also closes the old backlog note that the heading trim had no effect in flick.
  - `tools/firmware/restore_settings.py` ignores `gait` and `flickHip` in older settings files.
  - The hip pulse limit stays at ±90° nominal so trims and emotion poses keep their range.
- **No brownout boot loop.** With weak servo power, arming all 8 servos sagged the supply, the ESP32 reset on brownout, armed again at boot and kept looping.
  - After a reset with `esp_reset_reason()==ESP_RST_BROWNOUT` the servos stay off.
  - The screen shows **Sụt áp: bấm Bật servo**. The page shows **Sụt áp**, explains why the servos are off, and lists **Khởi động: Sụt áp — servo chưa bật**. `/api/status` has `"brownoutHold":true`.
  - **Bật servo** arms as usual and clears the hold. A normal power-on or reset still arms by itself (`cfg::AUTO_ARM`).

Host tests cover the brownout hold and its release, the trot-only gait and tracking, the 404 routes, the page without the selector and the restore plan. The brownout path still needs a real sag on the robot to confirm.

## Firmware update over Wi-Fi (OTA) — 2026-11-16

Release `positional180-v24`. The owner wants the crab on battery without the USB cable, so firmware can now be updated from the control page.

- **How:** ☰ → **Trạng thái** → **Cập nhật firmware qua Wi-Fi**.
  1. **Hiện mã trên màn hình cua** shows a 6-digit code on the crab's screen for 2 minutes.
  2. Type the code.
  3. Pick the `crab.ino.bin` file (LILYGO build) and tap **Nạp firmware**.
  - The servos switch off and Tự đi ends while it writes. The crab restarts by itself. As after any normal start, the servos then arm by themselves.
- **Why a code on the screen:** the crab's own Wi-Fi is open and any page can take control. The code means only someone who can see the robot can replace its firmware. A wrong code burns it.
- **Safety:**
  - Every image carries `crab-ota-target=lilygo;`. A file without it (the integrated build, another project, or any firmware before v24) is refused before the boot slot switches.
  - A cut upload, a refused file or a power loss mid-write leaves the old firmware running, because the slot only switches at the end.
  - **Rollback:** the 2.0.14 bootloader has app rollback on. New firmware marks itself good after 20 s of running. If it resets before then (crash, boot loop), the bootloader goes back to the previous firmware. A brownout in those first 20 s also rolls back; just upload again.
  - USB flashing still works for recovery.
- **API:**
  - `POST /api/ota/begin` (`token`) starts the 2-minute code.
  - `POST /api/ota?token=…&pin=…` takes the multipart upload.
  - `/api/status` adds `otaPin`, `slot` (`app0`/`app1`), `target` and `otaMarker`.
- **USB flashing after an OTA:** the running app may then be in `app1` (`0x310000`), and `otadata` no longer matches `boot_app0.bin`. A USB script that verifies "the current firmware is vN at `0x10000`" will fail safely. Check `slot` in `/api/status` first, and verify the active slot.

Host tests cover:
- the marker scan across chunks
- the code: issue, expiry, a wrong guess burning it, and owner-only
- refusing a file for the wrong target
- a dropped upload and a write error
- a successful upload: exact bytes, slot switch, servos off, restart scheduled
- the page: the code step, input checks, the error shown, status polls paused during the upload, and the reload afterwards

## Lighter page and Wi-Fi signal — 2026-11-16

Release `positional180-v25`. On the office Wi-Fi the page kept spinning: pings to the crab lost 35–75% of packets while the router lost none, so its link was weak.

- **Gzip pages.** `/` and `/emo` are sent gzip-compressed: the control page goes from 27 KB to 10 KB, the emotion page from 16 KB to 6.5 KB.
  - `embed_assets.py` writes deterministic `*_GZ` arrays; `tools/firmware/test_embed_assets.py` checks that they decompress to the sources.
  - The app shrank by 26 KB.
- **Signal strength.** `/api/status` has `rssi` (dBm; `null` without home Wi-Fi). The page lists **Sóng Wi-Fi**:
  - −60 and above: mạnh
  - down to −70: khá
  - down to −80: yếu
  - below that: rất yếu, with a hint to move the battery and wires away from the antenna

## Hands-free updates from a computer — 2026-11-16

Release `positional180-v26`. The owner wants updates pushed straight from the computer, without anyone reading the screen.

- **PIN over the home Wi-Fi.** When `/api/ota/begin` arrives over the home or office Wi-Fi, the reply carries the PIN, so `tools/firmware/ota_push.py --host <ip> --bin …` runs with no human step.
  - That Wi-Fi has a password; the crab tells the two apart by which of its own addresses the request came in on.
  - Over the crab's own open Wi-Fi the PIN still only shows on the screen.
  - Anyone already on the home or office Wi-Fi who opens the page can therefore update the crab. The owner accepted that.
- **Servos stay off after an update.** A pushed update may come with nobody watching, so after the post-OTA restart the servos do not arm. The screen shows **Đã cập nhật: bấm Bật servo** and `/api/status` has `"updateHold":true`. **Bật servo** clears it.
  - An `RTC_NOINIT` flag set just before `ESP.restart()` tells this restart apart. A power-on, a reset or a crash rollback still arms as before; a brownout still holds.
- **`ota_push.py`:**
  - It uses the system `curl`, because on macOS 15 a Homebrew Python gets "No route to host" on the LAN (Local Network privacy).
  - It takes the PIN from the reply when it is there.
  - Otherwise it asks for it, or works in two steps with `--show-pin` and then `--pin`.

## PCA reconnect without reset — 2026-11-16

Release `positional180-v27`. Unplugging and re-plugging the PCA9685 used to leave **Lỗi dây** until a reset, because the driver was only probed at boot.

- While the driver is missing, the motion task probes it again every 2 s (`crab::driverProbeDue`, `DRIVER_PROBE_MS`).
- When the probe succeeds, the PCA comes back with the servos **off**. Tap **Bật servo** to move again.

## Speed is saved — 2026-11-16

Release `positional180-v28`. Every firmware update restarts the crab, and the walking speed came back at 90% each time. `/api/speed` now saves the value as a percent (`speed` in the `cua-180-v1` store), and boot restores it through `crab::savedSpeed`. A missing or out-of-range value gives the default.

## Higher knee lift and a new 👋 Chào — 2026-11-16

Release `positional180-v29`. The owner found that the knees can lift much higher than the firmware allowed.

- **Knee pulse limit:** `KNEE_PULSE_LIMIT` goes from 65 to 90 deg nominal (1000–2000 µs), the same as the hips.
  - On CH3/CH5 the ±30 trims used to eat the lift, so a 45° knee lift stopped at 35°. These knees now get the whole lift.
  - At the owner's current Nhấc gối of 35° the walk is unchanged.
- **Emotion poses:** a knee may lift up to `KNEE_LIFT_MAX` (60°). Pressing a knee down stays at 30°, and hips stay at ±30°.
  - The emotion editor's knee sliders go to 60.
- **👋 Chào:** CH3's knee lifts all the way and waves 60° ↔ 30° three times, then the crab stands again.

## Knee lift 100° in emotions, independent sliders — 2026-11-16

Release `positional180-v30`. The owner tested 60° in the emotion editor and nothing bound, then asked for 100°.

- **Higher lift in poses.** Poses may lift a knee up to `POSE_KNEE_LIFT` = 100° nominal.
  - The knee pulse limit is 130° nominal (1500 ± 722 µs), which leaves room for the ±30° trims and stays inside the SG90's 500–2500 µs.
  - Walking still lifts at most `KNEE_LIFT_MAX` (60°). Hips and knee press-down are unchanged.
- **👋 Chào:** CH3's knee goes to 100° and waves 100° ↔ 60°.
- **Sliders:** one slider now moves only its own joint. **Đối xứng trái/phải** starts unticked; before, it was ticked, so every slider also moved the opposite leg.

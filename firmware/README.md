# Crab firmware —180° positional release

This release is for the owner's replacement **positional180° SG90-class servos**. On November13 the owner reports movement from the replacement180° motors, but finds it too slow. Their current power state and physical calibration are unconfirmed. The earlier360° experiments failed loaded tests and are [archived as unsuccessful](EXPERIMENT-STATUS.md).

**Current behavior:** servo PWM is off at every boot. Saved Wi-Fi/direct AP and capped-brightness LEDs remain available. Use **Bật servo180°** to enable channels one at a time,300ms apart; approximately3seconds enables all eight. The left driving panel then offers Forward, Backward, Left and Right; settings and logs live in the right panel, hidden behind ☰ on mobile. **Ngắt servo** disables every output. The default speed is **Bình thường**: about2.77seconds per front/rear cycle; **Chậm** is4.5seconds and **Nhanh** is1.8seconds. Releasing a direction or missing its heartbeat500ms stops walking and settles gently towards standing; it does not disconnect the servo supply.

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

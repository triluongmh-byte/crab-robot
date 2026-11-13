# Crab firmware —180° positional release

This release is for the owner's replacement **positional180° SG90-class servos**. On November13 the owner reports movement from the replacement180° motors, but finds it too slow. Their current power state and physical calibration are unconfirmed. The earlier360° experiments failed loaded tests and are [archived as unsuccessful](EXPERIMENT-STATUS.md).

**Current behavior:** servo PWM is off at every boot. Saved Wi-Fi/direct AP and capped-brightness LEDs remain available. Use **Bật servo180°** to enable channels one at a time,300ms apart; approximately3seconds enables all eight. The main page then offers all eight directions. **Ngắt servo** disables every output. The default speed is **Bình thường**: about1.54seconds per cycle; **Chậm** is2.5seconds and **Nhanh** is1second. Releasing a direction or missing its heartbeat500ms stops walking and settles gently towards standing; it does not disconnect the servo supply.

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

The gait requests hip amplitude12° and knee lift15° nominal. Final mirror-plus-trim output is clamped symmetrically to±25° nominal on hips and±35° on knees, inside the owner's hand-reported30/60° hip and40° knee clearances. Trims are bounded to±12° nominal and cannot bypass the final clamp. Nominal slew is capped at180°/s (previously30°/s), and only one channel updates per10ms. Mirroring uses the existing mechanism's `cfg::SIGN`; actual mounting direction still needs the first unloaded bench check. Neither these bounds nor host tests prove collision-free loaded movement on the drilled body.

## Validation scope

Host core, actual PCA register output, real HTTP handlers and the shipped web script are checked for boot-off, explicit enable/disable, sequential startup,8directions, release/deadman, raw centre/trim, post-trim pulse limits, removed360 routes and unchanged AP/QR/Wi-Fi behavior. The LILYGO target is the one to flash to the owned modules. Physical stopping, horn fit, power under load and stable walking remain unverified by this update.

The full repository CAD/source-build manual step remains documented in [BUILD-VALIDATION.md](../BUILD-VALIDATION.md); this firmware update does not change printed parts or the PCB.

## Normal-speed update —2026-11-13

The owner reports the previous setting is too slow and explicitly requests normal speed. The base gait period is now1second, default factor0.65, with the existing0.4/0.65/1 factors preserved. This changes tempo and joint slew only: pulse calibration, gait amplitudes, joint/trim limits, motor directions, sequential enable, BOOT/stop behavior, Wi-Fi and the `cua-180-v1` trim store are unchanged. The status version is `positional180-v2`. The larger software speed allowance is not a measurement of the delivered servo's physical speed or loaded walking.

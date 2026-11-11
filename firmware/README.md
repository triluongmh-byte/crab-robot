# Crab firmware — two hardware targets

The application implements QR setup, nearby 2.4 GHz Wi-Fi selection, saved credentials, eight hold-to-move directions, a light switch and servo centring/trim controls. Everything is served by the robot; there are no accounts, cloud services or downloaded web dependencies. The screen and web UI remain Vietnamese.

**Current owned motors:** keep the eight continuous-rotation SG90s already bought; no replacement purchase is selected. Use the [360° manual-reference experiment](CONTINUOUS360.md) for one-channel calibration and bounded estimated-angle jogs. This is speed/direction control with human observations, not encoder feedback or a walking gait. All outputs start off. On 2026-11-11 the owner reported all eight servos worked individually and all joints were manually placed at the 90° reference. Per-direction speed calibration and a fresh runtime confirmation remain necessary; these reports do not auto-arm anything.

## Choose the correct target

| Hardware | Target | Complete image directory |
|---|---|---|
| Original LILYGO T-Display-S3 non-touch + external PCA9685 | `lilygo` | `build/firmware/esp32/` |
| Custom ESP32-S3-WROOM-1-N16R8 + PCA9685 PCB, Waveshare 23822 LCD | `integrated` | `build/firmware/integrated/` |

Run the repository-root `./build.sh` to build and check both. To compile one target after its source dependencies are prepared:

```sh
python3 tools/firmware/build.py --target integrated
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

## Direct phone connection and optional home Wi-Fi

1. Power logic/LCD only. Scan the Wi-Fi QR to join `CuaRobot-XXXX`. Keep the connection if the phone says it has no internet. Open **http://192.168.4.1/** in a normal browser if the captive page does not open.
2. The controller opens directly. Status polling must preserve the selected **Lái cua**, **Ráp** or **Wi-Fi** page, including when home Wi-Fi is absent, unreachable or rejects the password. The light can be used without joining a router.
3. Home Wi-Fi is optional. Open **Wi-Fi** manually, tap **Tìm Wi-Fi quanh đây**, choose a 2.4 GHz network and tap **Kết nối** after entering its password. Wrong credentials or a timeout show an error without redirecting other pages. Credentials are stored in NVS, not source or logs. After success the second QR gives the home-network address; direct AP access remains available.
4. For supported positional servos, hold a direction to move and release to stop. Tab changes, screen locking and a missing keep-alive for about 0.5 seconds cancel motion. Release and press again after a disconnect. Left/right mean sideways in the kinematic model, with four diagonal translations. The owner's continuous servos cannot execute this joint-angle gait; actual walking remains unproven.
5. **Bật/tắt đèn** switches all eight LEDs, brightness limited to 16/255. Hold BOOT for eight seconds **while the application is running** to clear Wi-Fi; servo trims remain saved. BOOT is not a power switch.

Desktop request/browser tests do not prove that every phone will retain an internet-free AP connection or that the real radio will remain uninterrupted. Physical direct-AP verification remains separate from compilation and host tests.

## Continuous 360° control with a manual reference

Open **360° thử nghiệm**. The [complete guide](CONTINUOUS360.md) explains the per-channel stop/forward/reverse counts (205–409), assignment to observed clockwise/counterclockwise rotation, measured degrees and elapsed milliseconds, pending hip-viewpoint selector, and **Đã đặt 90°** confirmation. Entering or saving observations never starts a servo. No stop value or motor speed is assumed correct by default.

Only one CH0–7 can receive a timed command. Duration is clipped to a selected 50–500 ms cap and remaining software travel budget; the 500 ms keep-alive cannot extend it. Front hip budgets are CW25°/CCW55°, rear hips CW55°/CCW25°, and knees ±35°: the owner's hand-reported limits minus a 5° margin. The UI displays estimated displacement and requested/last emitted PCA counts. These are software/I²C observations, not measured shaft angle or a collision guarantee.

Expiry, release/off, disconnect, settings/calibration/session/mode changes, a fault or untracked motion invalidate the reference. Physically restore the pose and confirm again before another run; the button is not automatic homing or a way to bypass the travel budget. Settings remain in RAM, and reboot starts with all 16 outputs off. **Drive arrows stay disabled for continuous servos** because there is no validated loaded walking pattern for this joint geometry.

The previous [single-servo diagnostic](SERVO-TEST.md) remains under **Chi tiết → Thử cũ** for an unloaded servo only. It is untracked motion and invalidates the manual reference. The light and direct Wi-Fi remain independent of actuator mode.

The positional gait is retained for a separate compatible configuration using eight confirmed positional servos. Never choose that setting for the owner's continuous motors.

## Centre before attaching horns — positional servos only

With supported positional mode explicitly selected, support the body securely with feet clear and uncouple installed horns/legs from their output shafts. Open **Ráp**, tap **Giữa thô 1500 µs** and wait about two seconds. Attach horns in the mechanical neutral pose. **Tư thế đứng** applies saved trims; adjust individual +/− controls in one-degree steps (±12°), then use **Lưu tâm** and **Xong ráp**. Assembly locks walking until exited. Trim compensates horn indexing, not asymmetric printed parts. These commands are refused in unknown/continuous mode.

In positional mode channels initially enable 300 ms apart and subsequent commands update one channel per 10 ms with slew/amplitude ramps. These reduce command surges without imposing an electrical current limit. The experimental mode uses its separate one-channel output policy. PCA init failure is finite and does not prevent QR/web startup; it displays the driver warning.

## Desktop checks and limits

`python3 tools/firmware/check.py` runs all seven host groups for both hardware profiles, including independent QR decoding with Apple Vision. Tests cover reference invalidation, uncalibrated and pending-viewpoint gates, front/rear hip and knee budgets in both directions, duration clipping, actual PCA register writes, output limits, stopping/session/settings behavior, and direct-AP navigation. [TEST-RESULTS.json](TEST-RESULTS.json) is generated after the complete suite passes. Board reconciliation separately checks actual PCB/XML pins.

The existing positional gait model does not establish stability or physical walking. The continuous experiment is an estimated, single-joint motion tool. Software full-off is not braking, holding or a power disconnect; a lost I²C link on the original LILYGO cannot guarantee receipt of an off command. The supply rating and actual pulse/frequency/load behavior remain unmeasured. See [the full limits](CONTINUOUS360.md) and [flashing policy](FLASH-POLICY.md).

[Sources and licences](SOURCES.md) · [Interface metadata](INTEGRATION.json) · [Mechanical checklist](../case/CHECKLIST-RAP.md)

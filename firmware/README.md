# Crab firmware — two hardware targets

The application implements QR setup, nearby 2.4 GHz Wi-Fi selection, saved credentials, eight hold-to-move directions, a light switch and servo centring/trim controls. Everything is served by the robot; there are no accounts, cloud services or downloaded web dependencies. The screen and web UI remain Vietnamese.

**Current owned motors:** the seller confirms the purchased SG90 360° units are continuous-rotation motors. The positional walking, centre and angle-trim instructions below apply only to supported positional servos. Sending 1500 µs to a continuous unit is a neutral-speed experiment; it does not centre or hold its shaft. Do not run the positional assembly/gait commands with the owner's continuous motors. The owner has no additional purchase budget; a software-only experiment is under review, not a demonstrated walking solution.

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

For the original LILYGO, disconnect power-bank output 2 and all servo power. Unplug bank output 1 before connecting the LILYGO to the computer with a data cable. Choose the actual LILYGO serial port, then run:

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

## Centre before attaching horns

Support the body securely with its feet clear. **Uncouple already installed horns/legs from their servo output shafts before centring.** Do not drive an assembled leg against the frame.

Open **Ráp**, tap **Giữa thô 1500 µs** and wait about two seconds. Attach horns in the mechanical neutral pose. **Tư thế đứng** applies saved trims; adjust individual +/− controls in one-degree steps (±12°), then use **Lưu tâm** and **Xong ráp**. Assembly mode locks walking until exited, even if the browser disconnects. Trim compensates horn indexing, not asymmetric printed parts.

Servo channels enable 300 ms apart; subsequent commands update one channel per 10 ms with slew/amplitude ramps. Simultaneous 50 Hz holding pulses remain. This reduces command surges but does not limit electrical current. If the bank shuts off, select **Chậm**, remove mechanical binding and use a suitable bank. Disconnect output 2 before reset/flashing; PCA/LED state can persist during MCU reset.

## Desktop checks and limits

`python3 tools/firmware/check.py` runs core, web, HTTP, interface, driver, target and display groups, including independent QR decoding with Apple Vision. [TEST-RESULTS.json](TEST-RESULTS.json) is generated only after the suite passes. The board reconciler checks exact PCB/XML pins and reviewed evidence separately.

The gait test samples 720 points per cycle in eight directions, with alternating diagonal pairs. Its ideal-contact model does not establish static stability, friction, servo lag, power capacity or real walking. CAD collision checks are separate. First-prototype checks cover direction signs, horn fit, QR visibility, Wi-Fi range, bank behaviour and WS2812 reception of direct 3.3 V data.

[Sources and licences](SOURCES.md) · [Interface metadata](INTEGRATION.json) · [Mechanical checklist](../case/CHECKLIST-RAP.md)

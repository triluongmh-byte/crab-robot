# Crab firmware — two hardware targets

The application implements QR setup, nearby 2.4 GHz Wi-Fi selection, saved credentials, eight hold-to-move directions, a light switch and servo centring/trim controls. Everything is served by the robot; there are no accounts, cloud services or downloaded web dependencies. The screen and web UI remain Vietnamese.

**Current owned motors:** the seller confirms the purchased SG90 360° units are continuous-rotation motors. They control speed/direction and cannot hold the joint angles required by this gait. The default is now **360° / unknown, all sixteen PCA outputs off**. Walking and raw-centre commands are refused until an explicit positional selection. A manually opened [one-servo experiment](SERVO-TEST.md) provides bounded neutral/speed commands; it does not turn these motors into positional servos. No additional purchase or physical motor test is being made.

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

## Default outputs and the one-servo experiment

Every reset starts as **360° / chưa rõ loại — mặc định tắt** (continuous/unknown, off). The actuator selection and test settings live in RAM only; stored positional trims cannot enable the outputs. Home Wi-Fi and the light remain available independently of the actuator mode.

**Thử 1 servo** opens the experimental test. Opening it, changing channel or adjusting neutral does not move a servo. A held button can command exactly one CH0–7; release, stop, session change or timeout requests full-off. Each press has a 2000 ms cap and 500 ms command lease. Integer PCA counts are displayed with a labelled nominal microsecond conversion. Read the [complete test guide and limits](SERVO-TEST.md) before any physical test. The current owned inventory has no servo supply of established rating, and flash permission does not authorize motor operation.

The positional gait and centring code remain available only for **eight confirmed compatible positional servos**. On **Lái cua**, choose **Định vị 180° — đã xác nhận cả 8**, then **Áp dụng loại servo**. This intentionally starts positional pulses. Never select it for the owner's continuous motors. Reboot returns to unknown/off.

## Centre before attaching horns — positional servos only

With supported positional mode explicitly selected, support the body securely with feet clear and uncouple installed horns/legs from their output shafts. Open **Ráp**, tap **Giữa thô 1500 µs** and wait about two seconds. Attach horns in the mechanical neutral pose. **Tư thế đứng** applies saved trims; adjust individual +/− controls in one-degree steps (±12°), then use **Lưu tâm** and **Xong ráp**. Assembly locks walking until exited. Trim compensates horn indexing, not asymmetric printed parts. These commands are refused in unknown/continuous mode.

In positional mode channels initially enable 300 ms apart and subsequent commands update one channel per 10 ms with slew/amplitude ramps. These reduce command surges without imposing an electrical current limit. The experimental mode uses its separate one-channel output policy. PCA init failure is finite and does not prevent QR/web startup; it displays the driver warning.

## Desktop checks and limits

`python3 tools/firmware/check.py` runs core, web, HTTP, interface, driver, target and display groups for both hardware profiles, including independent QR decoding with Apple Vision. It checks actual HTTP routes and PCA register output for default-off startup, one channel, count bounds, timeout/dead-man/session transitions and the retained positional behavior. [TEST-RESULTS.json](TEST-RESULTS.json) is generated only after the suite passes. The board reconciler checks exact PCB/XML pins and reviewed evidence separately.

The positional gait test samples 720 points per cycle in eight directions, with alternating diagonal pairs. Its ideal-contact model does not establish stability, friction, servo lag, power capacity or walking. CAD collision checks are separate. The continuous-servo test neither holds angle nor establishes a walking gait. Software full-off is not a power cut or a guaranteed brake; I²C failure and scheduling/network delays remain physical limitations, as detailed in the test guide.

[Sources and licences](SOURCES.md) · [Interface metadata](INTEGRATION.json) · [Mechanical checklist](../case/CHECKLIST-RAP.md)

# Firmware for the integrated controller

The current prototype uses the side-entry USB-C PCB and two open frames. See [build validation](../BUILD-VALIDATION.md) for desktop checks and the remaining first-board tests.

The two hardware variants share the web/Wi-Fi/gait application but use different display and servo-enable pins. Build the **integrated** target for this custom PCB. Keep the LILYGO target for the original development board and separate PCA9685 module.

```sh
python3 tools/firmware/build.py --target integrated
```

Or build both with `--target all`. ESP32 Arduino core **2.0.14** must already be installed in the documented shared toolchain. The build does not install software or access a USB device.

The integrated artifacts are under `build/firmware/integrated/`; `firmware/BUILD-integrated.json` records their source/toolchain hashes. The integrated recipe is `firmware/flash-integrated.json`. The LILYGO binary directory is `build/firmware/esp32/`. Do not interchange them.

Before flashing, run the host suite and final-board reconciliation:

```sh
python3 tools/firmware/check.py
python3 tools/firmware/reconcile.py
```

The reconciliation must pass against the current native board/netlist; a pending or failed result is not a release. GPIO21 holds PCA outputs off by default. Initialization sends FULL_OFF; actual pulses require an explicit positional selection or the separate continuous-servo experiment. See the [actuator policy](../firmware/README.md#continuous-360-control-with-a-manual-reference). The integrated display uses SPI (GPIO8 clock, GPIO39 data), while LILYGO retains its original parallel display bus.

## Flash it yourself after assembly inspection

1. Disconnect power-bank output 2 and all servo plugs. Disconnect the power-bank USB cable before connecting the PCB's USB-C directly to your computer with a data cable.
2. Identify the USB port belonging to the new PCB. The original LILYGO can have the same Espressif USB vendor ID, so unplug it while choosing the port.
3. If needed, hold BOOT, press/release RESET, then release BOOT to enter the ROM downloader.
4. Replace `YOUR_BOARD_PORT` in the command below with the actual port and run it. This command uploads the complete built image set, not only the application binary.

```sh
arduino-cli upload \
  --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,PSRAM=opi,DebugLevel=none' \
  --port YOUR_BOARD_PORT \
  --input-dir build/firmware/integrated firmware/crab
```

Press RESET after upload if needed. Check that the setup QR is readable and that Wi-Fi setup works before adding servo power. The module memory configuration is 16 MB flash with 8 MB octal PSRAM. Do not write `crab.ino.bin` alone at address zero.

The Firmware pane may retain the LILYGO default recipe; explicitly select the integrated recipe if the UI offers recipe selection, or use the command above. Merely seeing an Espressif USB device does not choose the correct target.

Holding BOOT for eight seconds **after the application has started** clears saved Wi-Fi settings and returns to setup. This differs from holding it during reset for programming. Follow the [wiring/servo-centering guide](INTEGRATED-WIRING.md) for the first powered robot test.

These are instructions for the future board. The integrated firmware has not been flashed or run on manufactured hardware; compilation and host tests do not prove that the robot walks.

# Integrated Crab Robot controller — design intent

The owner explicitly corrected the passive-carrier interpretation: the PCB must replace the ESP32/LILYGO development board and bought controller breakout boards, including the PCA9685 module. The passive carrier is superseded and unpublished.

## Chosen direction

One custom PCB with a soldered ESP32-S3 radio module, onboard PCA9685 servo driver, native USB-C programming/power, required logic supply/support parts, BOOT/RESET and the robot connectors. Keep QR/screen, local Wi-Fi/web operation, eight SG90 channels and the WS2812 light. The existing 5V two-port power bank remains; no loose-cell battery pack. Routine engineering choices were delegated by the owner.

A carrier retaining the LILYGO/PCA modules was rejected by the owner. A bare-SoC RF design is unnecessary: a documented radio module on the PCB keeps the radio integration simpler. Display selection and any interface changes must be documented from manufacturer data and reflected in firmware; no guessed FPC pinout.

## Integration and delivery

Use the actual final board STEP, connector positions and display geometry for compatible mounting changes. Preserve the plate-2 legs/clamp bars and servo axes. Do not claim a physical print or fit from CAD. Native board ERC/DRC/manufacturing checks and independent role/integration tests must pass. Build both the new board firmware and retained LILYGO profile, without flashing either device.

Publish sources/inputs/docs on `hardware/integrated-controller`, leaving main unchanged. Provide an English README, PCB/PCBA ordering guide, exact remaining purchases and manual assembly work, firmware recipes, current case/plate handoff, and a source-only build proven in an empty clone. Generated packets/binaries/reports stay outside Git; no credentials, flash/NVS backups, vendor datasheets or personal photos. No purchase, hardware motion or printer job is requested.

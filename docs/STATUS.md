# Hardware status — 9 November 2026

[Tiếng Việt](STATUS.vi.md).

- The owner has a LILYGO T-Display-S3 non-touch. The newer workspace firmware was flashed onto its ESP32-S3; bootloader, partition and application regions were read back and verified successfully.
- The owner confirmed the QR display, web access and the company Wi-Fi appearing in the scan list. Successful connection to that network has not been confirmed.
- Only the board and screen are USB-powered. The owner does not yet have a PCA9685 and needs one module with soldered headers: see the [buying guide](PCA9685-WIRING.md).
- Plate 2 was reported printing. Completion and fit have not been confirmed; a slicer preview does not prove a physical print exists.
- Servos, LEDs, power-bank behavior under load, frame strength and floor walking remain untested.

## Keep the two versions separate

| Item | GitHub source baseline, 6 November | Owner's workspace/flashed board, 9 November |
|---|---|---|
| Body | Original closed body, shown in the README gallery | Skeleton A1V4-r2, exposing boards and wires |
| LED DIN | GPIO21 | GPIO1 |
| SDA / SCL / logic VCC | GPIO18 / GPIO17 / 3.3 V | Same as baseline |
| CH0–CH7 | Hip/knee pairs for FL, FR, RL, RR | Same as baseline |
| Lost-heartbeat timeout | 600 ms | 500 ms |
| Physically confirmed | No separate confirmation for the baseline binary | QR, web and Wi-Fi scanning on the loose board |

These Git updates add buying/wiring documentation, translations and status notes while retaining the existing baseline CAD/firmware sources. The flashed-board guide does not mean the baseline source is the binary running on the owner's board. When building/flashing from this repository, follow the baseline pinout. Software differences do not establish mechanical fit or walking ability.

Flash/NVS backups and Wi-Fi information stay local and are not published.

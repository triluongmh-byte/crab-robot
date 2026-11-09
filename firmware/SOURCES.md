# Source evidence — baseline 2026-11-06; note-4 update 2026-11-09

- [Kame32](https://github.com/JavierIH/kame32/tree/8f33e489f7425747ab62aeb509777a06d2f14f3e), `code/lib/Kame/kame.cpp`, specifically `execute`, `walk`, `omniWalk`: amplitude/period/offset/phase oscillator structure. Snapshot `vendor/kame32-original.cpp`; full GPLv3 in `vendor/KAME32-LICENSE`. This project's adapted firmware is GPL-3.0-or-later. Hardware-specific LEDC, blocking loops and old channel ordering were replaced; no claim of copying its physical gait calibration. New direction projection is specific to this robot.
- [LILYGO official non-touch reference](https://github.com/Xinyuan-LilyGO/T-Display-S3/tree/1cc41eb1c76b2f3215130a3dd64e7138ce00b482), `examples/factory/pin_config.h` and `factory.ino`: verified i80 pin order, power GPIO15 HIGH, RD HIGH, 16 MHz pixel clock, swap XY, mirror(false,true), gap(0,35), invert colour, USB at left in landscape, and the newer-panel LCD_MODULE_CMD_1 register sequence. MIT license is in `vendor/LILYGO-LICENSE`. Reference pin header saved in `vendor/lilygo-pin_config.h`; the full example was inspected as evidence, not compiled. The LILYGO build remains tied to schematic 2024-04-29. Note 4 adds a separate integrated board target; the LILYGO reference is not evidence for the new panel/FPC, backlight circuit or OE wiring. Firmware uses the installed Espressif `esp_lcd` driver.
- [Adafruit PCA9685 pinouts](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts): VCC is logic, V+ is servo power, common GND; matched the contract. Clone pin location is not assumed: WIRING uses labels.
- [NXP PCA9685 datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf): MODE1 AI/sleep, prescale, LEDn full-off fields. Startup off writes are single-register writes so they work even before auto-increment is enabled; prescale121 assumes the nominal25MHz internal oscillator, approximately50Hz. Oscillator tolerance/SG90 range are unmeasured.
- [Nayuki QR Code generator](https://github.com/nayuki/QR-Code-generator/tree/bcfe1b018cec5f1f91b5705eca5bb4cdd34e9f8d/c), unmodified `qrcodegen.c/.h`, MIT notice embedded in both files. QR version1…5, ECC M with boost, ≥4-module quiet zone, screen integer scale3…4. Host tests use the same encoder and actual pixel size, independently decoded by macOS Vision.
- [Noto Sans](https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf/NotoSans), Regular, SIL OFL (`assets/OFL.txt`). Downloaded source font retained in `assets/`; its exact SHA256 is in `font-manifest.json`. Embedded12px bitmap includes Vietnamese precomposed tone letters, no font downloaded at runtime.
- Build runtime: official Espressif Arduino core2.0.14 from shared `ARDUINO_DIRECTORIES_DATA`. Only core WiFi, WebServer, DNSServer, Wire, Preferences and bundled IDF `esp_lcd`/RMT. No local SDK/toolchain install, no cloud dependency, no hardware access.

Release note4 tip: `122b5b3d406fc1cc148b6bf5abaf6c6fc7315e933a95e5565c1b60ee86d35e08`.
Final board sources `design/main.kicad_pcb`, `build/board/main.net`,
`engineering/firmware-interface.md` and `engineering/DEVIATIONS.md` establish
GPIO21 OE, GPIO15 NC and the SPI display fallback. Reviewed hashes and all
pad groups are in [board-interface.json](board-interface.json).

- [Official Waveshare 1.9inch LCD wiki](https://www.waveshare.com/wiki/1.9inch_LCD_Module)
  documents the SPI ST7789V2 and links its
  [official demo archive](https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip).
  Downloaded 2026-11-09: exact archive/file SHA256 and URL in
  `vendor/waveshare-source.json`. Retained C/Python originals in `vendor/`.
  `LCD_1in9.c::LCD_1IN9_InitReg` supplies all16 register commands and120ms
  sleep-out delay. `LCD_1inch9.py::ShowImage/SetWindows` supplies landscape
  MADCTL0x70 and y35 offset (the C demo's orientation handling is inconsistent,
  so the Python landscape window is used). The firmware uses SPI mode0 at
  a conservative10MHz per board report. `case/DEVIATIONS.md` D15 turns the
  panel180°, so MADCTL XOR0xc0=0xb0. No LILYGO init on the new target.
- Display supply/pinout/backlight: board-team retained manufacturer schematic
  `engineering/sources/integrated/waveshare.pdf`, and final J10 pad nets;
  board logic supply3V3 matches the display logic requirement. No FPC guess.

Case D7 servo direction signs remain unchanged; case D15 adds only the screen
orientation. Hardware, Wi-Fi range, screen/window scan, power bank and movement
remain untested. No other project/worktree or hardware was accessed.

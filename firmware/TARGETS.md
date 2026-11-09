# Hardware targets — release note 4, reconciled 2026-11-09

One application, two explicit compile configurations; no runtime pin guessing.
Shared Arduino ESP32 core2.0.14/toolchain cache, all-core compilation, no install.

- `lilygo`: non-touch T-Display-S3; LCD power15 HIGH, original i80 16MHz,
  original factory init/gap/orientation; external PCA module, no MCU OE control.
- `integrated`: ESP32-S3-WROOM-1-N16R8; native USB19/20, on-board PCA9685,
  GPIO21 /OE with R9 10k pullup to3V3; GPIO15 is NC. SPI Waveshare23822,
  SCLK8/MOSI39/CS6/DC7/RES5/BL38 at10MHz mode0, vendor init RGB565 and
  landscape gap(0,35), rotated180° for case D15 (MADCTL0xb0).

Both keep SDA18/SCL17, LED1, BOOT0, all eight channels/direction signs and
Wi-Fi/web/gait/trim behaviour. Integrated-only unused i80 GPIOs are never set.
OE stays HIGH before LCD/I2C; clear all16 registers, release only after a valid
first CH0 write. Any I2C failure asserts OE immediately and latches the fault.

The final native PCB/XML and board report are bound by board-interface.json;
reconcile.py checks every reviewed connection and native pad parity read-only.
Host display tests exercise actual Screen::begin/show, validate the chosen bus,
offsets, rotation, failure backlight state and compare the emitted commands to
the independently retained official Waveshare C init, not LILYGO's sequence.

Outputs: build/firmware/{esp32,integrated}/crab.ino.bin, accompanying bootloader,
partitions, ELF; BUILD.json and BUILD-integrated.json bind full source/recipes
and every binary. flash.json remains the LILYGO pane default; select the separate
flash-integrated.json manually for the new board. No integrated flash permission.
Physical behaviour is untested; firmware checks are not whole-product readiness.

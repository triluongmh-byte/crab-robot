# Integrated V0 firmware interface — release note 4

Native source: design/spec.json and design/main.kicad_sch/pcb. Final native
XML netlist will be build/board/main.net. GPIO numbers are MCU GPIOs, not
physical module pads. Keep the existing LILYGO build separately.

| Feature | GPIO / destination | Electrical behaviour |
|---|---|---|
| I2C SDA / SCL |18 /17 → U3 pins27/26 | Single4.7k pullups to3V3 |
| PCA address |0x40 | A0..A5 atGND, EXTCLK GND, internal oscillator |
| PCA output enable |21 → U3 pin23 /OE | NEW: 10k pullup; high disables outputs |
| WS2812 DIN |1 → J11 pin1 | Direct3.3V; J11 pin2SERVO_5V/pin3GND |
| BOOT |0 → SW1 | Active low;10k pullup, existing8s erase behaviour |
| RESET |EN → SW2 | Active low;10k/1uF power-on RC |
| LCD reset /CS /DC |5 /6 /7 → J10 pins2/4/3 | Reset10k down;CS10k up |
| LCD SPI clock /MOSI |8 /39 → J10 pins5/6 | CHANGED from i80; SPI mode0, start10MHz |
| LCD backlight |38 → J10 pin1 | Active high,330Ω reset pulldown |
| LCD VCC /GND |J10 pins8/7 | 3V3 matching Waveshare logic supply |
| Native USB D− /D+ |19 /20 | USB Serial/JTAG,22Ω per signal nearMCU |
| Legacy LCD_POWER_ON |15 | NC; driving high has no effect |

GPIO4,16,3,43,44,35..37 remain unused. GPIO9,40..42,45..48 are NC because
the display uses SPI. Strapping0 pulled high,45/46 unused; no display readback
can drive boot straps. N16R8 flash16MB/quad,PSRAM8MB/octal.

BOOT/reset initialization: keep GPIO21 HIGH (or input, external pullup holds
it high), initialize I2C and PCA all channels FULL_OFF, set50Hz and totem-pole
outputs/OUTNE00. Only then driveGPIO21 LOW and enable channels sequentially.
On failure keep /OE high. For emergency disable drive high. Blank flash,
ROM download and MCU reset all leave pulses disabled. A powered SG90 can
still draw idle current; /OE is signal disable, not supply isolation.

PCA CH0..7: hipFL,kneeFL,hipFR,kneeFR,hipRL,kneeRL,hipRR,kneeRR. CH8..15NC.
No gait, direction or UI behaviour change. Waveshare23822 ST7789V2 170×320
needs its vendor initialization and panel address offsets; the former LILYGO
parallel peripheral configuration must not be reused. Do not silently map back
to i80. Original LILYGO firmware remains a separate target.

LED may retain its last colour through MCU reset. Firmware must send black
at startup. Physical LED acceptance of3.3V DIN and power-bank surge response
remain original bench assumptions. No board has been flashed or powered.

Note9 USB relocation (2026-11-10): J1 now opens toward board-local+Y,
centreX21.45, mouthY+32.8 (native origin21.45,-28, rotation180°). Use the
case side opening and ordinary USB-C cable route after final case recheck.
All nets/GPIOs and wire destinations are unchanged; no firmware source change
or binary rebuild is needed. LCD stays rotated180° per current firmware.

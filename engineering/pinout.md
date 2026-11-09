# Integrated V0 pin audit

Active native sources are main.kicad_sch/pcb and spec.json. Full real XML
netlist is build/board/main.net. tools/board/check.py uses an independent
manufacturer pad map and actual KiCad pads, then native parity checks every
pad including NCs. Fifty-one schematic symbols include three power flags,
four holes and four testpoints; no hollow electrically active symbol.

ESP module Table3-1:1/40/41GND,2supply,3EN;5GPIO5=LCD_RES,6GPIO6=LCD_CS,
7GPIO7=LCD_DC,10GPIO17=SCL,11GPIO18=SDA,12GPIO8=SPIclock,13GPIO19=USB−,
14GPIO20=USB+,23GPIO21=PCA/OE,27GPIO0=BOOT,31GPIO38=BL,32GPIO39=MOSI,
39GPIO1=LED. Module4GPIO4,8GPIO15,9GPIO16,15GPIO3,16GPIO46,24GPIO47,
25GPIO48,26GPIO45,28..30GPIO35..37,33..35GPIO40..42,36RXD0/44,
37TXD0/43,38GPIO2 are explicitNC. Internal33/34 are not module pads or usable
external pins.16MBflashquad/8MBPSRAMoctal ordering suffix is exact.

PCA TSSOP28:1..5A0..4,24A5,25EXTCLK,14VSS atGND;28VDD3V3;23/OE GPIO21
with10kup;26SCL/27SDA fromGPIO17/18 each one4.7kup. Pins6..13 LED0..7 map
toJ2..9 pin3, channels0..7;15..22 LED8..15 explicitNC. CH0hipFL,1kneeFL,
2hipFR,3kneeFR,4hipRL,5kneeRL,6hipRR,7kneeRR.

USB J1 A4/A9/B4/B9PB1_5V;A1/A12/B1/B12/shieldGND;A6/B6D+;A7/B7D−;
A5CC1 andB5CC2 each own5.1k pulldown;SBU1/2NC. D±22Ω near MCU.
U2 physical1GND,2OUT3V3,3INPB1_5V, tab2OUT. Symbol TLV1117-33 is a
pin-compatible graphic only; BOM/value enforce TI TLV1117LV33DCYR.

J2..9 from top-view row y17→22.08:pin1GND/brown,pin2SERVO_5V/red,pin3PWM/orange.
J10 pin1BL,2RESET,3DC,4CS,5SCK,6MOSI,7GND,8VCC3V3 (x increasing).
J11 pin1DIN,2SERVO_5V,3GND. J12 pin1SERVO_5V,2GND. TP1PB1_5V,
TP2SERVO_5V,TP3logic3V3,TP4GND. Never join two positive5V nets.

New SPI target and GPIO21 are explicitly handed to firmware in
firmware-interface.md; GPIO15NC has no power switch. Case receives actual
PCB/display STEP and board-interface.json. No firmware remap is implicit.

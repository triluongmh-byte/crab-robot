# Integrated board V0 — release note 4, 2026-11-09

Selected architecture: ESP32-S3-WROOM-1-N16R8 certified module, native USB-C,
TLV1117LV33 1A LDO, PCA9685PW 0x40, eight servo connectors, independent
SERVO_5V terminal and LED connector. Top population, 88×62×1.6mm, two layers.
Common ground; PB1_5V and SERVO_5V have no positive-rail connection.

Display V0 uses the documented Waveshare 23822 1.9in 170×320 ST7789V2 SPI
module on a flexible labelled 8-wire harness. GPIO8=SCLK and39=MOSI;5=RESET,
6=CS,7=DC,38=BL unchanged;9/40/41/42/45/46/47/48 unused. GPIO15 is deliberately
NC (legacy LILYGO LCD power enable has no load). GPIO21 drives PCA /OE, with
10k pullup so reset/empty flash/BOOTSEL disable all servo pulses. Firmware
must initialize all channels FULL_OFF before pulling GPIO21 low.

The bare-panel approach was investigated first. GoldenMorning's official
GMT019-01 drawing/pin assignment was obtained, but its web voltage specification
(3–5V) conflicts with the manufacturer's Rev A specification's 3.3V maximum.
Microtips AWY-170320T19N01 also specifies 3.3V maximum normal operation, below
the worst-case output of a nominal3.3V LDO. Neither provides a documented route
for the permitted single fixed3.3V supply without accepting an out-of-range
condition or adding a second rail. Therefore choose the documented plug-in V0
and record the bus change; no FPC pinout or clone geometry is guessed.

Interfaces: final netlist and measured PCB export are the handoff to firmware
and case. Display STEP from manufacturer, PCB STEP from actual KiCad; display
position/retention is the case team's decision, with 8-wire slack/access.
Factory SMT population, including USB connector and switches. Nine 3-pin THT
headers + one8-pin LCD header + one2-pin terminal are the only planned manual joints (37 total),
prefer factory THT assembly if quoted. Servo connectors brown/red/orange
=GND/SERVO_5V/PWM. CH0..7 remain HIP_FL,KNEE_FL,HIP_FR,KNEE_FR,HIP_RL,
KNEE_RL,HIP_RR,KNEE_RR. Radio antenna placed on edge with copper keepout.

USB input capacitance <=10uF. Radio supply reserve>=500mA plus40mA LCD+10mA
PCA+pulls; LDO1A. Servo bank port>=2.4A is source-limited, motion sequencing
required; no claim eight stalled servos can operate from2.4A. LED<=480mA
estimate, data3.3V assumption retained. No ordering, hardware or flash action.

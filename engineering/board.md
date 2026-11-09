# Board-team deliverable — integrated V0, 2026-11-09

Effective release4 replaces the former passive carrier. Active native schematic,
PCB and real XML netlist represent ESP32-S3-WROOM-1-N16R8,TI3.3VLDO,PCA9685,
USB-C,BOOT/RESET,eightservoheaders,LEDconnector and separate servo terminal.
88×62×1.6mm2layers/top assembly,4optional M3mount holes. Two positive5V rails
remain separate; commonGND is on PCB. Hardware has not been powered/tested.

Display is documented Waveshare23822 1.9in170×320SPI fallback; GPIO8SCLK,
39MOSI; GPIO21 /OE added, GPIO15NC. firmware-interface.md is the pin/state
handoff and board-interface.json/case-interface.md the geometry handoff.
Actual STEP: build/board/integrated.step; official display STEP in sources/.
USB and switch STEP are disclosed conservative envelopes (3D-MODELS.md).
MUA-THEM-PCB.md is the Vietnamese buy/service list; assembly.md names37 PCB
joints and three conditional LED-bar joints. Factory SMT is required.

Current readiness/counts/packet hashes come only from boards/main.board.json
and its newest native/manufacturing reports. Old note3 fab.ready does not
apply. Independent tester and cross-team integration still determine product
readiness. No push, order, upload, flash, motor or printer action occurred.

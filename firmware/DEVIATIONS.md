# Note-4 firmware reconciliation — 2026-11-09

The sealed contract and release notes are unchanged. Firmware follows the final
board fallback allowed by note4 and the lead's concrete integration findings.

| Contract / former draft | Verified final option | Evidence | Cross-team impact |
|---|---|---|---|
| Note4 prefers bare 1.9in i80; permits documented plug-in ST7789 fallback | Waveshare 23822 SPI ST7789V2; SCLK8, MOSI39, CS6, DC7, RES5, BL38 | engineering/DEVIATIONS.md, engineering/firmware-interface.md, final XML/PCB, vendor/LCD_1in9.c + vendor/LCD_1inch9.py | Integrated SPI configuration; LILYGO i80 retained. GPIO9/40–42/45–48 NC. No user behaviour/channel/gait change. |
| Earlier firmware proposed GPIO15=OE; note4 asks to state GPIO15's role | GPIO21 drives /OE; GPIO15 NC | U1.23–U3.23 and R9.2 on SERVO_OE; R9.1=3V3, R9=10k | Firmware and integrated tests now use21; no copper, rail or wire change. Blank flash/reset stays inhibited by physical pullup. |
| Screen must read through case window | Vendor landscape MADCTL0x70 xor0xc0=0xb0, window gap(0,35) | Official Python landscape driver; case/DEVIATIONS.md D15 panel rotation180° | Integrated-only rotation compensation. Case orientation unchanged. QR/window legibility still needs physical check. |

board-interface.json records source/evidence hashes and actual pad groups;
BOARD-RECONCILIATION.json now passes from the actual native PCB/XML, including
USB series paths, rails, output-enable pullup and servo connector order.
The previous candidate and pending-carrier statements are superseded.

No flash, motors, hardware, order, commit or push. No user blocker.

# Integrated-board sources — checked 2026-11-09

This release supersedes note3's passive carrier. No earlier workspace was read.
Native library source is the KiCad bundle in /Applications/KiCad/KiCad.app;
footprints/models copied locally. Generated flattened symbols come only from
kicadpy.author and its bundled libraries; no hand-edited schematic symbol.

- Espressif ESP32-S3-WROOM-1/WROOM-1U v1.8: https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
  Local sources/integrated/esp32.pdf. Tables3-1/4-1, module dimensions and
  antenna/layout figures establish pad numbers, memory restrictions, reset,
  supply reserve and module edge placement. N16R8 is16MB quad/8MB octal.
- NXP PCA9685 Rev4: https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf
  Local pca9685.pdf; TSSOP pin table, /OE, POR and OUTNE reset state.
- TI TLV1117LV SBVS160C: https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf
  Local tlv1117lv.pdf; DCY pins1GND/2OUT/3IN/tabOUT; ceramic1uF stability,
  1A rating, input5.5V max, output tolerance±1.5%, thermal reference62.9°C/W.
- Waveshare SKU23822: https://www.waveshare.com/1.9inch-LCD-Module.htm
  https://www.waveshare.com/wiki/1.9inch_LCD_Module
  https://files.waveshare.com/upload/7/7f/1.9inch_LCD_Module.pdf
  https://files.waveshare.com/upload/9/98/1.9inch_LCD_Module_3D.zip
  Local waveshare.html/.pdf/-3d.zip/-display.step: exact documented8-pin
  BL,RST,DC,CS,SCL,SDA,GND,VCC;3.3V supply matches3.3V logic;40mA maker FAQ.
- Bare panel investigation: GoldenMorning GMT019-01 official drawing/pins:
  https://goldenmorninglcd.com/tft-display/1.9-inch-170x320-st7789-gmt019-01/
  Local gmt-drawing.webp/gmt-pinout.webp. Manufacturer web3–5V conflicts with
  RevA 3.3V-max normal range. Microtips AWY-170320T19N01 manufacturer's RevA
  2024-01-04 spec hosted by Mouser also max3.3V VDD/VDDIO:
  https://www.mouser.com/datasheet/2/271/Microtips_Technology_AWY170320T19N01_MTUSA-3451602.pdf
  Both investigated, neither assigned a guessed FPC footprint. V0 SPI fallback
  and its bus change are explicitly recorded in DEVIATIONS.md.
- Live factory identity/stock: build/board/stock.json, 15 exact codes queried
  directly from JLCPCB on this date, including C2913202 module,C2678753 PCA,
  C15578 TI regulator,C165948 HRO USB,C318884 XKB switch,C970714 bulk.
  Every supplier URL/MPN is in parts.json. Stock is a timestamped observation,
  never a guarantee; no price, order or upload is claimed.
- Native-vs-factory pad measurement: build/board/easyeda.json, rotation.log.
  **JLCEDA/EasyEDA Official Library**: https://lceda.cn/ and https://easyeda.com
  Supplier data used for independent factory footprint/orientation audit;
  original metadata/attribution retained in sources/integrated/C*-easyeda.json.
  USB/switch OBJ envelopes are explicitly identified in 3D-MODELS.md.
- Manual headers: https://www.samtec.com/products/tsw-103-07-g-s and
  https://www.samtec.com/products/tsw-108-07-g-s ;2.54mm,0.64mm posts.
- Terminal: Phoenix1715721 MKDS1,5/2-5,08:
  https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-15-2-508-1715721?type=pdf
  5.08mm pitch,2positions, through-hole; native exact model and land pattern.
- Fab: https://jlcpcb.com/capabilities/pcb-capabilities/ and
  https://jlcpcb.com/help/article/jlcpcb-copper-weight ; standard2layer1oz,
  1.6mm FR4. Actual widths≥0.2mm, clearance0.2mm, drills≥0.3mm; fab's own
  native floor and independent packet parser must pass unchanged.

sources/ prior LILYGO docs are historical evidence for note3 only. Current
board does not use LILYGO sockets or an external PCA module. No owned module,
mechanical fit, current, temperature or motor movement has been measured.

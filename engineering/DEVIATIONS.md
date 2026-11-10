# Deviations — integrated V0, release note 4

- Baseline sealed contract unchanged; notes3/4 replace dummy and carrier.
- Note4 first-choice bare1.9in 8-bit panel: official GMT019-01 pinout/drawing
  verified, but web3–5V statement conflicts with manufacturer RevA max3.3V;
  AWY-170320T19N01 similarly max3.3V. A nominal3.3V regulator has nonzero
  positive tolerance. Closest documented V0 is Waveshare23822 SPI display,
  expressly allowed as fallback; source details in integrated-design.md.
  Impact: GPIO8 nowSCLK,39 nowMOSI;9,40–42,45–48 unused. Firmware needs SPI
  target; case retains QR window using supplier STEP and harness.
- GPIO21 added for /OE default-off. GPIO15 no load/NC; no LCD power switch.
  All original I2C, LED, BOOT, CS/DC/RES/BL GPIOs and servo channels unchanged.
- Hand solder allowance follows note4:37 PCB joints if factory declines
  THT assembly, plus none for supplied display lead. SMT is factory only.
- Original passive-carrier documentation under carrier-* is historical note3;
  active product/spec/main board will exclusively represent integrated V0.

- Note9: same two-layer stackup retained. USB full-speed prototype paths are
  90.532/91.718mm, skew1.187mm, but controlled90Ω±10% is not established.
  This differs from Espressif layout guidance; see USB-RELOCATION.md for
  evidence/limits and mandatory first-board USB acceptance. No compliance,
  physical enumeration or whole-product readiness claim. Pins/parts unchanged.

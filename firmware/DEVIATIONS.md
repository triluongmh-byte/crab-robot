# Firmware deviations / decisions — 2026-11-06

Contract unchanged: `65b9793b07d82edc0defd9900ba1cfbee13dc730266cc0b675d897c87a75d9ea`.

## WS2812 fallback voltage (own wiring domain)

- Sealed text, `interfaces.assumptions[3]`: if flicker persists, “move the bar's 5V wire to the LILYGO 3V pin and keep brightness at 20% or less”.
- Change: keep the bar on 5 V. Shorten DIN beside GND first; if still unreliable, leave this optional light unplugged pending a compatible replacement. Do not advise 3.3 V as a verified supply for a 5 V WS2812B bar.
- Evidence: manufacturer Worldsemi WS2812B datasheet, supply range 3.5–5.3 V, digital VIH ≥0.7 VDD: https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf . At 5 V the guaranteed high threshold is 3.5 V; direct GPIO21 3.3 V therefore remains the explicitly requested hardware assumption. Supplying the LEDs from 3.3 V is outside the specified supply range and cannot be promised as the fix.
- Closest V0: unchanged three wires, no extra component, brightness cap 51/255, all 8 LEDs same colour, empirical flicker check. GPIO, rail, case, outline and mounts unchanged. Cross-team impact: lead should use this remedy in the root checklist/README; light remains untested.

## Knee lift direction reconciliation (integration repair)

- Sealed text, `interfaces.firmwareBehavior[10]`: “default knee: FL +1, RR +1, FR -1, RL -1”; the same item says the case team confirms the signs in its mechanical report.
- Change: positive gait knee angle means foot UP, so knee signs are FL −1, FR +1, RL +1, RR −1. All hip signs remain +1. Contract and release notes remain untouched.
- Evidence: `case/reports/mechanical.json`, `servoSigns.kneeLargerPulse`: larger pulses move FL/RR feet DOWN and FR/RL feet UP. With positive `pulseUsPerDegree`, the sealed defaults drove every swing foot down. The lead integration review independently confirmed the shaft-axis geometry.
- Closest verified V0: reverse only the four knee conversion signs in `crab/Config.h`; neutral, trim, GPIO, channels, power rails, motion limits, outline and mounts stay the same. `integration.json` and README now distinguish gait lift from pulse direction.
- Checks: `check.py gait` traces production `Robot::tick` servo angles through the pulse mapping for all eight directions; `check.py pins` compares the actual case sign report with Config.h and integration.json. Both reproduced the old failure before the repair. No physical locomotion claim.
- Cross-team impact: lead must use the corrected knee signs in integrated instructions; case geometry needs no change for this firmware fix. The three separately reported case defects remain for the case team.

## Firmware-owned tunables (not sealed deviations)

- 8000 ms crawl period, 12° hip / 16° knee target amplitude, ±25° absolute servo envelope including trim, 8°/s slow / 24°/s swing and 80°/s² acceleration. One swing leg at a time; target axes use Kame32 oscillator concepts adapted to the contract's adjacent hip/knee channel order.
- Wi-Fi falls back to setup AP after 15 seconds; the owner can re-enter credentials. The saved credential record is atomic, contains no hardcoded network, and is never returned by a handler.
- No sideways-to-turn fallback selected: the planar stance projection test supports requested sideways directions in the simplified model. This is not physical locomotion proof; case joint signs/range and floor behavior remain integration/assembly checks.

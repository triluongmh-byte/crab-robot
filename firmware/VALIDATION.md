# Local firmware validation — 2026-11-06

Builder-local result; independent tester and team integration remain separate.

- Target build: Arduino CLI1.5.1 / ESP32 core2.0.14, ESP32-S3 16MB flash / OPI PSRAM, passed. ELF reports790381 bytes flash and47016 bytes static RAM. Application `.bin`:790752 bytes.
- Binary SHA256: `98097f92abb374282efc0026bfc2350b67aae5f987e423f94764e34d061a5cf9` at `build/firmware/esp32/crab.ino.bin` (rebuilt once for the knee-sign repair).
- Native firmware freshness helper: `firmware_written('.') == True`, `firmware_built('.') == True`. Hash-based copy freshness proof recorded at `build/firmware/esp32/build-proof.json`.
- Full host command: `python3 tools/firmware/check.py` —9/9 groups passed: api, assembly, boot, gait, hardware(register mock), pins, qr, web, wifi.
- Host report: `build/firmware/host/report.json`, with hashes of actual source/test/helper inputs. ASan/UBSan enabled for core and PCA register-mock tests.
- Gait sweep: all8 directions,3 cycles each,10ms sampling; angle65–115°, speed≤24°/s, acceleration≤80°/s² within finite-difference tolerance; at most2 joints above10°/s simultaneously (limit4); one target knee lift at a time. Smooth return to90° checked after stop. Simplified stance projection has expected directional sign; no physical traction/contact claim.
- Regression: both `gait` and `pins` failed with the original signs before repair. All4 production knee outputs now have an upward pulse displacement >80µs in each direction and stay above neutral within1µs tolerance in the model. Positive target lift is checked after sign conversion, rather than counting unsigned knee targets.
- Cross-team evidence: `case/reports/mechanical.json` SHA256 `7d94ec1ccfd54e3f93aa9448af3647125b6b18b1b7c5db19a6ebffb9c90ec1e5`; larger pulses lower FL/RR and raise FR/RL. Corrected knee signs −1/+1/+1/−1 agree with that report and integration.json; hips remain+1. See DEVIATIONS.md for the sealed default reconciliation.
- Wi-Fi tests use mocked radio/NVS and actual state machine: scan UI wiring, wrong-password timeout, success save/reboot join, dropped connection fallback, malformed records/write failure, BOOT reset and clock wrap.
- HTTP tests invoke production Api::handle. Web tests execute production inline JavaScript in Node with mocked DOM/fetch: hold/release, heartbeat, cancellation, visibility, offline, assembly lock, keyboard, SSID text escaping. This is not a real-phone browser test.
- QR tests compile actual target C encoder and independently decode Wi-Fi join + local URLs with ZXing at148x148px /4-module quiet zone. Not a scan through the actual lid.
- PCA tests model NXP register broadcasts: dirty warm-reset registers remain full-off until each scheduled channel is written; prescale,1500µs neutral counts, phase staggering and NACK failure checked.
- Source build input fingerprint unchanged: repeat build command reuses binary; no toolchain installed in worktree.
- All local links in firmware Markdown resolve. Contract hash unchanged. Changes confined to firmware/, tools/firmware/, build/firmware/.
- Actual dummy PCB is present and inspected by `pins`; its pads do not define robot wiring. Fresh native CLI ERC/DRC at severity-all both exit0 (no violations/unconnected items); reports/logs are in `build/firmware/native/`. `kicadpy.verify stale .` reports no stale board inputs.
- Read-only `kicadpy.verify gate .`: sidecar fab.ready=true/errors0/warnings0, native check passed/findings0; stored manufacturing report prototypeReady=false/findings1 (`gerber_silk_line_width`). This pre-existing report discrepancy is for the lead/board team; no gate or board output altered. Firmware completion is not team readiness.
- Three lead-reported case defects remain outside firmware ownership. Real servo direction, traction, closed-lid scanning and fit remain assembly checks. No hardware accessed, flashed, energized, measured, printed or ordered.
- No user blocker. Assembly-only assumptions and the WS2812 remedy change are recorded in CHECKLIST-RAP.md / DEVIATIONS.md for the lead to merge.

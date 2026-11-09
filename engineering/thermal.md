# Thermal and actual copper — integrated V0

U2 TI TLV1117LV33: pad2/tab3V3 is a real filled top copper heat spreader,
not an imagined ground tab. Native thermal command measures its contiguous
polygon and same-net vias (latest build/board/thermal-check.log). After merging
same-net top pours, measured top polygon is3542.498mm² with10same-net vias.
Bottom has a smaller3V3 heat island; most B.Cu is commonGND. No solder-wicking
via-in-pad is used: the ESP EP is solidSMD, paste is windowed, thermal vias
are outside solder pads; drills0.3mm. Top population only.

At5.25V input,3.3V output,415mA continuous estimated load: P=0.809W.
560mA source-reserve transient: P=1.092W. TI's JEDEC θJA62.9°C/W is a reference,
not a measurement of this board. Using +25% layout margin =78.625°C/W gives
estimated rise63.6°C at415mA and85.9°C if560mA were continuous. At40°C local
ambient, estimated junction103.6°C /125.9°C respectively. Thus560mA is a
transient reserve; sustained service must remain≤0.415A in normal operation.
Radio TX budget355mA +display40 +PCA10 +pulls10 meets that design budget.
Full-board copper and thermal vias are present; the closed-body temperature
must be verified on the first assembly, by a competent lab rather than asking
the user to measure electronics. Acceptance: steady QR/web+Wi-Fi and no
thermal cycling, target measured U2 case≤85°C at40°C ambient; if failed,
reduce radio TX duty/LED-backlight control load or revise the oneLDO layout.
No measured temperature or unbounded maximum-current guarantee is claimed.

Servo feed trunk2mm35um copper, ≈70mm routed path estimate:
R≈ρL/(wt)=0.0175×0.070/(2×0.035)=0.0175Ω, at2.4A drop42mV/loss0.101W.
Branches≥1mm carry one servo orLED; GND returns through B.Cu plane and PTH
contacts. Actual native widths are audited, signal minimum0.2mm and USB
supply minimum0.6mm. Connector/wire/contact heating and bank protection are
physical checks, not simulated results. Never feed eight stalled SG90s.

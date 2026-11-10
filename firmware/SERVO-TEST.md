# One-servo neutral/speed experiment

This uses the owned continuous servos as speed-controlled motors. **It cannot hold a joint angle or make the positional walking gait work.** No additional purchase is planned. The current inventory has no servo supply of established rating; the exposed 18650 and unidentified module are not recommended or wired as a supply. A prior polarity reversal also leaves component health uncertain. Resolve the supply before any physical test. Flash permission does not authorize motor operation.

## Controls after the physical prerequisites are met

1. Use exactly one unloaded servo, with its horn and leg removed and its lead free to rotate. Unplug the other servo connectors. Do not run this on an assembled joint.
2. Join `CuaRobot-XXXX` and open `http://192.168.4.1/`. Keep **360° / chưa rõ loại** selected. Exit Assembly with **Xong ráp**, then open **Thử 1 servo**.
3. Select one CH0–7 and check the actual channel shown in the status line before holding a button. The dropdown can show CH0 after a reload while the server retains an earlier channel. Opening the page, changing channel or neutral does not emit pulses.
4. Hold **Giữ tâm** briefly and release. Adjust **Tâm −1 count / Tâm +1 count** within 287–327 and repeat. The ±1 and ±4 buttons compare speeds/directions around neutral. A stable neutral may not exist; stop if it cannot be found. Neutral stop is not position holding.
5. Optional observation aid: briefly hold **Thấp −20 count**, release, then **Cao +20 count** and release. Continuous turning while the pulse remains active suggests continuous rotation. A positional stop may suggest a positional servo, but no motion, a jammed/damaged servo, disabled output or weak supply cannot classify it. Record observations per channel; firmware neither infers nor saves a servo type.
6. Release requests full-off, rather than a neutral pulse. A press is capped at 2000 ms and its keep-alive expires at 500 ms. After expiry, release and press again. Page/session changes, BOOT/inhibit and faults stop the test. **Đóng thử — tắt PWM** closes it.
7. Settings and actuator selection are RAM-only. Reset returns to unknown/off. Never choose **Định vị 180°** for continuous or unidentified servos: that intentionally enables the positional standing/gait pulses.

## Counts and output policy

At nominal 50 Hz, 20000/4096 gives **4.8828125 µs per count**. Prescaler121 and oscillator tolerance are unmeasured. The UI displays integer requested/emitted counts and labels microseconds as nominal, not measured. There is no 1 µs control resolution. 1500 µs rounds to 307 counts, nominal 1499.0234375 µs. A seller's claimed 7 µs deadband is about 1.4 counts and can vary between clones.

Neutral is 287–327 counts. Held offsets are −20, −4, −1, 0, +1, +4 and +20, giving total output bounds of **267–347 counts** (nominal 1303.71–1694.34 µs). At neutral307 the low/high pair is 287/327. Exactly one CH0–7 can emit; the other fifteen channels remain full-off. Mode/channel/new-hold transitions clear outputs before a test pulse. The 2000 ms cap is not extended by keep-alives; ordered session commands reject stale renewal after stop/expiry. Walking and Assembly cannot own outputs while the test is open.

## Limits

Full-off is neither a supply disconnect nor guaranteed braking/holding. The handwired LILYGO has no MCU-controlled OE wire: after an I²C failure it cannot guarantee the PCA receives an off command. The integrated target also asserts its existing OE. Neither can cut servo power. The motion task runs at 10 ms intervals; I²C, scheduler and stalled HTTP-error replies can delay software stopping. These are software limits, not measured hard real-time guarantees. ±20 buttons can also cancel early on a finger scroll/long press.

Host tests exercise the production core, HTTP handlers, output service and PCA registers for both profiles. Real phone/radio, supply, servo health/type, neutral stability, frequency and stopping response remain unverified. No physical motor test or walking result is claimed.

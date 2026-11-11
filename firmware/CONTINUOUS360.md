# Continuous 360° experiment with a manual reference — notes 15/16

The owner keeps eight continuous-rotation SG90s. No purchases or mechanical
conversion are selected. They control speed/direction, with no angle feedback,
homing or angle holding. The robot **does not walk**. Positional startup and
Kame32 gait remain behind the explicit180° setting, unsuitable for these servos.
Drive arrows stay disabled; this is a single-channel open-loop experiment.

Connect to `CuaRobot-XXXX`, browse `http://192.168.4.1/` and manually open
**360° thử nghiệm**. Home Wi-Fi is optional; polling never changes pages.
Original LILYGO is the owner's physical target; integrated remains a separate
build, unmanufactured and unauthorized for flashing. Pins/wiring are unchanged.

No owned servo supply has an established rating. A supply decision is required
before physical tests. Do not use the exposed18650 or unknown boost module as a
recommended supply. Servo health after reported reversed polarity is unknown.
The build never flashes or runs motors. Authorized entry flashing follows [FLASH-POLICY.md](FLASH-POLICY.md); build acceptance alone does not authorize motor commands.

## Configuration and measurement entry (no output)

All16 outputs boot fully off. Select a CH0–7 and configure integer stop/forward/
reverse counts205–409. Defaults307/267/347 are unverified candidates. A stop count
is not a brake and307 is not assumed neutral. Values remain RAM-only. Changing
counts invalidates the reference and clears that channel's measured rates.

One global CW viewpoint starts **pending**. Hip motion refuses until explicitly
set to horn/shaft face or looking down from the body. Neither interpretation is
silently selected or mirrored. Symmetric knee budgets work with pending hip
viewpoint. Changing viewpoint invalidates reference and all direction rates.
Use the selected viewpoint consistently when recording observations; firmware
cannot verify what the owner meant. The owner has not resolved this yet.

Record previously observed unloaded measurements for each channel **and each
CW/CCW direction**: configured count used, observed degrees and elapsed ms.
Rate=degrees/ms at that exact count; a different count requires new measurements.
Forward/reverse labels do not determine CW: assign each count from observations,
including swapping them. Equal counts cannot be both directions. No speed is
inferred from geometry or the seller's0.12s/60deg claim. The form only records
observations; it never emits motion as part of saving calibration. Without real
observations, that direction remains **chưa hiệu chỉnh** and timed moves refuse.
No fabricated example rate is installed by default.

Legacy **Chi tiết → Thử cũ** is an untracked, unloaded-servo diagnostic with the
prior267–347 count/2s limits. It is not a joint-travel control or a shortcut for
the new timed path. Opening or operating it invalidates the manual reference.
Do not use it with legs/horns attached. Measurement entry and the new timed
joint path emit nothing until their reference/calibration gates are satisfied.

## Manual reference and software travel budget

Select the requested jog angle and duration cap before confirmation: changing
either setting invalidates the reference. Physically place every joint in the owner's manual90° reference, then press
**Đã đặt 90°**. This confirms a human action; it does not home or command a servo.
On 2026-11-11 the owner reported placing all eight joints at this manual reference. A new boot still starts unreferenced: the runtime confirmation must be made intentionally after setup. Estimated displacement starts at0
from that pose, not a measured absolute angle. Confirmation leaves PWM off.

Owner-reported contact limits on the old cropped/drilled body, minus a builder-
selected5° margin, determine the budgets. These are hand estimates, not CAD or
loaded collision measurements:

| Channel | Owner CW / CCW | Software CW / CCW |
|---|---|---|
| CH0 / CH2 front hips |30° /60° |25° /55° |
| CH4 / CH6 rear hips |60° /30° |55° /25° |
| CH1 /3 /5 /7 knees |40° /40° |35° /35° |

Hold a CW/CCW estimated jog. Backend derives duration from the measured rate,
clips it to the selected50/100/200/500ms cap and remaining travel budget, or
refuses when less than50ms fits. The compatibility raw-count hold route uses
the same reference, calibration, viewpoint and travel gates; raw neutral pulses
are refused. Only one channel can be active, others fully off. Keepalive cannot
extend the hard duration; missing keepalive stops within500ms. Phone shows the
selected and last emitted counts, committed duration, estimate and clip/refusal
reason. Emitted count history records I2C acknowledgements, not shaft motion.

The estimate integrates commanded time from request acceptance, conservatively
including output scheduling latency. It is not encoder position. At expiry,
release/off/disconnect, settings/calibration/mode/session change, fault,
untracked diagnostics, reset or power loss the reference becomes **invalid**.
Return joints physically to the manual pose and confirm again before another
run. Do not use confirmation as a software shortcut to reset the travel budget.
Saved/RAM calibration never auto-arms; nothing moves at boot or during data entry.

A5° margin and short pulses do not establish safe mechanical travel. Oscillator
error, load, slip, drift and coasting can exceed estimates. PWM-off is not braking
or holding. No loaded leg-step pattern or walking is justified or claimed.
At nominal50Hz/count resolution is4.883µs; prescale121 with assumed25MHz gives
4.88µs/count, about50.03Hz. Clock and pulse width are unmeasured; there is no1µs
resolution. A seller's7µs deadband spans only about1.4counts. Neutral may drift,
differ between clones or be absent.

## Implementation and review

`continuous360.h` is the shared reference/calibration/budget policy. `core.h`
separates it from positional and untracked diagnostics. `actuator_output.h`
checks final count, channel, rate, reference and projected budget before actual
PCA writes. `/360/reference`, `/viewpoint`, `/calibrate` stop before settings;
`/move` replies with duration, estimate and reason outside the mutex. Every
motion command uses one owner and strictly increasing sequence. Session
replacement stops previous output. Faults latch off. Original LILYGO lacks OE:
a broken I2C link cannot guarantee PCA received off; integrated uses GPIO21 OE.
The output task runs every10ms plus RTOS/I2C latency. Real RF/phone behaviour,
stopping, directions, servo health, supply and physical travel are unvalidated.

Fast: `python3 tools/firmware/check.py core drivers http web`.
Full: `python3 tools/firmware/check.py` covers both build profiles, reference
invalidation, uncalibrated/pending gates, both directions of every hip/knee,
actual registers, final limits, expiry, session/settings/off and direct AP.
`python3 tools/firmware/build.py --target all` uses all CPUs and content caching.
The source build generates [BUILD.json](BUILD.json) and [BUILD-integrated.json](BUILD-integrated.json), including binary hashes. The original LILYGO is the only authorized physical target. A private flash packet requires independent review, current motor isolation and a complete verified backup under [FLASH-POLICY.md](FLASH-POLICY.md).

## Owner observations and present validation boundary

On 2026-11-11 the owner reported that all eight installed continuous SG90s worked when tested individually on the original LILYGO/PCA9685 and manually modified printed body. The owner also reported placing the hips and elbows at the manual 90° reference. These reports do not provide calibrated stop/direction counts, direction-specific degrees/ms, measured PWM frequency, supply rating, release-stop response, loaded clearance or walking. They do not test the unmanufactured integrated PCB or establish operation of a later firmware candidate. No calibration or runtime reference is silently created from the reports.

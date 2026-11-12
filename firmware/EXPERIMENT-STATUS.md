# Owned-servo experiment status —2026-11-11

> Historical360° material. The current positional180° release has removed these web/API controls. Use [POSITIONAL180.md](POSITIONAL180.md) for the received replacement motors.

The owner currently has eight continuous-rotation SG90-class servos, a LILYGO T-Display-S3 and external PCA9685. The owner reported that every servo worked individually and had manually set the joints to90° before whole-robot trials. Neither that reference nor equal forward/reverse time supplies actual angle feedback.

## What was tried and observed

| Checkpoint | Implemented behavior | Actual owner report |
|---|---|---|
| Timed crawl | One channel at a time; hip/knee sequence with short saturated pulses | Legs collided after Forward/Backward presses |
| Latest hips-only experiment | Forward FL/CH0 CCW,FR/CH2 CW,RR/CH6 CCW,RL/CH4 CW; Backward inverts all four. Nominal60ms outward stroke then inverse compensation. No knee pulses from these controls. | Erratic jumping/motion; not a usable walking result |

The latest implementation preserves signed ON-time through interrupted presses. The next press only repays an interrupted stroke, with a60ms compensation cap per press; scheduler residual remains an estimate. It does not measure joint angle, determine physical stall/contact, guarantee stopping/holding, or guarantee return to the starting pose.

**ASSUMPTIONS:** rear-left travel also30°; directions viewed into the output shaft; PCA205count CCW/409count CW; nominal30° from60ms based on the seller's no-load0.12s/60° figure. Per-servo loaded direction/rate calibration is not established. No further loaded360° joint trial is recommended from this checkpoint. Hardware work is paused while the owner waits for parts; do not represent a part as ordered or received without confirmation.

## Validation versus hardware outcome

Host core, driver, HTTP and web checks passed for the latest source, including actual PCA register replay: only even hip channels, four concurrent outputs, direction reversal, bounded return, interrupted release/session handling, timing jitter, no knee pulse writes, and deadman shutdown. The LILYGO target compiled and its complete image set was written and byte-verified on the identified owner's ESP32-S3. These tests establish implemented commands, not physical walking or actual30° motion. The new integrated PCB has not been manufactured or tested.

The LED starts on at16/255. All servo outputs start off. Firmware source for the owned modules remains [crab/](crab/); use the LILYGO target, not the future integrated-board image.

## Options for discussion; none implemented here

1. **Keep this jointed-leg mechanism and use positional servos.** This is the most direct continuation. Confirm the delivered variant actually positions its shaft; the label SG90 alone does not distinguish180° positional from360° continuous. Check its mounting fit before replacing all eight. The existing boards, wiring, frame and software can be reused subject to actual fit/power checks.
2. **Use the continuous servos as wheel drives.** Fit wheels and a supporting caster/skid; two drive servos can steer by different speeds. This changes the toy into a wheeled robot and needs mechanical mounting changes, but does not require absolute shaft angles for basic driving.
3. **Use a crank/linkage designed for continuous rotation.** A rotating crank can drive a repeating foot path mechanically. This requires a new linkage, clearance/force checks and printed adapters; it is not a firmware patch to the current independent hip/knee legs.
4. **Inspect one spare motor for possible conversion to positional feedback.** Feasibility depends on its internal circuit, feedback potentiometer coupling and gear parts. Do not assume a factory360° unit can be converted cheaply or reversibly. No servo has been opened or verified for this option.

A fixed travel stop alone does not add angle feedback; repeatedly driving into a stop can stall the motor and load its gears. External sensing is another design project, not selected as a budget fix.

Sources: [Pololu on continuous-rotation versus multi-turn servos](https://www.pololu.com/blog/24/continuous-rotation-servos-and-multi-turn-servos), [Adafruit continuous-rotation overview](https://learn.adafruit.com/adafruit-motor-selection-guide/continuous-rotation-servos), [Adafruit mechanical conversion example](https://learn.adafruit.com/modifying-servos-for-continuous-rotation). Mechanical alternatives above are proposals, not checked CAD or demonstrated robot performance.

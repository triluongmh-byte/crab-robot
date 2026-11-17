# Front sonar head (+Y face, under the screen)

This is one printed PETG part. It holds both HC-SR04P modules on the **+Y face**, the side the crab walks toward on **↑ Tiến** (owner, 2026-11-17). It sits below the screen stand, so nothing sticks up past the screen. It replaces `../sonar_bracket`, which was made for the −X end and is now obsolete.

**Status:** not printed and not tested on hardware. All the evidence comes from CAD and the slicer.

## What you need

- 2 zip ties, 2.5 mm wide. They go around the +Y side rail of frame_upper.
- 4 M2×6 self-tapping screws, two per module, for the two holes on the header edge. M2 is not in the kit.

## Fitting

1. **Do this on the bench, before the part goes on the robot.** Once it is on the robot, the frame blocks the screwdriver for the left top screw.
   - Push each module in from behind. The cans go through the holes, the inner edge rests on the shelf, and the 4-pin header points outwards (toward ±X).
   - Fit the two screws from behind. You reach the top screw through the round channel in the back plate.
2. Hold the plate flat against the outside face of the +Y side rail, centred (the ties sit at x ±12, between the rim posts).
   - Thread the two zip ties through the slots and around the rail, then pull them tight.
   - Plug in the Dupont leads after the part is on, so they bend away from the front feet.
3. **Left module** (−X: on your left when you stand behind the crab facing Tiến) goes to GPIO10/11. **Right module** goes to GPIO12/13. Both take 3V and G. To check which is which, cover one sensor and watch which reading changes.

## Geometry (robot / CAD frame)

| | |
|---|---|
| Modules | Each stands on its end with the cans one above the other. Turned 15° outwards from straight ahead and tilted up 10°. |
| Can centres | Upper cans 56 mm above the floor, lower cans 31 mm. x ±16–17, y 60–65. |
| Part bounding box | x ±26, y 37.2–59.7, z 2.2–48.5. The top is 3.6 mm below the front-bottom edge of the screen cradle. About 19 mm off the floor when standing. |
| Print | Upside down, with the flat top web on the bed. No support. **1 h 03 min, 6.8 g** (A1, 0.4 mm, repo PETG profile). |

**Why 15° and not 25°.** At 20° or more, the beams see the crab's own front feet at the end of every trot step (hip 25°). At 15° they don't, as long as Bù lệch (balance) stays at 0. Above about ±20 % balance, the hip reaches 27.5–32.5° and a foot can show up 30–70 mm ahead. A near-range echo filter in the firmware would handle that.

**Lying down.** The built-in Ngủ pose lifts all four knees 30° and lowers the body 16.2 mm. The bottom of the part then sits 2.5 mm above the floor. A custom emotion that lifts all four knees further would put the crab's belly on this part, so keep all-four lifts at 30° or less.

## Checks (`check_fit.py` → `fit_report.json`, all pass)

- **Static:** no overlap with frame_upper, the 12 servos, the screws, the screen stand, the LILYGO, or its USB-C plug and Dupont rows.
  - The closest gaps are 0.23 mm to the stand and 0.25 mm from the plate to the rail face.
  - The zip ties wrap the rail and pass through the slots.
  - frame_lower is not fitted, so it is not checked.
  - The `electronics` reference (the future integrated board) is not checked either. Its USB-C plug model would sit in the right module's wire path.
- **Modules in the holder:** no overlap.
  - A 5 mm screwdriver reaches all four screws on the bench.
  - The walls between the tie slots and the screwdriver channels are at least 1.96 mm.
- **Leg sweep:** 478 poses of the two +Y legs (CAD FL and RL), inside the firmware limits.
  - Walking: hip up to 32.5°, knee lift 0 to −60°.
  - Poses: hip ±30°, knee −100 to +30°.
  - The part, modules and ties stay at least 8.7 mm clear.
  - The Dupont plug envelope stays 1.05 mm clear at hip 30° with the knee pressed fully down (pose only). The wires bend there.
- **Beams:**
  - The 15° cones stay clear of the part, the frame and the stand.
  - The lower beam reaches the floor 350 mm ahead.
  - No foot is seen while walking at balance 0.
- **Ngủ pose:** 2.5 mm above the floor.

## Files

| File | What it is |
|---|---|
| `sonar_front.py` | CadQuery source. Every dimension is in `Params`. `gen_step()` returns the part in print orientation. |
| `sonar_front.step` / `sonar_front_print.stl` | The part in print orientation. |
| `sonar_front.3mf` | Unsliced Bambu Studio project, repo PETG profile. |
| `sonar_front_with_sensors.step` | The part with both modules fitted, in the robot frame. |
| `sonar_front_fit_preview.step` | The same, plus frame_upper, servos, legs, screen stand, LILYGO and ties. |
| `check_fit.py`, `make_3mf.py` | Checks, and the 3MF writer (add `--slice DIR` to slice offline). They never contact a printer. |

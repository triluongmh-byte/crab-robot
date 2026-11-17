# Front sonar head: two rows on the +Y face, under the screen

This is one printed PETG part. It holds both HC-SR04P modules on the **+Y face**, the side the crab walks toward on **↑ Tiến**. It sits under the screen stand.

- The modules lie flat, one above the other, so the four "eyes" form two rows of two, like a face.
- This replaces the first upright version (PR #43) and `../sonar_bracket`, which was made for the −X end.

**Status:** not printed and not tested on hardware. All the evidence comes from CAD and the slicer.

## Why two rows and not one row of four

One row of four is about 94 mm wide (x ±47). The front legs leave only about ±36 mm free in front of this face. Every position tried (yaw 0–20°, 40–70 mm out, 12–26 mm up) either hit a hip servo or the frame, or a front leg while walking. On top of that, the outer cans looked straight at the front feet on every step. Each of the two rows is 49 mm wide and fits.

## What you need

- 2 zip ties, 2.5 mm wide, around the +Y side rail of frame_upper.
- 4 M2×6 self-tapping screws, two per module, for the holes on the header edge. M2 is not in the kit.
- **Bend the 4 header pins of each module 90° backwards** (away from the cans) with pliers. The HC-SR04P header points out of the long edge in the PCB plane.
  - Unbent, the upper plug would stick up in front of the screen and the lower one would drag on the floor.
  - Bent, both Dupont plugs go back toward the body.

## Fitting

1. **On the bench, before the part goes on the robot.**
   - Push each module in from behind. The cans go through the holes and the inner edge rests on the middle beam.
   - **Upper row:** header on top. **Lower row:** header at the bottom.
   - Fit the two screws per module from behind. Channels in the back plate let the screwdriver reach.
2. Hold the plate flat against the outside face of the +Y side rail, centred.
   - Thread the two zip ties (x ±12) through the slots and around the rail, then pull them tight.
   - Plug the Dupont leads in. The upper leads go back over the top, the lower leads go back underneath.
3. Wiring:

   | Module | Points | Pins |
   |---|---|---|
   | Upper | 15° to the left (−X, your left when you stand behind the crab facing Tiến) | GPIO10/11, the left sensor |
   | Lower | 15° to the right | GPIO12/13 |

   Both take 3V and G. To check, cover one sensor and watch which reading changes.

## Geometry (robot / CAD frame)

| | |
|---|---|
| Rows | Each module lies flat with its cans side by side. The rows are turned ±15° and both tilted up 10°. They cross at x = 0. |
| Can centres | Upper row 59.5 mm above the floor, lower row 36 mm. x −16…+16, y 68–74. |
| Part bounding box | x ±25, y 37.2–71.3, z 7.3–51.0. The top is 1.1 mm below the screen's bottom edge. It is in front of the stand (y ≥ 37.25 vs ≤ 37.02), so nothing covers the display. |
| Print | Upside down, top plane on the bed. **1 h 09 min, 11.5 g** (A1, 0.4 mm, repo PETG profile). Tree support only under the ramp at the front where the crossed rows meet; it comes off from the front. |

**Why 15°.** At 20° or more, the beams see the crab's own front feet at the end of every trot step (hip 25°). At 15° they don't, as long as Bù lệch stays at 0.

## Checks (`check_fit.py` → `fit_report.json`, all pass)

- **Static:**
  - No overlap with frame_upper, the 12 servos, the screws, the screen stand, the LILYGO, or its USB-C plug and Dupont rows.
  - Closest gaps: 0.23 mm to the stand, and 0.25 mm from the plate to the rail face.
  - The zip ties wrap the rail and pass through the slots.
- **Modules:**
  - No overlap with the part or with each other, including the bent-back plugs.
  - A 5 mm screwdriver reaches all four screws on the bench.
  - The tie-slot walls are at least 2 mm thick.
- **Leg sweep:** 478 poses of the two +Y legs within the firmware limits.
  - Walking: hip up to 32.5°, knee lift 0 to −60°.
  - Poses: hip ±30°, knee −100 to +30°.
  - Everything stays at least **13.5 mm** clear.
- **Beams:**
  - The 15° cones stay clear of the part, the other module, the frame and the stand.
  - No foot is seen while walking at balance 0.
  - The lower beam reaches the floor 414 mm ahead.
- **Ngủ pose** (all four knees lift 30°): the part sits 7.7 mm above the floor and the lower plug 1.75 mm.
- **Not checked:** frame_lower (not fitted), and the future integrated board's USB-C plug (the `electronics` reference).

## Files

| File | What it is |
|---|---|
| `sonar_front.py` | CadQuery source. Every dimension is in `Params`. `gen_step()` returns the part in print orientation. |
| `sonar_front.step` / `sonar_front_print.stl` | The part in print orientation. |
| `sonar_front.3mf` | Unsliced Bambu Studio project, repo PETG profile, support on. |
| `sonar_front_with_sensors.step` | The part with both modules fitted (pins bent back), in the robot frame. |
| `sonar_front_fit_preview.step` | The same, plus frame_upper, servos, legs, screen stand, LILYGO and ties. |
| `check_fit.py`, `make_3mf.py` | Checks, and the 3MF writer (add `--slice DIR` to slice offline). They never contact a printer. |

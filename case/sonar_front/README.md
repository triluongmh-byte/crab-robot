# Front sonar head: V of two modules, four eyes in a row (+Y face, under the screen)

This is one printed PETG part. It holds both HC-SR04P modules on the **+Y face**, the side the crab walks toward on **↑ Tiến**, just under the screen.

The owner's layout (2026-11-17, photo IMG_2728): seen from above, the head is an **isosceles triangle**.
- The back plate along the side rail is the base.
- The two modules lying flat are the equal sides. They meet at the apex in front of x = 0.
- From the front, the four "eyes" are in one row.

This replaces the earlier versions (PR #43 upright, PR #44 two rows) and `../sonar_bracket` (−X end).

**Status:** not printed and not tested on hardware. All the evidence comes from CAD and the slicer.

## Angle

Each module is turned **12° outwards** and tilted **8° up**.
- The two beams (±15° each) cover −27° to +27°. They overlap by 6° straight ahead, so both sensors see an obstacle dead ahead. Above 15° there would be a blind gap in the middle.
- The beams' lower edges reach the floor about 400 mm ahead.

## What you need

- 2 zip ties, 2.5 mm wide, around the +Y side rail of frame_upper. You can glue (502) as well.
- 4 M2×6 self-tapping screws, two per module, for the holes on the header edge. A drop of glue also works. M2 is not in the kit.
- No pin bending: the header points down, as when you held the module up to the face, and the Dupont plugs hang below the head.

## Fitting

1. Push each module in from behind with the header at the bottom: the cans go through the holes and the top edge goes under the shelf. Fit the screws, or glue.
2. Hold the plate flat against the outside face of the +Y side rail, centred. Thread the two zip ties (x ±12) through the slots and around the rail, then pull them tight.
3. Plug in the Dupont leads (they hang down) and run the wires back under the body.
   - **Left module** (−X, your left when you stand behind the crab facing Tiến, looking left): GPIO10/11.
   - **Right module:** GPIO12/13.
   - Both take 3V and G. To check, cover one sensor and watch which reading changes.

## Geometry (robot / CAD frame)

| | |
|---|---|
| Part bounding box | x ±49.5, y 37.25–59.4, z 20.4–43.0. The top is 9 mm under the screen's bottom edge. |
| Can centres | 49 mm above the floor. x ±14 (inner) and ±39 (outer). |
| Dupont plugs | Hang down to z 3. In the Ngủ pose they are 3.4 mm above the floor; the part itself is 20.8 mm above it. |
| Print | Upside down, top plane on the bed. **No support. 37 min, 8.6 g** (A1, 0.4 mm, repo PETG profile). |

## Checks (`check_fit.py` → `fit_report.json`)

**Pass:**
- **Static:**
  - No overlap with frame_upper, the 12 servos, the screws, the screen stand, the LILYGO, or its USB-C plug and Dupont rows.
  - Closest gaps are 0.2 mm (a frame screw head) and 0.25 mm (plate to rail face).
  - The zip ties wrap the rail and pass through the slots.
- **Modules:**
  - No overlap with the part or with each other.
  - A 5 mm screwdriver reaches all four screws.
- **Beams:**
  - The cones stay clear of the part, the other module, the frame and the stand.
  - The floor is about 400 mm ahead.
- **Ngủ pose:** see Geometry.

**Information only (owner override):**
- In the CAD leg model, the front foot or knee servo reaches the outer can when the hip steps 25° forward (both walking and poses).
- In that pose the outer beams see that foot at about 1 cm.
- This happens at every V angle tried (0–15°), because the row is ±47 mm wide.
- The owner measured the real robot and it does not touch, so these results are recorded in `fit_report.json` and do not gate the check.
- If the feet do show up in the readings, a firmware filter for echoes under about 5 cm would remove them.

## Files

| File | What it is |
|---|---|
| `sonar_front.py` | CadQuery source. Every dimension is in `Params`. `gen_step()` returns the part in print orientation. |
| `sonar_front.step` / `sonar_front_print.stl` | The part in print orientation. |
| `sonar_front.3mf` | Unsliced Bambu Studio project, repo PETG profile. |
| `sonar_front_with_sensors.step` | The part with both modules fitted, in the robot frame. |
| `sonar_front_fit_preview.step` | The same, plus frame_upper, servos, legs, screen stand, LILYGO and ties. |
| `check_fit.py`, `make_3mf.py` | Checks, and the 3MF writer (add `--slice DIR` to slice offline). They never contact a printer. |

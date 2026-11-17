# Sonar turret (accessory): two HC-SR04P back to back on a rotating SG90

This is an **optional add-on**. The crab's eyes stay the [fixed front sonar head](../sonar_front/README.md). When Tự đi meets an obstacle, the crab turns its whole body on the spot to look for a free way, so it needs no turret to find its path (owner, 2026-11-17, after watching other crab robots).

The turret is kept for later toys: a security-camera-style sweep, a camera mount, and so on. It is two printed parts and one spare SG90.

**Status:** not printed and not tested on hardware. The firmware does not drive CH8 yet. All the evidence comes from CAD (`check_fit.py`) and the slicer.

## What it is

```
            ◯◯ ═[ cradle ]═ ◯◯       front module GPIO10/11 | back module GPIO12/13
                  ┌──┴──┐           header UP: Dupont plugs on top, wires loop down with slack
                  │SG90 │  CH8      sweeps ±90°, so the two modules together see 360°
             ┌────┴─────┴────┐  ← column: the SG90 drops in, tabs screwed on top
             │  pedestal     │     cable slot at the bottom of both ends
        ═════╧═══════════════╧═════  ← glue pad, 502 on the orange centre strip
```

- **Column.** It is glued (502 / cyanoacrylate) on the flat orange centre strip of `frame_upper`, between the LILYGO and the wire bundle. The owner chose that place on 2026-11-17 (photo IMG_2736).
  - The pad is 34.3 × 18.8 mm.
  - The SG90 body stands on the pocket floor. Its tabs sit on the column top and are fixed with the two screws that come with the servo.
- **Cradle.**
  - The double-arm or cross horn goes into a cross recess under the disc. Glue it with 502.
  - Both module PCBs drop into slots in the two end posts, backs facing each other, header up. A front lip runs along each PCB's bottom edge. A rubber band in the notches on the post tops, or a drop of 502 in each slot, keeps them in.
- **Height.** The rotating head clears the owner's tidied wire bundle, which stands 45 mm above the frame top.
  - The underside of the head is 51 mm above the frame top.
  - The can centres are 64 mm above the frame top and 127 mm above the floor.

## Print

`sonar_turret.3mf` holds both parts on one plate. It uses the repo PETG profile (A1, 0.4 mm), with **no support**.
- The column stands on its pad.
- The cradle lies on its disc.

The offline Bambu Studio CLI slice gives **53 min and 11.8 g**. That is a slicer estimate.

## Fit

1. **Centre the SG90 first.** The firmware does not drive CH8 yet.
   1. Unplug one leg servo from the PCA, e.g. CH0.
   2. Plug the turret SG90 into that socket and tap **Ráp**. Every channel goes to 1500 µs.
   3. Plug the leg back afterwards.
2. Glue the horn into the cradle recess with 502, then push the horn onto the spline. The modules must face front and back (Tiến / Lùi).
3. Fix the horn screw through the centre hole. This must happen **before** the modules go in.
4. Drop the SG90 into the column, run its cable out of a bottom slot, and screw the tabs down.
5. Glue the column pad onto the orange centre strip with 502.
6. Slide both modules into the slots, header up, with the cans facing outwards.
   - Plug in the Dupont leads and leave a loose loop so ±90° of turning never pulls them.
   - Front module: GPIO10/11. Back module: GPIO12/13.
   - Both modules take 3V and G.

## Checks (`check_fit.py` → `fit_report.json`)

All of these pass:
- **Fit.**
  - The column and the turret SG90 do not overlap frame_upper, the leg servos, the screws or the legs.
  - The pad sits on the spine top.
- **Turret sweep.** From −90° to +90° in 15° steps, the cradle, modules and plugs keep at least 1 mm from everything fixed. The closest gap is 1.7 mm, between the cradle and the turret SG90's own top.
- **Wire bundle.** The head is 51 mm above the frame top; the bundle is 45 mm.
- **Legs.** No pose reaches the head at turret angles −90, −45, 0, 45 and 90. The poses tested cover every corner:
  - hips at ±40;
  - knee lifted up to 150, the v34 Chào pose;
  - knee pressed down to 55.
- **Beams.**
  - Both beams stay clear of the body and the standing legs at every angle.
  - At 25 cm a beam sees things taller than about 60 mm.
  - Its lower edge reaches the floor at about 47 cm.

## Files

| File | What it is |
|---|---|
| `sonar_turret.py` | CadQuery source. Every dimension is in `Params`, checked by `validate()`. `column_print()` and `cradle_print()` give the parts in print orientation. |
| `check_fit.py` | The checks above. It writes `fit_report.json` and `sonar_turret_fit_preview.step` / `.glb` (robot frame, with the beams). |
| `make_3mf.py` | Writes `sonar_turret.3mf` and the two STLs. Add `--slice DIR` to slice offline. It never contacts a printer. |

The generated STEP, STL and 3MF files are not in Git. Run the two scripts to make them.

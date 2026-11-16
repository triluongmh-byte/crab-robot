# Power tray (A1V4-r5 open frame)

This is a printed PETG tray that drops into the `frame_lower` bay. It holds the battery parts that used to hang taped under the body. With them inside, `frame_lower` can be fitted again. You do not reprint either frame, and the ground clearance stays the same, because the tray rests on the existing floor bars (top z = 3).

A second small part, the **switch holder**, is a flat plate with a snap-in cut-out. You zip-tie it against any 3 mm frame bar you like.

**Status:** not printed and not tested on the robot. All the evidence comes from CAD (`check_fit.py`) and the slicer.

## What goes where

All positions are in robot-frame mm: +X is the old power-bank mouth, which is the rear when walking; +Y is left.

| Part | Owner's size (ruler) | Pocket | Held by |
|---|---|---|---|
| 1×18650 holder | 79 × 21 × 25 | along X on the centreline (y −19…+2.6), walls 10 mm | 2 zip ties over the top, at x = ±12 |
| 1S charge/boost module | 25 × 20 × 25 | +Y side, x 6.4…32, **+X end open** | snug 3-wall pocket and double-sided tape |
| LiPo for the LILYGO (30 × 26 × 8) | 30 × 26 × 8 | standing on edge, +Y side, x −31.5…−0.9 | 1 zip tie at x = −21.5 |
| Switch (body 20 × 14 × 22) | — | separate switch holder, 20.3 × 14.3 cut-out in a 2 mm plate | 4 slots, 2 zip ties around a frame bar |
| 1000 µF capacitor | 42 mm leads | none: it stays on the PCA screw terminal | — |

- **Charging without taking anything apart.** The module's USB-C end faces +X. A plug goes straight in through the old bank mouth under the deck, and `check_fit.py` checks that path.
- **Fixing the tray to the frame.** Two more zip ties each go down one slot, under the floor bar at x = 0, and up the other slot. They are at y −22.3 and y +5.6.
- **Wires leave over the top.** The bay is open up to `frame_upper`. The holder end walls have 6 × 5 mm notches for its leads.

## Assumptions (GIẢ ĐỊNH)

- **Sizes are ruler readings.** All the sizes above are the owner's ruler measurements from 2026-11-16, not calipers. Each pocket has 0.6 mm total clearance, and the fit check inflates every part by 0.75 mm per side.
- **Module.** Its USB-C is assumed to be on a 20 mm end, facing +X, about 3.5 mm above the tray floor. If yours is different, change `module` / `module_x0` in `Params`.
- **Switch.** The 20 × 14 is assumed to be the body that passes through the panel, with snap clips that grip a 1.5–2 mm panel. If it is loose, reprint with a smaller `switch_fit`.
- **LILYGO and PCA9685 stay on top of `frame_upper`.** Nothing of theirs hangs into the belly. The tallest part in the tray, the LiPo standing on edge, reaches z 31.4.
- **Antenna.** The LILYGO antenna end is not modelled. Keep the 18650 and the LiPo away from it if you can; the Wi-Fi is already weak (about −75 dBm).

## Checks (`check_fit.py` → `fit_report.json`)

These run with real solids from `case/robot/*.step`. All of them pass:

- **Seated.** The tray and every part envelope (+0.75 mm) have zero overlap with `frame_lower`, `frame_upper` and the servos. The tray floor touches the floor bars, with a gap of 0.
- **Drop-in path.** The tray and every part envelope are lowered from z 34.9 to their seats in 0.5 mm steps, with no contact with `frame_lower`. A negative test confirms the check catches a fault: shifting the tray 4 mm in X, or 2 or 3 mm in Y, hits the inner deck bars and the board seats.
- **USB-C.** A 12.5 × 7 mm plug path from the module end out to x 75 is clear of both frames, the servos and the tray.

The +Y edge is tight: 0.4 mm to the deck rail line on the way in. If it catches, take 0.5 mm off that edge with a file.

## Print

`power_tray.3mf` holds both parts on one plate. It uses the repo profile (`case/print-settings.json`, A1 0.4 mm, PETG), with supports turned off: the tie grooves under the tray have 45° sides and a 2.6 mm bridge, and tree supports inside them would block the ties.

The offline Bambu Studio CLI slice gives **42 min and 18.1 g** for both parts. That is a slicer estimate, not a measured time.

## Assembly

1. Print the plate, flat as exported. The tray floor goes on the bed.
2. Put the tray into the `frame_lower` bay from above, with the module's open end toward the bank mouth (+X). The floor rests on the floor bars.
3. Thread the two tie-down ties around the floor bar at x = 0 and pull them tight.
4. Fit the 18650 holder and tie it with 2 ties. Stand the LiPo on edge and tie it with 1 tie. Stick the module down with double-sided tape, USB-C toward +X.
5. Route the wires up out of the bay. Then fit `frame_upper` with its 3 M3×12 joint screws.
6. Fit the switch into the switch holder, and zip-tie the holder to a frame bar where you want the switch.

You need **5 zip ties for the tray, 2 for the switch holder**, all 2.5 mm wide.

## Regenerate

`check_fit.py` needs the `case/robot/*.step` exports from `./build.sh`. If this checkout has none, set `CRAB_CASE_EXPORTS` to another checkout's `case/` folder.

```sh
python3 ~/.claude/skills/cadcode/scripts/cad "$PWD/case/power_tray/power_tray.py"
CRAB_CASE_EXPORTS=/path/to/case python3 case/power_tray/check_fit.py
python3 case/power_tray/make_3mf.py --slice /tmp/tray_slice
```

The generated `*.step`, `*.stl` and `*.3mf` files are gitignored.

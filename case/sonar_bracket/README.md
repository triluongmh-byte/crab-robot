# Twin HC-SR04P sonar head (A1V4-r5 open frame)

> **OBSOLETE (2026-11-17).** This part was made for the −X end. The crab now walks toward +Y (Tiến), so the sonars sit on that face: use [`../sonar_front`](../sonar_front/README.md) instead.

This is one printed PETG part. It holds the two HC-SR04P modules for Auto mode (`positional180-v22`) on the robot's walking front. You do not reprint the body or drill it. You need **two 2.5 mm zip ties** and **four M2×6 self-tapping screws** (two per module). M2 is **not** in the owner's kit, so buy them.

**Status:** not printed and not tested on hardware. All the evidence comes from CAD and the slicer.

## Files

| File | What it is |
|---|---|
| `sonar_bracket.py` | CadQuery source. Every dimension is in `Params`. `gen_step()` returns the part in print orientation. |
| `sonar_bracket.step` / `.stl` | The part in print orientation: upside down, with the bezel tops on the bed. |
| `sonar_bracket.3mf` | Unsliced Bambu Studio project. It uses the repo's A1 / 0.4 mm / calibrated PETG profile (`case/print-settings.json`). |
| `sonar_bracket_fit_preview.step` | Robot-frame preview: bracket, both module envelopes, ties, USB cable, both frames, and the front hip servos and legs at neutral. |
| `check_fit.py` → `fit_report.json` | Static fit, leg-sweep, wide-hip, beam-cone and cable checks. |
| `make_preview.py` | Writes `sonar_bracket_with_sensors.step`: the bracket with both HC-SR04P modules fitted, no robot body, for review. The 3MF holds only the printed bracket. |
| `make_3mf.py` | Writes the 3MF. Add `--slice DIR` to slice offline with the Bambu Studio CLI. It never contacts a printer. |

The repo `.gitignore` ignores `*.step`, `*.stl` and `*.3mf`, so the generated files will not show up in `git status`. Use `git add -f` if you want to commit them.

Regenerate with these commands. `check_fit.py` needs the `case/robot/*.step` exports from `./build.sh`. If this checkout has none, point `CRAB_CASE_EXPORTS` at another checkout's `case/` folder.

```sh
python3 ~/.claude/skills/cadcode/scripts/cad "$PWD/case/sonar_bracket/sonar_bracket.py"
python3 case/sonar_bracket/check_fit.py
python3 case/sonar_bracket/make_3mf.py
```

## Which end is the front

The front is **CAD −X**, the end opposite the bank opening. Note that `model.py` calls −X "rear".

The evidence:

- `tools/case/route_check.py` `HEADER_REFS` and the original map in `firmware/WIRING.md` put CH0/1 on FL and CH2/3 on FR, both at +X. They put CH4/5 on RL and CH6/7 on RR, both at −X.
- Firmware v17+ sets `FRONT_IS_CH46=true`, so ↑ Tiến walks toward CH4/CH6. That is the −X end.
- Viewed facing −X, CAD RL (CH4) is front-right and RR (CH6) is front-left. CAD FL (CH0) becomes rear-right. This matches the owner's note "CH0 at the rear right" and the v17 table.
- Caveat: this assumes the servo plugs follow the CAD channel map. The owner's observation was made on the earlier orange body.

The bracket does **not** fit the +X end. Its lower zip ties pass under the deck end bar, and at +X the power bank sits 0.5 mm below that bar. It would also block the bank slide-out.

## How it mounts (−X end)

The two ends of the frame are not identical, and the only existing M3 hole near this end is J3 at (−36.9, −34.3). So the part clamps the two end bars:

1. **Hook.** A 3.2 mm lip (11 mm wide) rests on top of the frame_upper outer end bar (x −63…−60, top z 39.9). A 45° gusset sits above it. The lip stops 0.65 mm short of the hip servo tabs and is narrower than the 11.8 mm gap between the two front hip servos.
2. **Base.** A 16 × 9 mm block bears on the faces of the upper end bar and the frame_lower deck end bar (z 18.5–21.5).
3. **Two zip ties.** Each 2.5 mm tie (≤ 1.3 mm thick, ≥ 100 mm long) loops around the deck end bar through two slots in the base. The slots sit just above and just below the bar, at |y| = 2.4. That puts the ties in the servo gap and clear of the USB-A plug and adapter envelopes in the rear bay (0.35 mm).
   - The upper end bar cannot take a tie: it is 0.65 mm from the servo bodies and fused to the saddles.
4. **Mast.** An 8 × 9 mm mast rises in the free corridor between the two front thigh hubs (|y| < 13.8). It carries the V head above the leg envelope.

**Assembly sequence:**

1. Do wiring step 7 first.
2. Lay the USB cable and any leads across the end window.
3. Hang the hook on the end bar.
4. Fit and tighten the two ties, buckles on the front of the base.
5. Push each module in from behind, cans through the bezel holes, **header edge up**.
   - `model.py` calls −X "rear", so read left/right as seen walking forward. The walking-left module sits at CAD −Y, on the RR/CH6 side. It faces +25° (toward walking-left) and is wired to GPIO10/11. The walking-right module sits at CAD +Y (RL/CH4 side), faces −25° and goes to GPIO12/13 (`firmware/README.md` v22). `fit_report.json` `beams` confirms this: the CAD −Y cans have `yawDegTowardRobotLeft` = +25.
6. Drive an M2×6 self-tapper through each upper PCB corner hole (from the back) into its boss. **These screws are the retention.** Nothing else stops the PCB from sliding back out of the bezel. Engagement is 2.0 mm bezel + 2.4 mm boss = 4.4 mm, which is 2.2 × d.
7. Plug in the Dupont leads.
8. Run the wires down the mast to the end window, and tie them to the mast.

The bracket has an open channel behind its base, with a 45° floor (plus a 0.4 mm flat at the back face that keeps 1.6 mm of wall over the upper tie slot). The port-1 USB cable (D29) now crosses the end window at z ≈ 30.6 instead of 26. It still runs at z 28 under the centre saddle. Leads also fit through the channel, but servo plugs do not. So for hip/knee leads, "route B around the −X end" only works if the plug was routed before the bracket was fitted. Every lead still has its other route.

## Geometry and assumptions

**Aim:**
- The left module faces **+25°** (toward robot left) and the right module **−25°**.
- Both are pitched **5° up**.
- Both sit at the same height. Can centres are at z 79.8, which is **96 mm above the floor** at neutral (the floor is at z −16.5).

**Why the head sits high and pitched up:**
- With the lower edge of a ±15° beam (taken as the half-angle, which is conservative) at −10°, the floor first enters the cone at **≈ 550 mm**. That is beyond the 45 cm veer and 25 cm halt thresholds.
- At pitch 0 it would enter at ≈ 360 mm, which would trigger constant false veers.
- A body-height mount (eye about 26 mm above the floor) would see the floor at about 150 mm.
- Above the legs, two 45 mm boards in a V fit. In front of the body there is only |y| < 39 below z 42 and |y| < 16 above z 46, which is too narrow.

**Module holder:**
- Bezel 2 mm thick, with Ø16.3 can holes. The holes have a truncated teardrop at the bottom because the part prints upside down.
- The centre between the cans is open ±6.2 mm for the crystal and the header.
- End lips locate the 45 mm PCB with 0.2 mm clearance at each end.
- A 45° beam under the bezel ties everything together.
- Modules are mounted **header edge up**. Straight Dupont housings need 18 mm above the head, which is free space.
- A straight back-pointing header also clears: its plug is 4.1 mm from the part.

**HC-SR04P dimensions (GIA DINH, assumed).** step.parts had no HC-SR04 model; four searches found nothing. These values are from common drawings or a forum measurement, so check them with calipers:

| Feature | Assumed value |
|---|---|
| PCB | 45 × 20 × 1.6 mm |
| Cans | Ø16 × 12 mm, 26 mm apart |
| Back components | ≤ 3 mm |
| Corner holes | 42 × 17 mm pitch |
| Crystal | 11.4 × 4.7 mm, on the front between the cans |
| Header | 4-pin right-angle, centred on a long edge |

The cans only locate the module; the two M2 screws hold it. M2 is **not** in the owner's kit (`hardware.py` has only M3 plus SG90 bag screws). Until you have them, a drop of hot glue between each can rim and the bezel is a stopgap, not the design.

**Overall size:**
- In the robot frame the part spans x −72.2…−44.4, |y| ≤ 46.4 and z 13.8…88.7.
- The can faces reach 11 mm in front of the end face.
- With the plugs fitted, the robot is about 124 mm tall from the floor.

## Check results (`fit_report.json`)

**Static fit.** At neutral there are no unintended overlaps. The checks covered both frames, all servos, the M3/SG90 screws and the electronics envelopes.
- The only contacts are the intended ones: the bracket on the two end bars, and the ties wrapping the deck bar.
- Closest other parts: front hip servo bodies 0.6 mm, rear-bay plug envelopes 0.35 mm (ties).
- Modules sit in the holder with zero overlap. Cans clear the holes by 0.15 mm.
- The re-routed USB cable (Ø4.5, assumed) clears the bracket by 0.36 mm and the frame by 0.35 mm.

**Trot / turning sweep.** 98 poses per front leg: hip −30…+30° by 10, knee −35…+35° including the 35° lift.
- No collisions.
- Minimum clearance is **3.97 mm**, between the thigh top and the underside of the head.

**Wide hip angles (former flick gait, removed in firmware v23).**
- In this CAD the two front legs hit **each other** from a hip angle of 60° forward; the bracket is first touched at 65°. The trot only uses ±30°, so this no longer matters unless a wide-hip pose or emotion is added.

**Beams.** The checks modelled 15° half-angle cones, 600 mm long, from each can face.
- Nothing static in the cones: bracket, other module, frames, servos or electronics.
- No front-leg part entered a cone over a hip −30…30 × knee −35/0/35 grid.

**Model limits.** These checks use the robot exports dated 10 Nov in `crab-robot-v17g/case/robot`; that checkout's `model.py`, `hardware.py` and `build.py` are byte-identical to this worktree's. They test real solids at sampled poses only. They do not cover continuous motion, cable stiffness or real part tolerances.

## Print (Bambu A1, 0.4 mm, PETG)

- Print **upside down**, as exported: the bezel tops are on the plate and the mast points up.
- Use the repo profile (0.20 mm layers, 2 walls, 7% grid infill, tree supports, auto brim). Keep the brim: the bed contact is two 2 mm strips under a 75 mm tall part.
- Offline slice with the Bambu Studio CLI (`make_3mf.py --slice`): **1 h 27 min, 7.95 g**. That includes about 1 g of small tree supports under the four can-hole tips and the mast root. Slicer estimates are not measured times.
- The `gcode` skill's validator then checked the extracted plain G-code: no errors. Its wrapper profile only accepts orcaslicer/prusa/cura backends, so the wrapper is labelled `orcaslicer`; it was used for validation only, not slicing. Bambu Studio also flags `bed_temperature_too_high_than_filament` for the repo's 70 °C PETG bed, which is the owner's calibrated value. Bambu's own `M`/`G` extension commands are listed as unknown, and the A1 park and wipe moves to X −48.2 / Z −1.0 were allowed for.
- Nothing was sent to a printer.
- Walls: every wall, beam and web is ≥ 1.6 mm. `validate()` asserts the tie-slot ledge (1.6 mm), the bezel strip between each can hole and the header edge (1.62 mm after the print-face trim), and the boss engagement. A per-layer scan of the STL (morphological opening, 0.05 mm pixels) found only these below 1.56 mm:
  - the knife-edge cusps where each can hole meets the centre window;
  - the last layers of the 45° beams and of the truncated teardrop floors.
  These are the tapering ends of features, not walls.
- The solid volume is 7.65 cm³, about 9.6 g if printed 100% solid.

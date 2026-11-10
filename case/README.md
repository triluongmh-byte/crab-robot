# Open skeleton — A1V4-r5

The body consists of two structural bar frames, with open servo saddles and alternative wire routes. Each hip servo is held by its own two mounting tabs. There are no clamp bars, sheet walls, enclosing lid or cosmetic skin. Skin remains deferred until the owner asks for it.

**The new frame is unprinted and physically untested.** CAD and slicer results are not proof of real fit, strength, cable flexibility or walking. The owner's assembled orange body is an earlier, manually modified part; see [printed inventory](PRINTED-INVENTORY.md) and [the owner's photos](../references/OWNER-PRINTS.md).

## Keep and replace

- Reuse the four thighs and four feet already printed. Their r1 source meshes and saved bed positions remain frozen. Their physical source revision is inferred from project history, not measured from the photographs.
- Both interfering clamp bars are printed but removed and unused. They are absent from the current production assembly and Print all.
- The two new parts, `frame_lower` and `frame_upper`, replace the previous body. This is not a whole-robot reprint.
- The new installed electronics target is the integrated controller. These checks do **not** prove mounting or complete wiring for the owner's separate LILYGO and PCA9685 modules.

## Build and view

Run the repository-root `./build.sh` using the documented toolchain. It regenerates the assembly overview, CAD, reports and arranged slicer projects. Generated files are intentionally outside Git.

Open the generated `case/overview.html`: **Đủ bộ** shows the complete assembly; **Bước 1–8** selects the assembly step, its actual screws and insertion arrows. Optional camera, exploded, wire and motion controls are under **Chi tiết**. The product UI remains Vietnamese.

- `case/robot/`: assembled robot-frame STEP/STL exports.
- `case/out/`: the same geometry rigidly transformed to the board frame for the native checker.
- `case/fastener_map.csv`: screw IDs, mating parts, sizes and insertion directions.
- `case/reports/`: mechanical, section, wire-route, insertion/tool and native-case evidence.

Read [the BOM](BOM.md), [physical checks](CHECKLIST-RAP.md), [engineering deviations](DEVIATIONS.md) and [source handoff](HANDOFF.md). Electronics connections are in [the integrated wiring guide](../docs/INTEGRATED-WIRING.md).

## Print projects

The generated **`case/print/production.3mf` is the complete current assembly**, containing ten production parts on two plates:

| Plate | Contents | Action | Offline estimate |
|---|---|---|---|
| 1 — MỚI∕SỬA — CẦN IN | `frame_lower`, `frame_upper` | Select only when replacing the body | 3 h 42 min, 67.4 g |
| 2 — ĐÃ IN — GIỮ LẠI | Four thighs, four feet | Keep the existing prints | 1 h 36 min, 38.8 g |

Both use the saved Bambu A1 / 0.4 mm nozzle / calibrated PETG profile: 0.20 mm layers, two walls, 7% grid infill and automatic tree supports. Parts are grounded, their long sides follow printer X, and plate/group clearances are checked. The entire virtual kit is about 5.29 h / 106.2 g. Slicer estimates are not measured print times. No printer is operated by the build.

Before a long structural print, use generated **`case/print/test-saddle.3mf`**, marked **TEST ONLY**, with one real servo and its two correct mounting screws. It comes from the current saddle geometry. The separate `test-only.3mf` and `mating-test.3mf` check the retained horn/nut/leg interfaces; none is a production part. Follow [the coupon checks](CHECKLIST-RAP.md); do not force or drill a mismatching part.

## Assembly order

Use the same eight steps as the overview. B/T/J/H/K labels refer to the generated fastener map and hardware cards.

1. **Lower frame and PCB:** connect the J12 power wires on the bench while unpowered. Drop four M3 nuts into the open wells, lower the actual PCB straight into the lower frame and fit B1–B4, four M3×6 screws.
2. **Display and light:** with the upper frame off the robot, retain the LCD and LED bar using the specified ties. Keep the LCD orientation in D15; protect its glass from tie pressure.
3. **Join frames:** connect the LCD/LED harnesses, lower the upper frame onto the columns and fit J1–J3, three M3×12 screws into the printed Ø2.7 pilots. These three joints use no nuts.
4. **Hip servos:** first pass each three-pin plug into an open bay below its saddle. Lower the servo until both tabs rest on their saddles, then fit its two T screws into the existing Ø1.6 pilots. No member presses on its body or gear boss. Do not drill servo tabs or the frame.
5. **Leg subassemblies:** reuse the four existing thighs/feet, knee servos and horns. The H/K cards identify the arm screws, knee-tab screws and centre screws. Keep the servo output shafts uncoupled from the legs until centring in step 8.
6. **Power bank:** connect the bank-side adapters while unpowered, slide the bank into its low open cradle from the front, then secure the removable strap across the front face. Do not slide it with the strap tightened.
7. **Wire routes:** choose an open alternative for each lead in the routing step. Leave a knee-lead loop of at least **40 mm between its thigh and frame ties**, with enough slack at every tested pose. Plug the eight servo leads into the correct channels; route the bank-port-1 cable through the rear bay/end window and outside the +Y rail, then insert USB-C at the side. The checked plug housing is **12.5 mm wide × 7 mm thick × 25 mm long**, with a 4.5 mm cable. The head projects about 20 mm beyond the body; keep that space free.
8. **Centre, then attach horns:** with leg/horn assemblies uncoupled from the output shafts and clear of the frame, follow the firmware centring procedure. Attach thighs and feet at their centre positions, then fit the proper factory centre screws. An already assembled leg must be uncoupled before re-centring; do not drive it against the frame.

Before any powered motion, gently inspect the full joint movement with power disconnected. Never force geared servos or use motor power to overcome binding. The full CAD grid covers ±30° in both joints, including intermediate poses; the required ±25° range has more clearance than the worst ±30° corner. Real tolerances and wire stiffness remain to be checked.

## Dimensions and evidence scope

The exported body is **126 × 74.6 × 46.5 mm**. There are ten production prints, seven M3 screws and four M3 nuts. The nominal SG90 body has at least 0.65 mm clearance to the frame. The estimated assembled mass is about 355 g, including an assumed 120 g bank; weigh the real build.

The CAD checks cover the actual integrated PCB, staged insertion and tool access, frozen leg geometry, eight lead routes, plug-envelope samples, knee loops, strap/leg motion, symmetry and printable sections. Read the generated reports for sampling/model limits. These are model checks, not continuous physical-motion or real plug-passage tests. The board is unmanufactured; the frame is unprinted; `hardwareTested=false`.

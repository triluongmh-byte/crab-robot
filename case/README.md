# Integrated skeleton case — work in progress

**Do not print the current new plate 1 or order the current PCB.** The board fits the final seated pose but cannot be inserted, and three PCB screws are blocked. D18 in [DEVIATIONS.md](DEVIATIONS.md) specifies the required PCB revision; its virtual fit result is not an actual revised board. The temporary U1 clearance slit and thin nut-seat floor also need revisiting with the board's real module envelope.

The body is a skeleton exposing the PCB and cables. The new base/lid retain the integrated controller and a separate Waveshare 23822 display. The two clamp bars, four thighs and four feet on plate 2 remain frozen at r1, including their mesh bytes, print rotations and placements. The owner reported plate 2 printing; completion and fit have not been confirmed.

## Source and generated files

`model.py`, `hardware.py`, `assembly_steps.json`, `interfaces.json`, `placement-settings.json`, `print-settings.json` and the frozen r1 source archive are inputs. Run the root `../build.sh` with the documented toolchain. It recreates the old accepted frozen parts from source, rather than requiring an old generated STEP or private Git commit.

Generated `robot/` contains assembly-frame CAD used for motion, printing and the overview. `out/` contains rigid board-frame copies for the unmodified native checker. Reports record these frames separately. `overview.html` is the standalone assembly viewer. `print/production.3mf` is the arranged Bambu project; `test-only.3mf` and `mating-test.3mf` contain the separate coupons. No script sends a printer job.

## Assembly sequence after the repair passes

1. Test the coupon and horn/servo fit. Do not force a horn onto a misaligned shaft.
2. Fit the four cap nuts and hip servos, leaving the clamp bars off while the controller is inserted.
3. Have the PCB connectors assembled and inspected. Wire J12 on the bench before mounting; the wire-entry side has little clearance afterward. Route and retain the hip leads below the board without pinching them against the PCB tails.
4. Install the **revised, insertion-verified** PCB and its four M3×6 screws/nuts. The current PCB fails this step.
5. Install the frozen clamp bars with four M3×20 screws. Fit the separate LCD and centered LED bar on the lid using the specified ties, then close the lid with three M3×8 screws. The lid screws form their threads in the printed pilots; the current model uses eight M3 nuts in total.
6. Follow [wiring and centering](../docs/INTEGRATED-WIRING.md). Center servos before attaching horns, keep the body supported and legs free for the first joint tests, then install legs with the SG90-supplied screws.

These lengths describe the current candidate; the repair must confirm or update them. The assembler must inspect insulation under PCB mounting hardware. Use a USB-C plug body at most 11.4 mm wide, subject to the final connector-reach check after J1 moves.

## What the checks establish

The native check tests the final seated pose in board coordinates. The mechanical script samples the legs and checks several real-part envelopes, wire corridors and tool paths. The new assembly-access report separately tests the actual board insertion and screw access, and currently fails. Print checks/slicer estimates do not prove skeleton strength, the 0.23 mm simulated minimum leg/body gap, physical horn fit, floor grip or walking.

The first manufactured/printed assembly must check all those physical details, QR visibility with the lid fitted, antenna performance near the power bank/display, power-bank shutoff and servo loads. No physical result is claimed here. Keep already printed plate-2 parts until the owner confirms their condition; a printer job status alone is not a completed-part confirmation.

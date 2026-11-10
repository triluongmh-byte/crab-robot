# Physical assembly checks

These checks distinguish a nominal CAD fit from the actual prototype. Stop at a mismatch and report it; do not force, shave or drill the new parts. The integrated board and r5 frame have not been physically tested.

## Owner's current orange body

The owner reports four hand-made wire openings and direct hip-tab screws after removing both interfering clamp bars. Before supplying power:

- Inspect every opening for sharp edges against the lead insulation. Protect the crossing with suitable tape/sleeving without cutting the wire or enlarging the hole.
- Inspect around the four wire openings and every owner-made screw hole for cracks.
- Gently check each hip servo for looseness or cracked tabs. Snug the correct screws without overtightening; remaining looseness or cracks require a repair review, not more drilling.
- Check the four knee leads separately from the four hip leads. Each needs slack across its moving hip joint, with no tension at either end.
- Inspect movement gently with power disconnected. The photographs establish mechanical assembly, not calibration, retention strength or walking.

## Coupons before the new frame

1. Print generated `print/test-saddle.3mf`, marked **TEST ONLY**. Place one actual hip servo on the two saddles; its body must enter freely and both tabs must rest flat without being bent. Try the two proper tab screws in the existing pilots. Do not drill either the servo or coupon.
2. Use `print/test-only.3mf` for the retained horn/nut interfaces and `print/mating-test.3mf` for one front-left leg. Their historical pocket tests do not validate the new open saddle.
3. Check that the correct one-arm horn seats and remains retained, the M3 nut fits its well without spinning, and screws engage without splitting or stripping plastic.
4. Confirm screw **types and lengths**, not only total count. The current build needs sixteen tab screws, eight horn-arm self-tappers and eight centre screws; see [BOM.md](BOM.md). A centre screw is not a replacement for a horn-arm screw.

## New r5 body

| Check | Acceptable result |
|---|---|
| Lower actual PCB into lower frame | It rests flat on all four seats; all mounting holes align without force |
| B1–B4 nuts and screws | Nuts remain captured; correct M3×6 screws engage without bottoming |
| Lower upper frame onto the columns | It seats fully without trapping the LCD/LED harnesses |
| J1–J3 frame joints | Correct M3×12 screws engage the Ø2.7 pilots; no cracks or stripping |
| Hip servo saddles | Both tabs sit flat; body and gear boss clear every bar; two correct screws retain each servo |
| USB-C cable | Housing ≤12.5 ×7 ×25 mm fits the +Y side opening; cable ≤4.5 mm follows the outside-rail route, clear of moving legs. Keep the projecting head free |
| All eight servo leads | Each reaches its correct header by an open route with the moulded plug intact |
| Knee service loops | At least 40 mm free lead between the thigh/frame ties; no tension or rubbing throughout gentle joint inspection |
| Bank and strap | Bank can slide out when the strap is removed and stays retained when the assembly is gently tilted |
| LCD and LED ties | Components are retained without bending the LCD glass; tails do not obstruct motion |
| BOOT / RESET | Reach the marked buttons using the overview's pin path; remove the upper frame if necessary, rather than bending the LED bridge |
| Joint movement, unpowered | No rubbing on frame, screws, cables or straps; never force a geared joint |
| Frame without skin | It carries the devices without cracks, excessive play or a cosmetic shell providing support |

Before powered centring, uncouple already installed horns/legs from the output shafts. Centre the unloaded servos using the firmware procedure, attach the legs in the shown neutral pose, then install the proper centre screws. Verify directions one joint at a time using the wiring/firmware guide; the nominal signs are unchanged.

The complete first prototype still needs QR readability, Wi-Fi range, bank shutoff/load, regulator temperature, LED data-level, floor grip and walking checks. No such result is inferred from the owner's previous LILYGO QR test or from CAD animations.

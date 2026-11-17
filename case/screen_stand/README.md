# Screen stand (A1V4-r5 open frame)

A printed PETG stand that snaps over the **outer wall of the raised display rim on the +Y long side of `frame_upper`**. It holds the bare LILYGO T-Display-S3 board (no shell) **upright in landscape**, facing +Y and leaning back 15° toward the middle of the crab.

This is the owner's request of 2026-11-16. `frame_lower` is no longer fitted. The owner marked the +Y side on a render as the front: the first version (PR #38) faced the +X end and was wrong.

The board size is the owner's ruler reading of 2026-11-17: **56 × 26 × 7 mm**.

**Status:** not printed. All the evidence comes from CAD (`check_fit.py`) and the slicer.

## How it holds

- **On the frame.** A cap sits on the rim wall (y 33.46…37.02, z 43.5…46.52, x −46.5…11.5). Two flexing tabs at x = −8 and x = −28 snap under its inner edge with 0.5 mm barbs.
  - The tabs avoid the rim posts at x −46…−40 and −1…5.
  - The outer face is flush with the rim.
- **Position.** The screen centre is at x = −10 (the board spans x −38…18). The end bracket is 7.2 mm from the −X hip servo.
- **The screen.** It drops in from above into two end slots, each 8.0 mm wide (7 mm board + 1 mm clearance).
  - The slots grip only the **short ends** of the board. The front and back lips cover 2 mm of each end; the back lips only the band 7…19 mm up the screen.
  - So both header rows and their Dupont housings on the back stay free.
- **Ends open.** The end windows are open to the top, so the USB-C plug and the buttons work at either end.
- **Reversible.** It works with the USB-C end on either side.
- **Rubber band.** Loop one over the notches on top of the two back posts, along the top edge of the board, so the screen can't hop out while walking.

## Assumptions (GIẢ ĐỊNH): measure and tell Claude

| What | Assumed | Why it matters |
|---|---|---|
| Board length × height × thickness | 56 × 26 × 7 mm (owner's ruler) | Slot length 57, width 8.0. A loose fit means a band or tape; a tight one means sanding or a reprint. |
| Header rows | 2.5 mm in from each long edge; housings 2.5 wide, 14 long | They must clear the back lips and the deck tower |
| USB-C plug | overmould 12.5 × 7, centred on the end face | Window size |

The vendor STEP (`case/ref/vendor-lilygo-t-display-s3-full.stp`) agrees on the body: 56.2 × 25.5. Its 62 mm includes the USB-C overhang, and its 9.9 mm overall thickness includes back parts that start 2.1 mm in from each end, so the 2 mm lips stay off them.

## Checks (`check_fit.py` → `fit_report.json`)

All of these pass:

- **Stand.** Zero overlap with `frame_upper` and the servos. The minimum gap is 0.19 mm to the frame and 7.16 mm to the servos.
- **Screen.** The board envelope has zero overlap with the stand, the frame and the servos. It slides in along its own height from 40 mm above without touching the stand.
- **Dupont housings.** Both rows are clear of the stand, the frame and the servos.
- **USB-C.** The plug path is clear at both ends.
- **Snap.** Lowering the stand onto the rim meets it only at the barbs: at most 3.3 mm³.

## Print

`screen_stand.3mf` uses the repo profile (`case/print-settings.json`, A1, PETG) with tree supports.

The part stands on one of its flat end faces. That way the posts and the snap tabs bend within their layers rather than across them; printed upright, as on the robot, the tabs would snap along a layer line.

The offline Bambu Studio CLI slice gives **1 h 09 min and 5.6 g**. That is a slicer estimate.

## Fit

1. Remove the supports. Press the stand down onto the +Y display rim, with the open side of the cradle facing out (+Y). The tabs click under the rim wall.
2. Plug the Dupont wires onto the LILYGO first. Then drop the board into the slots, screen facing out.
3. Put a rubber band over the two back-post notches.

## Regenerate

```sh
python3 ~/.claude/skills/cadcode/scripts/cad "$PWD/case/screen_stand/screen_stand.py"
CRAB_CASE_EXPORTS=/path/to/case python3 case/screen_stand/check_fit.py
python3 case/screen_stand/make_3mf.py --slice /tmp/stand_slice
```

The generated `*.step`, `*.stl` and `*.3mf` files are gitignored.

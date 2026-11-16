# Screen stand (A1V4-r5 open frame)

A printed PETG stand that snaps over the **end crossbar of `frame_upper`**. It holds the LILYGO T-Display-S3 in its clear shell **upright in landscape**, facing out and leaning back 15°. This is the owner's request of 2026-11-16: the owner props the screen up like this anyway, and `frame_lower` is no longer fitted.

**Status:** not printed. All the evidence comes from CAD (`check_fit.py`) and the slicer.

## How it holds

- **On the frame.** A cap sits on the crossbar (x 43.0…46.2, z 34.4…39.95). Two flexing tabs at y = ±20 snap under the inside edge of the crossbar with 0.5 mm barbs.
  - The outer face stays flush with the crossbar, 0.95 mm from the hip servos.
  - The tabs avoid the deck ribs at |y| 6.4…9.4 and the side rails at |y| ≥ 34.
- **The screen.** It drops in from above into two end slots, each 13.1 mm wide.
  - The slots grip only the **short ends** of the shell. The front lips cover 2 mm of each end; the back lips only the band 7…23 mm up the screen.
  - So both header rows and their Dupont housings on the back stay free.
- **Ends open.** The end windows are open to the top, so the USB-C plug and the buttons work at either end.
- **Reversible.** It works with the USB-C end on either side.
- **Rubber band.** Loop one over the notches on top of the two back posts, along the top edge of the shell, so the screen can't hop out while walking.

## Assumptions (GIẢ ĐỊNH): measure and tell Claude

| What | Assumed | Why it matters |
|---|---|---|
| Shell length × height × thickness | 66 × 30 × 12.5 mm | Slot length 67, width 13.1. A loose fit means a band or tape; a tight one means sanding or a reprint. |
| Header rows | 2.5 mm in from each long edge; housings 2.5 wide, 14 long | They must clear the back lips and the deck tower |
| USB-C plug | overmould 12.5 × 7, centred on the end face | Window size |

The vendor STEP (`case/ref/vendor-lilygo-t-display-s3-full.stp`) is the bare board, 26.3 × 62 × 9.9. The clear shell is not published, so its size is a guess.

## Checks (`check_fit.py` → `fit_report.json`)

All of these pass:

- **Stand.** Zero overlap with `frame_upper` and the servos. The minimum gap is 0.2 mm to the frame and 0.95 mm to the servos.
- **Screen.** The shell envelope has zero overlap with the stand, the frame and the servos. It slides in along its own height from 40 mm above without touching the stand.
- **Dupont housings.** Both rows are clear of the stand, the frame and the servos. The cradle sits at z0 52.5 for this reason: at z0 47.5, the lower row hits the deck tower (x 20…33.9, |y| < 9.4, top z 46.5) by 226 mm³, which is the negative test.
- **USB-C.** The plug path is clear at both ends.
- **Snap.** Lowering the stand onto the crossbar meets it only at the barbs: at most 3.2 mm³.

## Print

`screen_stand.3mf` uses the repo profile (`case/print-settings.json`, A1, PETG) with tree supports.

The part stands on its flat −Y end face. That way the posts and the snap tabs bend within their layers rather than across them. Upright, as on the robot, would print 20 min faster (1 h 08), but the tabs would snap along a layer line.

The offline Bambu Studio CLI slice gives **1 h 28 min and 8.6 g**. That is a slicer estimate.

## Fit

1. Remove the supports. Press the stand down onto the crossbar at the end you want the face on. The open side of the cradle faces outward. The tabs click under the bar.
2. Plug the Dupont wires onto the LILYGO first. Then drop the shell into the slots, screen facing out.
3. Put a rubber band over the two back-post notches.

## Regenerate

```sh
python3 ~/.claude/skills/cadcode/scripts/cad "$PWD/case/screen_stand/screen_stand.py"
CRAB_CASE_EXPORTS=/path/to/case python3 case/screen_stand/check_fit.py
python3 case/screen_stand/make_3mf.py --slice /tmp/stand_slice
```

The generated `*.step`, `*.stl` and `*.3mf` files are gitignored.

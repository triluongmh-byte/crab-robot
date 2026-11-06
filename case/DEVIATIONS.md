# Case deviations from the sealed contract (r001)

Each entry gives the contract text, what changed, the evidence and the effect on other teams.

## D1. PCA9685 retention: rim pocket + lid instead of a zip tie
- **Contract:** "Mounted in a printed pocket with a zip tie."
- **Change:** PCA sits in a rim pocket on the shelf (rim blocks at both X ends, body wall on −Y,
  LED bridge pillars on +Y). The lid pocket ceiling (z 45.8, see D4) is 2.8 mm above the plug tops (z 43), less than the 4 mm rim, so the
  module cannot lift out. There is no zip tie.
- **Evidence:** a tie around the PCA would have to pass under the shelf, between the shelf and
  the power bank, where there is no gap. Over the top it would cross the servo headers.
  `case/reports/mechanical.json` → `deviceClearances` (lid–PCA 1.0 mm).
- **Cross-team impact:** none. Pins, position and envelope are unchanged. WIRING/BOM need no tie for the PCA.

## D2. LILYGO envelope split for the cradle (GIẢ ĐỊNH). Superseded in part by D4
- **Contract:** LILYGO box (0, 19, 32.5), 66 × 28 × 23, including the Dupont housings underneath.
- **Change:** none to position or size. The case models the box as shell+PCB+screen (z 33–44,
  full footprint) plus two 4 mm header strips underneath. A central rib (y 15–23, up to z 33)
  supports the board between the header rows.
- **Evidence:** this is an assumption that the header rows run along both long edges (owner photo
  only). CHECKLIST-RAP item C3 checks it.
- **Cross-team impact:** none. If the real board's underside differs, only the rib height changes.

## D3. Knee servo envelope orientation
- **Contract (target, case-owned):** knee size listed as 22.8 × 12.2 × 32.2, centre ≈ (75, 45, 40).
- **Actual:** the knee SG90 has its long axis vertical (tabs span z 23.9–56.1), its shaft
  horizontal along the leg tangent at z 45.5, and its centre at r = 30 mm on the 45° diagonal:
  FL (75.11, 45.11, 40). This is within the contract target and reported for firmware.
- **Cross-team impact:** for the firmware gait sim, the knee axis is at r = 30 and z = 45.5. The
  neutral foot is at r = 58 from the hip shaft, z = −20 (foot circle bottom z = −27).

## D4. LILYGO raised 1.8 mm into a lid pocket + shelf wire trenches (integration repair)
- **Contract:** LILYGO box centre (0, 19, 32.5), z 21–44, including the Dupont housings; "held by a printed cradle plus a zip tie".
- **Change:** the board now spans z 22.8–45.8. The lid has a 1.8 mm pocket on its underside (68 × 30, skin 1.2 mm) that
  takes the shell and screen, so the glass sits 1.2 mm under the lid top and the window is unchanged.
  Two trenches through the shelf (y 4.5–10.5 and 28–33, x ±31.5) open down to the pack top at z 18. That leaves
  about 4.8 mm under the housings for the Dupont wires to bend, and they leave the trenches at the +X end.
  The cradle rib now reaches z 37.5 (the shell underside, GIẢ ĐỊNH). The lid pocket clamps and locates the board,
  so the zip tie, its rib tunnel and the lid relief are removed.
  The PCA area gets the same 1.8 mm lid pocket, giving its plug tops 2.8 mm of room for the leads.
- **Evidence:** lead integration measured the vendor t-display-s3-full.stp: glass to PCB back 6.4 mm, plus a 2.5 mm
  header and a 14 mm Dupont housing. With the glass at z 44 the housings would end at z 21.1 with no room for the
  wires. Keep-outs `lilygo_dupont_wires_row1/2` and `pca_lead_bend_room` are checked in `case/reports/mechanical.json`.
- **Cross-team impact:** none to pins, rails, the window position or the firmware. The LILYGO centre z moves to 34.3 for integration.
  The shelf strip between the trenches (y 10.5–28) is carried by the 17 mm box rib and the shelf ends.

## D5. +X LILYGO end stop moved (integration repair)
- **Change:** the end stop is now a single block at y 11.5–21. The +X+Y hip pocket inner wall is closed again at y 12–21 on
  that quadrant only. The old stops at y 6–12 and 26–32 blocked the nut slots of S01 and S05.
  `nutSlotPaths` in `case/reports/mechanical.json` now probes all 8 slot paths on the exported STEP.
- **Cross-team impact:** none.

## D6. M3x20 lid screw seat (integration repair)
- The head sits in a d6.4 counterbore and bears on a 10.1 × 7.5 mm boss block under the lid. The block is fused to the
  lid plate over 43.9 mm² per screw (it was a 0.3 mm ring before), and the boss drops into a matching pocket in the
  clamp bar. The head top is z 47.0. `lidScrewJoint` in the mechanical report gates this at ≥ 30 mm².

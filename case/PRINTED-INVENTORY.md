# Owner-reported printed inventory

Evidence is the owner's direct reports on 2026-11-10 and [the supplied photographs](../references/OWNER-PRINTS.md). Exporting, slicing or a printer reporting completion is not treated as a physical print confirmation. Exact physical mesh identities remain unverified; no cropped-body mesh hash is invented. Orange/yellow describe visible colours, not confirmed materials.

| Inventory ID | Item / quantity | Physical status | Identity limits |
|---|---|---|---|
| `OWNER-20261110-P1-UPPER-FRAME` | One owner-selected region of the plate-1 body | Owner reports lower geometry was removed **in the slicer before printing**. Later photos show the orange body with four rough hand-made wire openings, four assembled legs/eight servos and direct hip-tab screws. The two clamp bars have been removed | The photographed body is probably this variant, not a proven exact match. Cut height, revision, cropped mesh, added holes and screw sizes/lengths are unknown |
| `OWNER-20261110-P1-REMAINDER` | Other plate-1 contents | Owner reports the plate completed; items were not individually enumerated | Do not invent a completed full base/lid or unlisted accessory |
| `OWNER-20261110-P2` — legs | Four thighs and four feet | Printed and mechanically assembled by owner report/photo; no failure reported. Reuse in the new production assembly | r1 association is inferred from history. No physical mesh measurement, calibration or walking result is established |
| `OWNER-20261110-P2` — clamp bars | `cap_front`, `cap_rear`, one each | Printed, removed because of servo interference, unused. Retain as spare inventory; absent from the current assembly and Print all | Exact interference location/cause is unknown. The identifying blue-highlight image is CAD, not a photo |

The owner's hip servos are now screwed through their tabs directly into the modified body. Whether servo tabs were enlarged, the precise holes, screw types and holding strength are unknown. Do not copy these unknown holes into CAD or assume permission for further drilling.

## Current production revision

A1V4-r5 consists of eight reusable leg parts plus **two new, unprinted** bar frames, `frame_lower` and `frame_upper`. The old owner-modified body is a separate physical variant. Its mechanical assembly does not validate the new frame, the integrated PCB, cable motion, strength or walking.

TEST ONLY / saddle / mating coupons have no owner-confirmed physical result. Earlier V3 failure photos refer to another design and are not reusable parts or validation for this revision.

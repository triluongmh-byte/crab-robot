# Open frame repair — owner-selected direction, 2026-11-10

The owner trial-mounted servos in the printed body pockets and could not route the wires. They selected bars/cross-members rather than walls: an exposed load-bearing skeleton with alternative cable routes, with skin deferred until they explicitly request it. This is an implementation request under the standing instruction to resolve routine engineering choices without technical questions.

## Direction

Use the existing servo axes, factory horns and useful printed leg interfaces. Replace only the obstructing body structure that must change with an open bar frame. Later owner feedback confirms both clamp bars interfere and were removed: use accessible direct-tab servo retention, not the old clamp interface. Keep short supported mounting lugs/shoulders where load transfer requires them, but no sheet walls, closed servo cups, enclosed wire channels or enclosure panels. Making a few small cable holes in the present walls does not meet the stated goal. The frame itself retains servos, controller, display/light and power-bank hardware; future skin must not provide missing structural support.

Conceptual intent (not CAD or a dimensional drawing):

    open direct-tab servo mounts
          |                   |
      ==== bar / open cross-member ====
          |   free routing space   |
      ==== bar / open cross-member ====
          |                   |
    alternate side/below/outside routes

Prefer dropping a lead into an open path and securing it to a bar over feeding the molded three-pin connector through a closed hole. Show multiple genuinely accessible routes around each reported obstructed mount, plus slack/strain relief for the moving joints. Keep screw heads/nuts and service tools reachable with the devices actually installed.

## Existing prints and scope

The owner reports both plates printed. The plate-1 box is a slicer-modified upper-frame-only variant, with the lower portion omitted before printing. Exact cut height, source revision and cropped mesh are unknown. Preserve these facts and keep usable existing prints; identify the smallest necessary replacement instead of reprinting the entire robot. Do not assume permission for further physical drilling/cutting. The prior complete-case D18 proposal is not fit evidence for this new physical variant.

Subsequent photos show the owner mechanically assembled four legs/eight servos and hand-made four wire openings in the retained orange body. Both clamp bars are printed but removed for interference; only the four thighs/four feet remain candidates for reuse in the installed production assembly. Exact hardware and physical strength remain unverified. See [the chronological owner evidence](../../../references/OWNER-PRINTS.md).

No skin, enclosing lid, cosmetic shell, GPIO/firmware behavior change, hardware actuation, printing or ordering is requested here. Necessary structural display/LED mounts are open supports, not skin. The lead decides whether the mechanical repair needs another domain; do not silently alter accepted copper just to simplify a case check.

## Required evidence and handoff

Use actual CAD solids and real servo-plug/wire envelopes to check connector installation, multiple routing options, nut/tool access, retention and full combined joint motion. Rebuild the real interactive assembly overview and the complete arranged print project, separating already-printed/reusable parts from new/updated structural parts. Keep separate coupons out of the production assembly. State reference-part/tolerance assumptions and physical tests still pending; do not label CAD/slicer results as a real fit/strength pass. Inspect actual insertion/wire findings even if the bridge marks the candidate ready.

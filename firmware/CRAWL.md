# Gait guide — diagonal trot

Since `positional180-v23` the diagonal trot is the only gait. The owner's front/rear pairs (v5) and knee-flick (v10–v11) trials never walked properly, so they, the **Dáng đi** selector, the **Góc hông búng** slider and `/api/gait` / `/api/flickhip` were removed (owner, 2026-11-15). Their history is in [the release notes](README.md).

## Diagonal trot (`trot`)

Diagonal pairs FL+RR (CH0/1 + CH6/7) and FR+RL (CH2/3 + CH4/5) alternate half a cycle apart.

| Stage for one diagonal pair | Cycle fraction | Fast duration | Knee | Hip |
|---|---:|---:|---|---|
| Stance (push) | 0.56 | 448 ms | Down | Constant-rate front to rear |
| Lift | 0.10 | 80 ms | Raise to nominal 30° | Hold rear endpoint |
| Swing | 0.24 | 192 ms | Hold raised | Smooth rear to front |
| Lower | 0.10 | 80 ms | Lower | Hold front endpoint |

Why it replaced the earlier front/rear pairs:

- **Support:** a whole diagonal is always grounded. That support line passes under the body centre. With front/rear pairs it runs across the front or the rear, so the body pitches towards the raised end.
- **Four-foot overlap:** stance 0.56 > 0.5 gives about 12% of every cycle with all four feet down, at each pair handover.
- **No scrub in the overlap:** stance is linear, so both grounded pairs move the body at one rate.
- **No self-rotation:** feet sit on the ±45°/±135° rays. A diagonal's two feet have parallel hip tangents and receive mirrored commands, so their yaw contributions cancel in every direction. With front/rear pairs, Left/Right yaw because both front hips get the same-sign command. The 13 Nov video shows the body rotating while ← Trái was held.
- **Timing fits the servos:** the cycle is 0.8 s at Fast, 1.23 s at Normal and 2.0 s at Slow. At Fast the knee lift needs 375°/s and the hip return peaks at 391°/s, both under the 600°/s slew limit (about the SG90's no-load speed). A host test checks that every joint tracks its target within 2.5°.

What to expect: each diagonal can only push the body along one axis, so Forward trot zig-zags slightly from side to side while making net forward progress. Foot clearance is unchanged (nominal 30° knee, 30° soft limit, 35° final clamp). If feet still drag, that is a lift/calibration issue: measure the real SG90 angle per microsecond, or check clearance before anyone raises the limits.

## Trial

On a level surface with room around the robot: reload the page, enable servos, wait about 3 seconds, and start on **Bình thường** or **Chậm**. Hold Forward for about 10 seconds from a taped start mark, then check the distance and heading change (use **Bù lệch trái ↔ phải** if it drifts). Stop if the body tips, the feet catch on the frame, or the power bank resets. Host simulation is not proof of physical walking; mass, friction, servo load and actual angles are unmeasured.

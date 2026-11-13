# Gait trial guide — diagonal trot (default) and owner front/rear pairs

The control page sidebar has a **Dáng đi** selector. Changing it, like changing speed, stops walking and briefly blanks the outputs; the servos stay enabled and resume the standing pose on the next frame. Release the arrow before switching.

## Default: diagonal trot (`trot`)

Diagonal pairs FL+RR (CH0/1 + CH6/7) and FR+RL (CH2/3 + CH4/5) alternate half a cycle apart.

| Stage for one diagonal pair | Cycle fraction | Fast duration | Knee | Hip |
|---|---:|---:|---|---|
| Stance (push) | 0.56 | 1008 ms | Down | Constant-rate front to rear |
| Lift | 0.10 | 180 ms | Raise to nominal 30° | Hold rear endpoint |
| Swing | 0.24 | 432 ms | Hold raised | Smooth rear to front |
| Lower | 0.10 | 180 ms | Lower | Hold front endpoint |

Why this replaces the front/rear pairs as the default:

- **Support:** a whole diagonal is always grounded. That support line passes under the body centre. With front/rear pairs it runs across the front or the rear, so the body pitches towards the raised end.
- **Four-foot overlap:** stance 0.56 > 0.5 gives about 12% of every cycle with all four feet down, at each pair handover.
- **No scrub in the overlap:** stance is linear, so both grounded pairs move the body at one rate.
- **No self-rotation:** feet sit on the ±45°/±135° rays. A diagonal's two feet have parallel hip tangents and receive mirrored commands, so their yaw contributions cancel in every direction. With front/rear pairs, Left/Right yaw because both front hips get the same-sign command. The 13 Nov video shows the body rotating while ← Trái was held.
- **Timing fits the servos:** at Fast, both the 30° knee lift and the smoothstep hip return stay under the 180°/s slew. A host test checks that every joint tracks its target within 2.5°.

What to expect: each diagonal can only push the body along one axis, so Forward trot zig-zags slightly from side to side while making net forward progress. Foot clearance is unchanged (nominal 30° knee, 30° soft limit, 35° final clamp). If feet still drag, that is a lift/calibration issue: measure the real SG90 angle per microsecond, or check clearance before anyone raises the limits.

## Option: owner front/rear pairs (`pairs`)

This is unchanged from `positional180-v5`. Front hips CH0/CH2 push rearwards with knees CH1/CH3 down, then lift, return and lower. The rear pair CH4–CH7 follows half a cycle later. At Fast the stages are push 900 ms, lift 225 ms, return 450 ms and lower 225 ms. It is yaw-free only for Forward/Backward. Sideways moves rotate the body.

## Trial

On a level surface with room around the robot: reload the page, enable servos, wait about 3 seconds, and start on **Bình thường** or **Chậm**. Hold Forward for about 10 seconds from a taped start mark, then compare the distance and heading change between the two **Dáng đi** options. Stop if the body tips, the feet catch on the frame, or the power bank resets. Host simulation is not proof of physical walking; mass, friction, servo load and actual angles are unmeasured.

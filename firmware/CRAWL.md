# Front/rear paired push trial

The owner explicitly requests front hips CH0/CH2 push rearwards with front knees CH1/CH3 down, followed by knee lift, forward hip recovery and knee lowering. Rear hips CH4/CH6 with knees CH5/CH7 repeat half a cycle later. This replaces the previous one-leg crawl; the filename is retained so existing links remain valid. Backward reverses hip travel while preserving the knee sequence.

| Stage for one pair | Fast duration | Knee | Hip |
|---|---:|---|---|
| Push |900ms|Down|Front to rear|
| Lift |225ms|Raise to nominal30°|Hold rear endpoint|
| Return |450ms|Hold raised|Rear to front|
| Lower |225ms|Lower|Hold front endpoint|

At Fast the complete front/rear pattern takes1.8seconds, with rear offset900ms. Default Normal takes about2.77seconds and Slow4.5seconds. Starting Forward commands the front hips from neutral towards the rear; the rear pair starts in recovery phase.

Nominal axial hip stroke is±25°, knee lift30°, slew180°/s and common pose frames20ms. The unchanged post-trim output limits remain±25° hip and±35° knee. Saved trims, conservative1000µs/180° mapping, channel directions, explicit enable, staged startup and500ms deadman are retained. Increasing stroke does not increase SG90 rated torque. Actual angles, force, supply behavior and load are not measured; a servo spanning180° over2000µs would move about half the nominal angle.

Host regressions decode actual PCA writes and check eight outputs per frame, matched front/rear knee pairs, at least two nominal contact feet with zero trims, raised knees before hip recovery at Fast, and exact Forward/Backward reversal. This front/rear support line does not establish pitch balance or a centre-of-mass stability margin. It is not a physically verified walking result.

Reload the control page, enable the180° servos and wait about3seconds. Use Normal for the first brief Forward/Backward check on a level surface with room around the robot. Look for the front pair pushing rearwards before lifting, then returning through the air; the rear pair does the complementary action. Release to stop. If knees press down instead of lifting, or the feet drag during recovery, stop and report that observation. Stable standing, horn direction, actual lift, floor grip and power under load still need the owner's check. No new parts or spending are required by this software trial.

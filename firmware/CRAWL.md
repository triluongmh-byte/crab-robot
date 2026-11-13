# Crawl trial: moving the body, not just the legs

The owner reports legs moving without body progress. The replacement gait is an experiment for the existing180° assembly, not a physically verified walking result.

Each leg takes a turn: front-left, rear-right, front-right, rear-left. The knee lifts first while the hip stays still; the hip returns while that foot is raised; the knee lowers before the next leg recovers. During stance the hips push opposite the requested body translation. Backward reverses hip travel while preserving knee lifting. Nominal three-foot support does not establish a centre-of-mass stability margin.

All joints use the same20ms pose frame. The PCA writes remain sequential; bus timing, servo response, oscillator error, load and physical contact are not measured by the tests. Host regressions decode actual PCA writes and check eight outputs per frame, at least three nominal contact feet with zero trims, and knee clearance before hip recovery at Fast. They do not prove clearance or traction on the owner's floor.

Normal is1second per recovered leg (4seconds for all four). Fast is0.65seconds per leg (2.6seconds per cycle). The nominal18° hip/25° knee movement uses the existing conservative pulse scale and unchanged final25°/35° output limits. A servo spanning180° over2000µs would move about half the nominal angle; actual calibration remains unknown.

Reload the control page, enable the180° servos and wait about3seconds. Start at Normal on a level surface with room around the robot. Briefly hold Forward and release. Look for one lifted foot returning freely while the other three support and push the body. If every foot remains on the floor, or a knee presses down when it should lift, stop and report that observation before trying more speed. Stable standing, horn alignment, knee direction, actual lift, supply under load and floor grip still need the owner's check. No new parts or spending are required by this software trial.

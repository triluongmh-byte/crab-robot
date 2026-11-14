#pragma once
#include <stdint.h>
#include "hardware.h"
// Robot frame: +X front, +Y left, +Z up. Channels alternate hip/knee.
namespace cfg {
constexpr uint8_t PCA_ADDR=0x40, LED_COUNT=8, LED_BRIGHTNESS=16;
constexpr int PWM_HZ=50, CENTRE_US=1500;
// Conservative nominal1–2ms/180deg mapping; delivered SG90 range must be observed.
constexpr float US_PER_DEG=1000.0f/180.0f, JOINT_LIMIT=30, TRIM_LIMIT=30;
// Trim steps: 1 deg nominal is ~5.6 us, about one PCA count and inside the SG90
// deadband, so single steps looked dead (owner). Coarse step 3 deg ~ 17 us.
constexpr int TRIM_FINE=1, TRIM_COARSE=3;
// Hips may travel to +/-90 deg nominal (1000-2000 us) for the owner's knee-flick
// stance; trot/pairs still request only HIP_AMPLITUDE. Knees stay at +/-35 deg.
// Knee lift is owner-adjustable KNEE_LIFT_MIN..KNEE_LIFT_MAX (saved); owner,
// 2026-11-13: feet dragged on the table while the hips returned, pushing the
// crab backwards, so the default rose from 30 to 45 deg nominal.
constexpr float KNEE_LIFT_MIN=20, KNEE_LIFT_MAX=60, HIP_LIMIT=90, KNEE_PULSE_LIMIT=65;
// Owner, 2026-11-13: CH0 actually sits at the REAR RIGHT. The firmware CAD
// frame (CH0 = front left) is therefore rotated 180 deg from the real robot.
// Drive commands are rotated into the CAD frame so Forward goes to CH4/CH6.
constexpr bool FRONT_IS_CH46=true;
// Owner, 2026-11-13: arm the servos at boot (was: PWM off until Bật servo).
constexpr bool AUTO_ARM=true;
// Heading trim: +N% gives the physical right hips N% more stroke and the left
// N% less (owner: Forward drifts right, right servos are slower). Saved.
constexpr int BALANCE_LIMIT=30;
// Case D7: hip shafts point up; single mirrors FR/RL reverse knee sense.
// Knees FL +1, FR -1, RL -1, RR +1; negative angle lifts each foot.
constexpr int SIGN[8]={1,1,1,-1,1,-1,1,1};
// Calibration labels as the owner names the legs (CH6 = rear-right hip).
// Owner, 2026-11-13: keep these names while Forward stays rotated by
// FRONT_IS_CH46; labels and drive direction are set independently.
constexpr const char* JOINT[8]={"Hông trước trái","Gối trước trái","Hông trước phải","Gối trước phải",
                             "Hông sau trái","Gối sau trái","Hông sau phải","Gối sau phải"};
constexpr uint32_t DEADMAN_MS=500, BOOT_HOLD_MS=8000, ENABLE_GAP_MS=300;
constexpr uint32_t FRAME_MS=20;
constexpr float FRAME_S=FRAME_MS*.001f, PERIOD_S=0.8f;
// Web speed slider: fraction of full rate, default 90%.
constexpr float SPEED_MIN=.2f, SPEED_MAX=1.f, SPEED_DEFAULT=.9f;
constexpr float HIP_AMPLITUDE=25, KNEE_LIFT=45, SLEW_DPS=600;
// Return to standing after an emotion pose is released or times out.
constexpr float RELAX_DPS=120;
constexpr float RADIAL[4]={0.7853981634f,-0.7853981634f,2.3561944902f,-2.3561944902f};
// Leg order FL, FR, RL, RR. Each pattern: phase group per leg, then cycle
// fractions for grounded stance, knee lift and airborne hip return; the
// remainder lowers the knee. Hip start offset begins mid-stance at neutral.
struct GaitPattern {float group[4],stance,lift,swing,start;bool linearStance;};
// Default diagonal trot FL+RR / FR+RL. Stance .56 > .5 leaves 12% of each
// cycle with all four feet down. Linear stance keeps both grounded pairs at
// one body velocity during that overlap. At Fast (0.8 s) the knee lift
// (30 deg/.08 s = 375 deg/s) and smoothstep hip return (peak 1.5*50 deg/.192 s
// = 391 deg/s) both stay under SLEW_DPS (600, about SG90 no-load speed at
// 4.8 V) so joints track their targets.
constexpr GaitPattern TROT={{0,.5f,.5f,0},.56f,.1f,.24f,.28f,true};
// Owner-requested front pair CH0/2 and rear pair CH4/6, half-cycle apart.
// First half: grounded push. Second: lift, airborne return, lower.
constexpr GaitPattern PAIRS={{0,0,.5f,.5f},.5f,.125f,.25f,.25f,false};
// Owner knee-flick for Forward/Backward: hips turn (default 90 deg nominal,
// owner-adjustable FLICK_HIP_MIN..FLICK_HIP from the page) and hold, front
// feet swung forwards and rear feet swung backwards; only knees move. The hip
// stance ramps in with walking amplitude over about .67 s. At 90 deg the
// diagonal front feet may cross; the owner lowers the slider if legs touch.
// Diagonal knees flick together, half a cycle apart. Forward = fast lift
// (FLICK_STROKE of the cycle) then slow return; Backward reverses that in time.
// Fast lift: smoothstep peak 1.5*30 deg/(.2*.5 s) = 450 deg/s < SLEW_DPS.
// Left/Right keep the trot.
constexpr float FLICK_HIP_MIN=30, FLICK_HIP=90, FLICK_STROKE=.2f, FLICK_PERIOD_S=.5f;
// Owner, 2026-11-14: four slanted moves that turn the body while walking
// (dir 5 forward-left, 6 forward-right, 7 back-left, 8 back-right), like a car
// with the wheel turned. ARC_YAW is the share of each hip stroke spent turning.
constexpr float ARC_YAW=.5f;
// Eyes look towards the robot's own left when it walks left. +1 assumes the
// screen faces outwards like a face (robot left = viewer's right).
constexpr int EYE_LOOK_SIGN=1;
// Idle face: sleepy after this long without a drive/pose command, asleep later.
constexpr uint32_t SLEEPY_MS=60000, ASLEEP_MS=180000;
}

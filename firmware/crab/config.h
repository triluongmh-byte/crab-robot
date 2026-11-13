#pragma once
#include <stdint.h>
#include "hardware.h"
// Robot frame: +X front, +Y left, +Z up. Channels alternate hip/knee.
namespace cfg {
constexpr uint8_t PCA_ADDR=0x40, LED_COUNT=8, LED_BRIGHTNESS=16;
constexpr int PWM_HZ=50, CENTRE_US=1500;
// Conservative nominal1–2ms/180deg mapping; delivered SG90 range must be observed.
constexpr float US_PER_DEG=1000.0f/180.0f, JOINT_LIMIT=30, TRIM_LIMIT=12;
// Case D7: hip shafts point up; single mirrors FR/RL reverse knee sense.
// Knees FL +1, FR -1, RL -1, RR +1; negative angle lifts each foot.
constexpr int SIGN[8]={1,1,1,-1,1,-1,1,1};
constexpr const char* JOINT[8]={"Hông trước trái","Gối trước trái","Hông trước phải","Gối trước phải",
                             "Hông sau trái","Gối sau trái","Hông sau phải","Gối sau phải"};
constexpr uint32_t DEADMAN_MS=500, BOOT_HOLD_MS=8000, ENABLE_GAP_MS=300;
constexpr uint32_t FRAME_MS=20;
constexpr float FRAME_S=FRAME_MS*.001f, PERIOD_S=1.0f;
constexpr float HIP_AMPLITUDE=25, KNEE_LIFT=30, SLEW_DPS=450;
constexpr float RADIAL[4]={0.7853981634f,-0.7853981634f,2.3561944902f,-2.3561944902f};
// Leg order FL, FR, RL, RR. Each pattern: phase group per leg, then cycle
// fractions for grounded stance, knee lift and airborne hip return; the
// remainder lowers the knee. Hip start offset begins mid-stance at neutral.
struct GaitPattern {float group[4],stance,lift,swing,start;bool linearStance;};
// Default diagonal trot FL+RR / FR+RL. Stance .56 > .5 leaves 12% of each
// cycle with all four feet down. Linear stance keeps both grounded pairs at
// one body velocity during that overlap. At Fast (1.0 s) the knee lift
// (30 deg/.1 s = 300 deg/s) and smoothstep hip return (peak 1.5*50 deg/.24 s
// = 312 deg/s) both stay under SLEW_DPS (450) so joints track their targets.
// SG90 no-load speed is about 600 deg/s at 4.8 V.
constexpr GaitPattern TROT={{0,.5f,.5f,0},.56f,.1f,.24f,.28f,true};
// Owner-requested front pair CH0/2 and rear pair CH4/6, half-cycle apart.
// First half: grounded push. Second: lift, airborne return, lower.
constexpr GaitPattern PAIRS={{0,0,.5f,.5f},.5f,.125f,.25f,.25f,false};
}

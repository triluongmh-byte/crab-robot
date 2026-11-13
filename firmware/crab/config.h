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
constexpr float FRAME_S=FRAME_MS*.001f, STEP_PERIOD_S=.65f, PERIOD_S=4*STEP_PERIOD_S;
constexpr float HIP_AMPLITUDE=18, KNEE_LIFT=25, SLEW_DPS=180;
constexpr float RADIAL[4]={0.7853981634f,-0.7853981634f,2.3561944902f,-2.3561944902f};
// One recovery leg at a time: FL, RR, FR, RL. Three feet stay in stance.
// Each recovery has separate lift, airborne return and lower intervals.
constexpr float SWING_START[4]={0,.5f,.75f,.25f};
}

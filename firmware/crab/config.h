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
constexpr float PERIOD_S=6.0f, HIP_AMPLITUDE=12, KNEE_LIFT=15, SLEW_DPS=30;
constexpr float RADIAL[4]={0.7853981634f,-0.7853981634f,2.3561944902f,-2.3561944902f};
// Diagonal trot in FL,FR,RL,RR order: FL+RR and FR+RL alternate.
// Knees lift for half a cycle; quarter-cycle offsets would remove both
// left or both right supports together. Keep each diagonal exactly in phase.
constexpr float PHASE[4]={0,3.1415926536f,3.1415926536f,0};
}

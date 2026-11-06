#ifndef CRAB_CONFIG_H
#define CRAB_CONFIG_H
#include <stdint.h>
// Single GPIO authority, checked against LILYGO 2024-04-29 schematic and pin_config.h.
#define CRAB_SDA 18
#define CRAB_SCL 17
#define CRAB_LED_PIN 21
#define CRAB_BOOT_PIN 0
#define CRAB_POWER_ON 15
#define CRAB_LCD_BL 38
#define CRAB_LCD_CS 6
#define CRAB_LCD_DC 7
#define CRAB_LCD_RST 5
#define CRAB_LCD_WR 8
#define CRAB_LCD_RD 9
#define CRAB_LCD_D0 39
#define CRAB_LCD_D1 40
#define CRAB_LCD_D2 41
#define CRAB_LCD_D3 42
#define CRAB_LCD_D4 45
#define CRAB_LCD_D5 46
#define CRAB_LCD_D6 47
#define CRAB_LCD_D7 48
namespace cfg {
constexpr uint8_t pcaAddress=0x40, ledCount=8, ledBrightness=51;
constexpr uint32_t heartbeatMs=600, wifiTimeoutMs=15000, bootHoldMs=8000;
constexpr uint32_t servoEnableMs=300, gaitPeriodMs=8000, motionTickMs=10;
constexpr float hipAmplitude=12, kneeAmplitude=16, maxJointDelta=25;
// FL hip/knee, FR hip/knee, RL hip/knee, RR hip/knee.
// Positive gait knee = foot UP. Case larger-pulse motion: FL/RR DOWN, FR/RL UP.
constexpr int8_t signs[8]={1,-1,1,1,1,1,1,-1};
constexpr uint8_t enableOrder[8]={0,2,4,6,1,3,5,7};
constexpr float slowRate=8, swingRate=24, acceleration=80;
constexpr int pulseNeutralUs=1500;
// Conservative SG90 reference mapping: 90 degrees = 1500us, 10us/degree.
constexpr float pulseUsPerDegree=10;
}
static_assert(CRAB_SDA!=16 && CRAB_SCL!=43 && CRAB_LED_PIN!=16 && CRAB_LED_PIN!=43,"reserved pin");

#endif

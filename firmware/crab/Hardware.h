#pragma once
#include "Robot.h"
#include <Wire.h>
namespace crab {
class Pca {
 bool write(uint8_t reg,uint8_t value){Wire.beginTransmission(cfg::pcaAddress);Wire.write(reg);Wire.write(value);return Wire.endTransmission()==0;}
 public:
 bool allOff(){return write(0xFD,0x10);}
 bool begin(){
  Wire.begin(CRAB_SDA,CRAB_SCL,400000);Wire.setTimeOut(10);
  if(!write(0x00,0x30)||!allOff()||!write(0xFE,121)||!write(0x01,0x04)||!write(0x00,0x20))return false;
  // ALL_LED_OFF_H writes all individual OFF_H registers (NXP §7.3.4).
  // Keep every channel full-off; servo() clears only the enabled channel.
  delay(1);return write(0x00,0xA0);
 }
 bool servo(uint8_t channel,float angle){
  int us=cfg::pulseNeutralUs+int((angle-90)*cfg::pulseUsPerDegree);
  int ticks=(us*4096L+10000)/20000;
  // Stagger PWM rising edges across the 20ms frame as well as mechanical startup.
  uint16_t on=channel*512,off=(on+ticks)&4095;
  Wire.beginTransmission(cfg::pcaAddress);Wire.write(uint8_t(0x06+4*channel));
  Wire.write(uint8_t(on));Wire.write(uint8_t(on>>8));Wire.write(uint8_t(off));Wire.write(uint8_t(off>>8));
  return Wire.endTransmission()==0;
 }
};
}

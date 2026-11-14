#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <driver/rmt.h>
#include "core.h"
class ServoDriver {
 bool ready=false;crab::ServoTelemetry last[8];
 bool reg(uint8_t r,uint8_t value){Wire.beginTransmission(cfg::PCA_ADDR);Wire.write(r);Wire.write(value);return Wire.endTransmission()==0;}
 public:
 // Also called before LCD initialization, which may take time or fail.
 void inhibit(){if(cfg::PCA_OE_PIN>=0){digitalWrite(cfg::PCA_OE_PIN,HIGH);pinMode(cfg::PCA_OE_PIN,OUTPUT);}}
 bool begin(){
  ready=false;inhibit();
  Wire.begin(cfg::SDA_PIN,cfg::SCL_PIN,100000);Wire.setTimeOut(10);
  // Kill all 16 outputs, including any state retained during MCU-only reset.
  bool ok=true;for(int i=0;i<16;i++)ok=off(i)&&ok;
  if(!ok)return false;
  if(!reg(0x00,0x30)||!reg(0xfe,121)||!reg(0x01,0x04)||!reg(0x00,0x20))return false;
  delayMicroseconds(600);ready=true;return true; // one-time oscillator startup only
 }
 bool off(int ch){
  if(ch<0||ch>=16)return false;
  bool ok=reg(0x09+4*ch,0x10);
  if(ch<8){last[ch].known=ok;last[ch].active=false;}
  return ok;
 }
 void snapshot(crab::ServoTelemetry (&out)[8])const{for(int ch=0;ch<8;ch++)out[ch]=last[ch];}
 bool write(int ch,int on,int off){
  if(ch<0||ch>15)return false;
  Wire.beginTransmission(cfg::PCA_ADDR);Wire.write(0x06+4*ch);Wire.write(on&255);Wire.write((on>>8)&31);Wire.write(off&255);Wire.write((off>>8)&31);return Wire.endTransmission()==0;
 }
 // Hard off without clearing the driver's initialised/fault state.
 bool disableOutputs(){inhibit();bool ok=true;for(int ch=0;ch<16;ch++)ok=off(ch)&&ok;return ok;}
 bool pulseCounts(int ch,int counts){
  if(!ready||ch<0||ch>7||counts<1||counts>4095)return false;
  int on=ch*512;
  if(!write(ch,on,(on+counts)&4095)){allOff();return false;}
  last[ch].known=last[ch].active=true;last[ch].counts=counts;last[ch].pulseUs=int(std::lround(crab::nominalUs(counts)));
  if(cfg::PCA_OE_PIN>=0)digitalWrite(cfg::PCA_OE_PIN,LOW);
  return true;
 }
 bool pulse(int ch,int us){
  if(!pulseCounts(ch,crab::pwmCounts(us)))return false;
  last[ch].pulseUs=us;return true;
 }

 void allOff(){inhibit();ready=false;for(int ch=0;ch<16;ch++)off(ch);}
};
class LightDriver {
 bool available=false;
 public:
 bool begin(){rmt_config_t c={};c.rmt_mode=RMT_MODE_TX;c.channel=RMT_CHANNEL_0;c.gpio_num=(gpio_num_t)cfg::LED_PIN;c.clk_div=8;c.mem_block_num=1;c.tx_config.idle_output_en=true;c.tx_config.idle_level=RMT_IDLE_LEVEL_LOW;
  available=rmt_config(&c)==ESP_OK&&rmt_driver_install(c.channel,0,0)==ESP_OK;if(available)set(false);return available;
 }
 void set(bool on){color(on?255:0,on?255:0,on?255:0);}
 // WS2812 GRB order; each channel scaled to the LED_BRIGHTNESS power cap.
 void color(uint8_t r,uint8_t g,uint8_t b){if(!available)return;const uint8_t rgb[3]={g,r,b};rmt_item32_t bits[24*cfg::LED_COUNT]={};for(int led=0;led<cfg::LED_COUNT;led++)for(int color=0;color<3;color++){uint8_t v=uint8_t((rgb[color]*cfg::LED_BRIGHTNESS+127)/255);for(int b=0;b<8;b++){bool high=(v&(128>>b));auto& item=bits[led*24+color*8+b];item.level0=1;item.duration0=high?8:4;item.level1=0;item.duration1=high?5:9;}}
  rmt_write_items(RMT_CHANNEL_0,bits,24*cfg::LED_COUNT,true);delayMicroseconds(80);
 }
};
// Two HC-SR04P at the front (cfg::SONAR_TRIG/ECHO). Each service call reads the
// previous ping's result and fires the other sensor, so nothing blocks the
// loop. Echo edges are timestamped in an interrupt: a busy-wait in loop() is
// preempted by the motion task's I2C frames and would read obstacles as farther.
class SonarDriver {
 public:
 struct Capture {int pin=-1;volatile uint32_t rise=0,width=0;volatile bool rose=false,fell=false;};
 Capture cap[2];
 private:
 bool available=false,pending=false;int next=0,fired=0;uint32_t last=0;
 // ARDUINO_ISR_ATTR: IRAM only when the core installs IRAM-flagged GPIO ISRs (not in 2.0.14).
 static void ARDUINO_ISR_ATTR edge(void* arg){
  Capture& c=*static_cast<Capture*>(arg);const uint32_t t=micros();
  if(digitalRead(c.pin)==HIGH){if(!c.rose){c.rise=t;c.rose=true;}}
  else if(c.rose&&!c.fell){c.width=t-c.rise;c.fell=true;}
 }
 public:
 bool begin(){
  available=cfg::SONAR_TRIG[0]>=0&&cfg::SONAR_TRIG[1]>=0;if(!available)return false;
  for(int i=0;i<2;i++){
   cap[i].pin=cfg::SONAR_ECHO[i];
   digitalWrite(cfg::SONAR_TRIG[i],LOW);pinMode(cfg::SONAR_TRIG[i],OUTPUT);
   // Pulled down: an unplugged sensor never shows a rising edge, so it reads absent.
   pinMode(cfg::SONAR_ECHO[i],INPUT_PULLDOWN);attachInterruptArg(cfg::SONAR_ECHO[i],edge,&cap[i],CHANGE);
  }
  return true;
 }
 bool present()const{return available;}
 bool service(crab::Sonar& s,uint32_t now){
  if(!available||now-last<cfg::SONAR_PERIOD_MS)return false;last=now;
  if(pending){
   Capture& c=cap[fired];
   // Echo still high after the period: beyond range (the module's own timeout).
   s.side[fired].ping(c.rose,c.fell&&c.width<=uint32_t(cfg::SONAR_MAX_CM)*58,c.width,now);
  }
  fired=next;next^=1;Capture& c=cap[fired];
  noInterrupts();c.rose=c.fell=false;c.width=0;interrupts();
  digitalWrite(cfg::SONAR_TRIG[fired],HIGH);delayMicroseconds(10);digitalWrite(cfg::SONAR_TRIG[fired],LOW);
  pending=true;return true;
 }
};

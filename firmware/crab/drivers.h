#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <driver/rmt.h>
#include "core.h"
class ServoDriver {
 bool ready=false;
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
 bool off(int ch){return ch>=0&&ch<16&&reg(0x09+4*ch,0x10);}
 bool write(int ch,int on,int off){
  if(ch<0||ch>15)return false;
  Wire.beginTransmission(cfg::PCA_ADDR);Wire.write(0x06+4*ch);Wire.write(on&255);Wire.write((on>>8)&31);Wire.write(off&255);Wire.write((off>>8)&31);return Wire.endTransmission()==0;
 }
 bool pulse(int ch,int us){
  if(!ready||ch<0||ch>7)return false;
  int on=ch*512;
  if(!write(ch,on,(on+(us*4096L+10000)/20000)&4095)){allOff();return false;}
  if(cfg::PCA_OE_PIN>=0)digitalWrite(cfg::PCA_OE_PIN,LOW);
  return true;
 }
 void allOff(){inhibit();ready=false;for(int ch=0;ch<16;ch++)off(ch);}
};
class LightDriver {
 bool available=false;
 public:
 bool begin(){rmt_config_t c={};c.rmt_mode=RMT_MODE_TX;c.channel=RMT_CHANNEL_0;c.gpio_num=(gpio_num_t)cfg::LED_PIN;c.clk_div=8;c.mem_block_num=1;c.tx_config.idle_output_en=true;c.tx_config.idle_level=RMT_IDLE_LEVEL_LOW;
  available=rmt_config(&c)==ESP_OK&&rmt_driver_install(c.channel,0,0)==ESP_OK;if(available)set(false);return available;
 }
 void set(bool on){if(!available)return;rmt_item32_t bits[24*cfg::LED_COUNT]={};for(int led=0;led<cfg::LED_COUNT;led++)for(int color=0;color<3;color++){uint8_t v=on?cfg::LED_BRIGHTNESS:0;for(int b=0;b<8;b++){bool high=(v&(128>>b));auto& item=bits[led*24+color*8+b];item.level0=1;item.duration0=high?8:4;item.level1=0;item.duration1=high?5:9;}}
  rmt_write_items(RMT_CHANNEL_0,bits,24*cfg::LED_COUNT,true);delayMicroseconds(80);
 }
};

#pragma once
#include <TFT_eSPI.h>
#include "QrEncoder.h"
#include "Font.h"
#include "Robot.h"
class Display {
 TFT_eSPI tft;
 crab::Str previous;
 void text(const crab::Str& s,int y){
  int x=5;
  for(size_t i=0;i<s.size();){
   uint32_t cp=(uint8_t)s[i++];
   if(cp>=0xC0){int n=cp<0xE0?1:cp<0xF0?2:3;cp&=n==1?31:n==2?15:7;while(n--&&i<s.size())cp=(cp<<6)|((uint8_t)s[i++]&63);}
   if(cp=='\n'||x+10>165){x=5;y+=19;if(cp=='\n')continue;}
   if(y+18>320)break;
   for(const auto& glyph:glyphs)if(glyph.cp==cp){tft.drawBitmap(x,y,glyph.bits,10,18,TFT_BLACK);break;}
   x+=10;
  }
 }
 public:
 void begin(){pinMode(CRAB_POWER_ON,OUTPUT);digitalWrite(CRAB_POWER_ON,HIGH);tft.init();tft.setRotation(0);tft.fillScreen(TFT_WHITE);digitalWrite(CRAB_LCD_BL,HIGH);}
 void show(const crab::Str& payload,const crab::Str& message,const crab::Str& address){
  crab::Str key=payload+message+address;if(key==previous)return;previous=key;
  tft.fillScreen(TFT_WHITE);QRCode qr;uint8_t buffer[128];
  if(qrcode_initText(&qr,buffer,3,ECC_MEDIUM,payload.c_str())<0){text("Lỗi mã QR",10);return;}
  // Version 3: 29 modules, 4-module quiet zone on all sides, 4px/module.
  constexpr int scale=4,left=11,top=5,quiet=4;
  for(int y=0;y<qr.size;y++)for(int x=0;x<qr.size;x++)if(qrcode_getModule(&qr,x,y))tft.fillRect(left+(x+quiet)*scale,top+(y+quiet)*scale,scale,scale,TFT_BLACK);
  text(message,161);text(address,275);
 }
};

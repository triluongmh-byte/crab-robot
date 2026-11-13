#pragma once
#include <stdint.h>
// Claude-pet style face (owner, 2026-11-13): two eyes drawn as shapes, not a
// bitmap. Idle: slow blink every 2.5-5.5 s and an occasional sideways glance.
// Walking or performing an emotion: happy squint arcs.
namespace crab {
struct EyeFrame {
 int8_t look=0;     // -1 left, 0 centre, 1 right (screen x)
 uint8_t open=100;  // percent of full eye height
 bool happy=false;  // ^ ^ arcs instead of open eyes
 bool operator==(const EyeFrame& o)const{return look==o.look&&open==o.open&&happy==o.happy;}
 bool operator!=(const EyeFrame& o)const{return !(*this==o);}
};
struct Eyes {
 static constexpr uint32_t BLINK_MS=160;
 uint32_t seed=0x2545f491u,nextBlink=2500,blinkStart=0,nextGlance=6000,glanceUntil=0;
 int8_t glance=0;bool blinking=false;
 uint32_t rnd(uint32_t lo,uint32_t hi){seed=seed*1664525u+1013904223u;return lo+(seed>>8)%(hi-lo+1);}
 static bool due(uint32_t now,uint32_t at){return int32_t(now-at)>=0;}
 EyeFrame frame(uint32_t now,bool active){
  EyeFrame f;
  if(active){blinking=false;glance=0;nextBlink=now+rnd(2500,5500);nextGlance=now+rnd(5000,10000);f.happy=true;return f;}
  if(!blinking&&due(now,nextBlink)){blinking=true;blinkStart=now;}
  if(blinking){
   const uint32_t t=now-blinkStart,half=BLINK_MS/2;
   if(t>=BLINK_MS){blinking=false;nextBlink=now+rnd(2500,5500);}
   else f.open=uint8_t(t<half?100-t*90/half:10+(t-half)*90/half);
  }
  if(glance==0&&due(now,nextGlance)){glance=rnd(0,1)?1:-1;glanceUntil=now+rnd(700,1500);}
  else if(glance!=0&&due(now,glanceUntil)){glance=0;nextGlance=now+rnd(5000,10000);}
  f.look=glance;return f;
 }
};
}

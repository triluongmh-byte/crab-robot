#pragma once
#include <stdint.h>
#include "config.h"
// Claude-pet style face (owner, 2026-11-13/14): two eyes drawn as shapes, not a
// bitmap, in the lamp's colour. Idle: blinks (sometimes double), smooth glances
// in four directions, short smiles and wide-eyed moments; sleepy after a minute
// without commands, asleep after three. Walking: happy bouncing arcs looking
// towards the travel side. The emotion page picks a mood per emotion.
namespace crab {
enum class Mood:uint8_t {Normal,Happy,Sad,Angry,Sleepy,Surprised,Love,Asleep,Wink};
constexpr int MOOD_COUNT=9;
inline const char* moodName(Mood m){
 static const char* n[MOOD_COUNT]={"normal","happy","sad","angry","sleepy","surprised","love","asleep","wink"};
 return n[uint8_t(m)<MOOD_COUNT?uint8_t(m):0];
}
inline bool moodFromName(const char* s,Mood& out){
 for(int i=0;i<MOOD_COUNT;i++){const char* n=moodName(Mood(i));int k=0;while(n[k]&&s[k]==n[k])k++;if(!n[k]&&!s[k]){out=Mood(i);return true;}}
 return false;
}
// Lamp colour -> eye colour (RGB565): same hue at full brightness so a dim or
// capped LED colour still reads on the screen; lamp off/black -> white eyes.
inline uint16_t eyeColor(uint32_t rgb){
 int r=(rgb>>16)&255,g=(rgb>>8)&255,b=rgb&255;const int m=r>g?(r>b?r:b):(g>b?g:b);
 if(m==0)return 0xffff;
 r=(r*255+m/2)/m;g=(g*255+m/2)/m;b=(b*255+m/2)/m;
 return uint16_t(((r>>3)<<11)|((g>>2)<<5)|(b>>3));
}
struct EyeFrame {
 int8_t lookX=0,lookY=0; // pixel offset of both eyes (screen x right, y down)
 uint8_t open=100;       // percent of full eye height (blinks, sleepy)
 Mood mood=Mood::Normal;
 uint16_t color=0xffff;  // RGB565
 bool operator==(const EyeFrame& o)const{return lookX==o.lookX&&lookY==o.lookY&&open==o.open&&mood==o.mood&&color==o.color;}
 bool operator!=(const EyeFrame& o)const{return !(*this==o);}
};
// What the robot is doing, sampled by the loop under the motion lock.
struct EyeInput {
 bool walking=false;     // walking amplitude is up
 bool posing=false;      // an emotion pose holds the lease
 int8_t sideX=0,sideY=0; // travel direction on screen: x -1/0/1, y -1 up (forward) / 1 down (back)
 Mood mood=Mood::Normal; // emotion page mood (Normal = none)
 uint32_t idleMs=0;      // since the last drive/pose command
 uint16_t color=0xffff;
};
// Drive command -> where the eyes look on screen (see cfg::EYE_LOOK_SIGN).
inline void travelLook(int dir,int8_t& x,int8_t& y){
 const int s=cfg::EYE_LOOK_SIGN;
 x=int8_t(dir==3||dir==5||dir==7?s:dir==4||dir==6||dir==8?-s:0);
 y=int8_t(dir==1||dir==5||dir==6?-1:dir==2||dir==7||dir==8?1:0);
}
struct Eyes {
 static constexpr uint32_t BLINK_MS=160,SLEEPY_BLINK_MS=600;
 static constexpr int LOOK_X=24,LOOK_Y=12;
 uint32_t seed=0x2545f491u,nextBlink=2500,blinkStart=0,blinkLen=BLINK_MS,nextGlance=6000,glanceUntil=0,nextQuirk=15000,quirkUntil=0,last=0,surpriseUntil=0;
 uint8_t blinksLeft=0;
 bool blinking=false,glancing=false,wasActive=false,drowsy=false,surprised=false;
 int8_t targetX=0,targetY=0;float x=0,y=0;
 Mood quirk=Mood::Normal;
 uint32_t rnd(uint32_t lo,uint32_t hi){seed=seed*1664525u+1013904223u;return lo+(seed>>8)%(hi-lo+1);}
 static bool due(uint32_t now,uint32_t at){return int32_t(now-at)>=0;}
 // Ease the gaze towards its target, about 0.25 px/ms (a full glance ~100 ms).
 void ease(uint32_t now){
  const uint32_t dt=now-last;last=now;const float step=float(dt<200?dt:200)*.25f;
  auto toward=[&](float& v,int t){if(v<t)v=v+step<t?v+step:t;else if(v>t)v=v-step>t?v-step:t;};
  toward(x,targetX);toward(y,targetY);
 }
 uint8_t blinkOpen(uint32_t now){
  if(!blinking&&due(now,nextBlink)){blinking=true;blinkStart=now;}
  if(!blinking)return 100;
  const uint32_t t=now-blinkStart,half=blinkLen/2;
  if(t>=blinkLen){
   blinking=false;
   // About one blink in four is a double blink.
   if(blinksLeft){blinksLeft--;nextBlink=now+90;}
   else{nextBlink=now+rnd(2500,5500);if(rnd(0,3)==0)blinksLeft=1;}
   return 100;
  }
  return uint8_t(t<half?100-t*90/half:10+(t-half)*90/half);
 }
 EyeFrame look(EyeFrame f,uint32_t now){ease(now);f.lookX=int8_t(x);f.lookY=int8_t(y);return f;}
 EyeFrame frame(uint32_t now,const EyeInput& in){
  EyeFrame f;f.color=in.color;
  const bool active=in.walking||in.posing||in.mood!=Mood::Normal;
  if(active){
   // Woken from sleep or drowsiness: a short wide-eyed surprise first.
   if(drowsy){drowsy=false;surprised=true;surpriseUntil=now+700;}
   if(surprised&&due(now,surpriseUntil))surprised=false;
   wasActive=true;glancing=false;quirk=Mood::Normal;blinkLen=BLINK_MS;
   f.mood=in.mood!=Mood::Normal?in.mood:surprised?Mood::Surprised:in.walking?Mood::Happy:Mood::Normal;
   targetX=int8_t(in.sideX*LOOK_X);targetY=int8_t(in.sideY*LOOK_Y/2);
   if(in.walking&&in.mood==Mood::Normal){
    // Bounce with the stride: 3 px up and down every 400 ms.
    const int p=int(now%400);targetY=int8_t(targetY+(p<200?p*3/100-3:3-(p-200)*3/100));
   }
   f=look(f,now);
   const bool blinkable=f.mood!=Mood::Happy&&f.mood!=Mood::Wink&&f.mood!=Mood::Asleep;
   f.open=blinkable?blinkOpen(now):100;
   if(f.mood==Mood::Sleepy)f.open=uint8_t(f.open*45/100);
   nextGlance=now+rnd(4000,9000);nextQuirk=now+rnd(15000,30000);
   return f;
  }
  if(wasActive){wasActive=false;targetX=0;targetY=0;}
  if(surprised&&due(now,surpriseUntil))surprised=false;
  if(surprised){f.mood=Mood::Surprised;targetX=0;targetY=0;return look(f,now);}
  if(in.idleMs>=cfg::ASLEEP_MS){drowsy=true;f.mood=Mood::Asleep;targetX=0;targetY=0;return look(f,now);}
  const bool sleepy=in.idleMs>=cfg::SLEEPY_MS;
  if(sleepy){
   drowsy=true;glancing=false;quirk=Mood::Normal;targetX=0;targetY=6;blinkLen=SLEEPY_BLINK_MS;
   f.mood=Mood::Sleepy;f=look(f,now);f.open=uint8_t(blinkOpen(now)*45/100);if(f.open<6)f.open=6;return f;
  }
  blinkLen=BLINK_MS;
  // Glances: left/right, sometimes up or down, held 0.7-1.5 s.
  if(!glancing&&due(now,nextGlance)){
   glancing=true;glanceUntil=now+rnd(700,1500);
   const uint32_t k=rnd(0,5);
   targetX=int8_t(k<2?-LOOK_X:k<4?LOOK_X:0);targetY=int8_t(k==4?-LOOK_Y:k==5?LOOK_Y:(rnd(0,2)==0?-LOOK_Y/2:0));
  }else if(glancing&&due(now,glanceUntil)){glancing=false;targetX=0;targetY=0;nextGlance=now+rnd(4000,9000);}
  // Small idle quirks: a smile, a wide-eyed look, a wink, a heart now and then.
  if(quirk==Mood::Normal&&due(now,nextQuirk)){
   const uint32_t k=rnd(0,9);quirk=k<5?Mood::Happy:k<7?Mood::Surprised:k<9?Mood::Wink:Mood::Love;quirkUntil=now+rnd(900,1600);
  }else if(quirk!=Mood::Normal&&due(now,quirkUntil)){quirk=Mood::Normal;nextQuirk=now+rnd(15000,30000);}
  f.mood=quirk;f=look(f,now);
  if(quirk==Mood::Normal||quirk==Mood::Surprised)f.open=blinkOpen(now);
  return f;
 }
 // Walking flag only (older callers and tests).
 EyeFrame frame(uint32_t now,bool active){EyeInput in;in.walking=active;return frame(now,in);}
};
}

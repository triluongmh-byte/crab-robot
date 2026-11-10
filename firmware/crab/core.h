// SPDX-License-Identifier: GPL-3.0-or-later
// Non-blocking adaptation of Kame32's amplitude/offset/phase oscillator design.
#pragma once
#include "config.h"
#include <algorithm>
#include <cstdio>
#include <cmath>
#include <stdint.h>
#include <string>
namespace crab {
inline float clamp(float x,float lo,float hi){return std::max(lo,std::min(hi,x));}
inline uint32_t elapsed(uint32_t now,uint32_t then){return now-then;}
struct Vec {float x,y; Vec(float x_=0,float y_=0):x(x_),y(y_){} };
inline Vec direction(int n){
 const Vec d[9]={{0,0},{1,0},{-1,0},{0,1},{0,-1},{.70710678f,.70710678f},
 {.70710678f,-.70710678f},{-.70710678f,.70710678f},{-.70710678f,-.70710678f}};
 return n>=0&&n<=8?d[n]:Vec{};
}
// Project commanded translation onto the tangent at each radial hip.
// Stance (sin phase <= 0) pushes the floor opposite the travel vector.
inline float hipProjection(int leg,Vec v){return -std::sin(cfg::RADIAL[leg])*v.x+std::cos(cfg::RADIAL[leg])*v.y;}
inline void gait(float phase,Vec v,float amplitude,float out[8]){
 for(int l=0;l<4;l++){
  const float a=phase+cfg::PHASE[l];
  out[2*l]=-cfg::HIP_AMPLITUDE*hipProjection(l,v)*std::cos(a)*amplitude;
  out[2*l+1]=-cfg::KNEE_LIFT*std::max(0.0f,std::sin(a))*amplitude;
 }
}
inline int pulse(int ch,float angle,float offset,bool raw=false){
 if(raw)return cfg::CENTRE_US;
 float degrees=cfg::SIGN[ch]*clamp(angle,-cfg::JOINT_LIMIT,cfg::JOINT_LIMIT)+clamp(offset,-cfg::TRIM_LIMIT,cfg::TRIM_LIMIT);
 return int(std::lround(cfg::CENTRE_US+cfg::US_PER_DEG*degrees));
}
inline std::string apName(uint32_t mac){char s[24];snprintf(s,sizeof(s),"CuaRobot-%04X",unsigned(mac&0xFFFF));return s;}
inline std::string wifiQr(const std::string& ap){return "WIFI:T:nopass;S:"+ap+";;";}
inline std::string webQr(const std::string& ip){return "http://"+ip+"/";}
// Vietnamese strings are shared by the display, HTTP status and host tests.
namespace msg {
constexpr const char* SETUP="Quét QR để nối cua";
constexpr const char* JOINING="Đang vào Wi-Fi...";
constexpr const char* ONLINE="Đã vào Wi-Fi";
constexpr const char* FAILED="Sai mật khẩu hoặc mất sóng";
constexpr const char* LOST="Mất Wi-Fi. Vẫn dùng cua";
constexpr const char* ERASED="Đã xóa Wi-Fi";
constexpr const char* DRIVER="Kiểm tra dây PCA9685";
}
enum class NetState {Setup,Connecting,Online};
struct Network {
 NetState state=NetState::Setup;
 bool pending=false, saved=false, saveRequested=false, retryRequested=false, pauseRequested=false;
 uint32_t since=0,retryAt=0;
 const char* message=msg::SETUP;
 void begin(bool hasSaved,uint32_t now){saved=hasSaved;if(saved)connect(false,now);}
 void connect(bool candidate,uint32_t now){state=NetState::Connecting;pending=candidate;since=now;message=msg::JOINING;}
 // Single-radio policy: do not start/restart saved-network association while
 // AP clients are attached. Cancel an in-flight background attempt on AP join.
 void pauseRetry(uint32_t now){
  if(state==NetState::Connecting&&!pending){state=NetState::Setup;message=msg::SETUP;retryAt=now;retryRequested=false;pauseRequested=true;}
 }
 void tick(uint32_t now,bool connected,bool hardFail=false,bool apClients=false){
  if(apClients&&!connected)pauseRetry(now);
  if(state==NetState::Connecting){
   if(connected){state=NetState::Online;message=msg::ONLINE;saveRequested=pending; saved=saved||pending;pending=false;}
   else if(hardFail||elapsed(now,since)>=18000){state=NetState::Setup;message=msg::FAILED;pending=false;retryAt=now;}
  }else if(state==NetState::Online&&!connected){state=NetState::Setup;message=msg::LOST;retryAt=now;}
  else if(state==NetState::Setup&&saved&&!apClients&&elapsed(now,retryAt)>=30000){retryRequested=true;connect(false,now);}
 }
 void erase(uint32_t now){*this=Network{};retryAt=now;message=msg::ERASED;}
};
struct HoldButton {
 bool down=false,fired=false;uint32_t since=0;
 bool tick(bool pressed,uint32_t now){
  if(!pressed){down=false;fired=false;return false;}
  if(!down){down=true;since=now;}
  if(!fired&&elapsed(now,since)>=cfg::BOOT_HOLD_MS){fired=true;return true;}return false;
 }
};
// All methods called under the firmware's mutex; network task never writes PWM.
struct Motion {
 float offsets[8]={},position[8]={};
 Vec velocity{};
 float amplitude=0,phase=0,speed=.65f;
 bool assembly=false,raw=false,inhibit=false,lease=false;
 uint32_t session=0,lastSeq=0,lastCommand=0,start=0,lastTick=0;
 int enabled=0,cursor=0;
 void begin(uint32_t now){start=lastTick=now;enabled=0;}
 void stop(){velocity={};lease=false;}
 bool command(uint32_t id,uint32_t seq,int dir,uint32_t now,bool fresh=true){
  if(!id||id!=session||seq<=lastSeq||dir<0||dir>8)return false;
  lastSeq=seq;
  if(dir==0){stop();return true;}
  if(inhibit||assembly||enabled<8)return false;
  if(!fresh&&(!lease||elapsed(now,lastCommand)>=cfg::DEADMAN_MS)){stop();return false;}
  velocity=direction(dir);lastCommand=now;lease=true;return true;
 }
 void newSession(uint32_t id){stop();session=id;lastSeq=0;}
 void setAssembly(bool active){stop();assembly=active;raw=false;}
 void centre(){stop();assembly=true;raw=true;}
 bool trim(int ch,int delta){if(!assembly||ch<0||ch>7||std::abs(delta)!=1)return false;raw=false;offsets[ch]=clamp(offsets[ch]+delta,-cfg::TRIM_LIMIT,cfg::TRIM_LIMIT);return true;}
 // One channel update per 10 ms; 300 ms gaps on initial enable.
 // angle+offset slew is enforced in the driver, so trim also moves smoothly.
 int tick(uint32_t now){
  if(elapsed(now,lastTick)<10)return -1;
  const float dt=std::min(elapsed(now,lastTick)*.001f,.05f);lastTick=now;
  if(inhibit||assembly||elapsed(now,lastCommand)>=cfg::DEADMAN_MS)stop();
  if(enabled<8){if(elapsed(now,start)<uint32_t(enabled)*cfg::ENABLE_GAP_MS)return -1;return enabled++;}
  const bool moving=std::fabs(velocity.x)+std::fabs(velocity.y)>.01f;
  // Keep last heading through amplitude decay to avoid snapping the hip target.
  amplitude=clamp(amplitude+(moving?dt*1.5f:-dt*4.0f),0,1);
  if(moving)heading=velocity;
  if(moving)phase=std::fmod(phase+dt*6.2831853072f*speed/cfg::PERIOD_S,6.2831853072f);
  float target[8]={};if(!assembly)gait(phase,heading,amplitude,target);
  int ch=cursor;cursor=(cursor+1)%8;
  position[ch]+=clamp(target[ch]-position[ch],-cfg::SLEW_DPS*.08f,cfg::SLEW_DPS*.08f);
  return ch;
 }
 private:Vec heading{};
};
}

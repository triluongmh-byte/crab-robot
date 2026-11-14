// SPDX-License-Identifier: GPL-3.0-or-later
// Non-blocking adaptation of Kame32's amplitude/offset/phase oscillator design.
#pragma once
#include "continuous360.h"
#include "config.h"
#include "eyes.h"
#include "autopilot.h"
#include <algorithm>
#include <cstdio>
#include <cmath>
#include <stdint.h>
#include <string>
namespace crab {
inline float clamp(float x,float lo,float hi){return std::max(lo,std::min(hi,x));}
inline uint32_t elapsed(uint32_t now,uint32_t then){return now-then;}
// Last acknowledged output command, not position feedback from the servo.
struct ServoTelemetry {bool known=false,active=false;int pulseUs=0,counts=0;};
struct Vec {float x,y; Vec(float x_=0,float y_=0):x(x_),y(y_){} };
inline Vec direction(int n){
 const Vec d[9]={{0,0},{1,0},{-1,0},{0,1},{0,-1},{.70710678f,.70710678f},
 {.70710678f,-.70710678f},{-.70710678f,.70710678f},{-.70710678f,-.70710678f}};
 return n>=0&&n<=8?d[n]:Vec{};
}
// Owner drive command in the CAD frame: 1 Forward, 2 Backward, 3 Left, 4 Right;
// 5..8 are arcs (forward-left, forward-right, back-left, back-right) that walk
// forward/back while turning the body; see bodyYaw.
inline Vec bodyDirection(int n){Vec d=direction(n>=5&&n<=8?(n<=6?1:2):n);return cfg::FRONT_IS_CH46?Vec{-d.x,-d.y}:d;}
// Body turn rate share, + = counter-clockwise seen from above (turn left). A
// 180-degree frame rotation keeps the turn sense. Reversing with "left" swings
// the tail left, which turns the body clockwise (car convention).
inline float bodyYaw(int n){return n==5||n==8?cfg::ARC_YAW:n==6||n==7?-cfg::ARC_YAW:0.f;}
// Project body translation onto each hip tangent in the nominal CAD frame.
inline float hipProjection(int leg,Vec v){return -std::sin(cfg::RADIAL[leg])*v.x+std::cos(cfg::RADIAL[leg])*v.y;}
// Physical right side (y<0 in the owner's frame); see cfg::FRONT_IS_CH46.
inline bool physicalRight(int leg){const bool cadLeft=std::sin(cfg::RADIAL[leg])>0;return cfg::FRONT_IS_CH46?cadLeft:!cadLeft;}
inline void applyBalance(float out[8],int percent){
 const float p=clamp(float(percent),-cfg::BALANCE_LIMIT,cfg::BALANCE_LIMIT)*.01f;
 for(int leg=0;leg<4;leg++)out[2*leg]*=1+(physicalRight(leg)?p:-p);
}
inline float smooth(float x){x=clamp(x,0,1);return x*x*(3-2*x);}
enum class Pattern:uint8_t {Trot,Pairs,Flick};
inline const cfg::GaitPattern& pattern(Pattern p){return p==Pattern::Pairs?cfg::PAIRS:cfg::TROT;}
inline const char* patternName(Pattern p){return p==Pattern::Pairs?"pairs":p==Pattern::Flick?"flick":"trot";}
// Flick only replaces axial Forward/Backward; sideways and diagonals trot.
inline bool flickActive(Pattern p,Vec v,float yaw=0){return p==Pattern::Flick&&std::fabs(yaw)<.01f&&std::fabs(v.x)>std::fabs(v.y)+.01f;}
inline float cyclePeriod(Pattern p,Vec v,float yaw=0){return flickActive(p,v,yaw)?cfg::FLICK_PERIOD_S:cfg::PERIOD_S;}
// The stance is 180-deg symmetric, so identical knee timing on every leg
// cannot pick a direction (owner video IMG_2637: it only bounced). Timing is
// set by geometry instead: a trailing leg (foot pointing away from travel)
// gets the power stroke, a slow lift then a fast drop that strikes and pushes;
// a leading leg snaps up fast and lowers slowly so it drags little.
inline void flick(float phase,Vec v,float amplitude,float out[8],float hip=cfg::FLICK_HIP,float knee=cfg::KNEE_LIFT){
 const float cycle=phase/6.2831853072f;
 for(int leg=0;leg<4;leg++){
  // CAD legs 0,1 swing their feet towards +X, legs 2,3 towards -X.
  const Vec pose(leg<2?1.f:-1.f,0);
  out[2*leg]=clamp(hip,0,cfg::FLICK_HIP)*clamp(hipProjection(leg,pose)*1.4142135624f,-1,1)*amplitude;
  const float group=(leg==0||leg==3)?0:.5f;
  float u=cycle-group-std::floor(cycle-group);
  const bool leading=pose.x*v.x>0;
  if(!leading)u=1-u;
  const float k=u<cfg::FLICK_STROKE?smooth(u/cfg::FLICK_STROKE):1-smooth((u-cfg::FLICK_STROKE)/(1-cfg::FLICK_STROKE));
  out[2*leg+1]=-clamp(knee,0,cfg::KNEE_LIFT_MAX)*k*amplitude;
 }
}
inline void gait(float phase,Vec v,float amplitude,float out[8],Pattern which=Pattern::Trot,float flickHip=cfg::FLICK_HIP,float knee=cfg::KNEE_LIFT,float yaw=0){
 if(flickActive(which,v,yaw)){flick(phase,v,amplitude,out,flickHip,knee);return;}
 yaw=clamp(yaw,-1,1);
 knee=clamp(knee,0,cfg::KNEE_LIFT_MAX);
 const cfg::GaitPattern& g=pattern(which);
 // Begin at mid stance: hips start from neutral, not an opposite kick.
 const float cycle=phase/6.2831853072f+g.start;
 const float swingEnd=g.stance+g.lift+g.swing,lower=1-swingEnd;
 for(int leg=0;leg<4;leg++){
  const float local=cycle-g.group[leg]-std::floor(cycle-g.group[leg]);
  float hip,lift=0;
  if(local<g.stance)hip=1-2*(g.linearStance?local/g.stance:smooth(local/g.stance));
  else if(local<g.stance+g.lift){hip=-1;lift=(local-g.stance)/g.lift;}
  else if(local<swingEnd){hip=-1+2*smooth((local-g.stance-g.lift)/g.swing);lift=1;}
  else{hip=1;lift=(1-local)/lower;}
  // Use the available full hip stroke for axial Forward/Backward commands.
  // Turning: the same push on every hip turns the body (grounded feet sweep
  // clockwise relative to the body for a counter-clockwise turn).
  const float push=clamp(clamp(hipProjection(leg,v)*1.4142135624f,-1,1)*(1-std::fabs(yaw))+yaw,-1,1);
  out[2*leg]=cfg::HIP_AMPLITUDE*push*hip*amplitude;
  out[2*leg+1]=-knee*lift*amplitude;
 }
}
inline int pulse(int ch,float angle,float offset,bool raw=false){
 if(raw)return cfg::CENTRE_US;
 // Clamp AFTER mirror and trim: trim cannot bypass the owner's travel budget.
 // Owner-requested hip range for the 90 deg knee-flick stance; knees unchanged.
 const float limit=ch%2?cfg::KNEE_PULSE_LIMIT:cfg::HIP_LIMIT,request=ch%2?cfg::KNEE_LIFT_MAX:cfg::HIP_LIMIT;
 float degrees=clamp(cfg::SIGN[ch]*clamp(angle,-request,request)+clamp(offset,-cfg::TRIM_LIMIT,cfg::TRIM_LIMIT),-limit,limit);
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
constexpr const char* FAILED="Không vào được Wi-Fi";
constexpr const char* WRONG_PASS="Sai mật khẩu Wi-Fi";
constexpr const char* NOT_FOUND="Không thấy Wi-Fi này";
constexpr const char* LOST="Mất Wi-Fi. Vẫn dùng cua";
constexpr const char* ERASED="Đã xóa Wi-Fi";
constexpr const char* DRIVER="Kiểm tra dây PCA9685";
}
enum class NetState {Setup,Connecting,Online};
// Failure reported by the radio for the current attempt only (from the
// disconnect event, never the cached WiFi.status(), which keeps an older
// attempt's NO_SSID_AVAIL and used to cancel a new home Wi-Fi join at 0.5 s).
enum class WifiFail:uint8_t {None,NotFound,Auth};
// ESP-IDF disconnect reasons: 201 NO_AP_FOUND, 202 AUTH_FAIL, 15 4-way
// handshake timeout and 204 handshake timeout (wrong WPA2 password), 8 our own
// ASSOC_LEAVE (ignored). Anything else: scan again while the attempt lasts.
inline WifiFail wifiFailFromReason(int r){if(r==0||r==8)return WifiFail::None;if(r==202||r==15||r==204)return WifiFail::Auth;return WifiFail::NotFound;}
struct Network {
 static constexpr uint32_t ATTEMPT_MS=18000,RETRY_MS=30000;
 NetState state=NetState::Setup;
 bool pending=false, saved=false, saveRequested=false, retryRequested=false, pauseRequested=false, rescanRequested=false;
 bool failedOnce=false; // an attempt failed since the last time online
 uint8_t authFails=0;bool sawNotFound=false;
 uint32_t since=0,retryAt=0;
 const char* message=msg::SETUP;
 void begin(bool hasSaved,uint32_t now){saved=hasSaved;if(saved)connect(false,now);}
 void connect(bool candidate,uint32_t now){state=NetState::Connecting;pending=candidate;since=now;message=msg::JOINING;authFails=0;sawNotFound=false;rescanRequested=false;}
 // Single-radio policy: do not start/restart saved-network association while
 // AP clients are attached. Cancel an in-flight background attempt on AP join.
 void pauseRetry(uint32_t now){
  if(state==NetState::Connecting&&!pending){state=NetState::Setup;message=msg::SETUP;retryAt=now;retryRequested=false;rescanRequested=false;pauseRequested=true;}
 }
 void fail(uint32_t now,const char* why){state=NetState::Setup;message=why;pending=false;retryAt=now;failedOnce=true;rescanRequested=false;}
 void tick(uint32_t now,bool connected,WifiFail failure=WifiFail::None,bool apClients=false){
  if(apClients&&!connected)pauseRetry(now);
  if(state==NetState::Connecting){
   if(connected){state=NetState::Online;message=msg::ONLINE;saveRequested=pending; saved=saved||pending;pending=false;failedOnce=false;rescanRequested=false;}
   // Wrong password shows as AUTH_FAIL / handshake timeout. One can be a
   // fluke on a weak link, so retry once before reporting it.
   else if(failure==WifiFail::Auth&&++authFails>=2)fail(now,msg::WRONG_PASS);
   else if(elapsed(now,since)>=ATTEMPT_MS)fail(now,sawNotFound?msg::NOT_FOUND:msg::FAILED);
   // A scan can miss the router; scan again until the attempt times out.
   else if(failure!=WifiFail::None){sawNotFound=sawNotFound||failure==WifiFail::NotFound;rescanRequested=true;}
  }else if(state==NetState::Online&&!connected){state=NetState::Setup;message=msg::LOST;retryAt=now;failedOnce=true;}
  // A saved network that associated after its attempt ended: adopt it rather
  // than WiFi.disconnect() a working link every 30 s (owner: page "load hoài").
  else if(state==NetState::Setup&&saved&&connected){state=NetState::Online;message=msg::ONLINE;failedOnce=false;}
  else if(state==NetState::Setup&&saved&&!apClients&&elapsed(now,retryAt)>=RETRY_MS){retryRequested=true;connect(false,now);}
 }
 void erase(uint32_t now){*this=Network{};retryAt=now;message=msg::ERASED;}
 // Screen: QR join guide whenever the crab is not online and no phone is on
 // its own Wi-Fi, except while the first attempt after boot/a new join runs.
 bool wantsQr(bool apClients)const{return state!=NetState::Online&&!apClients&&(state==NetState::Setup||failedOnce);}
};
struct HoldButton {
 bool down=false,fired=false;uint32_t since=0;
 bool tick(bool pressed,uint32_t now){
  if(!pressed){down=false;fired=false;return false;}
  if(!down){down=true;since=now;}
  if(!fired&&elapsed(now,since)>=cfg::BOOT_HOLD_MS){fired=true;return true;}return false;
 }
};
// All methods called under the firmware's mutex; network task may hard-off under the same mutex; only output task pulses.
enum class Actuator {Unknown,Positional};
// PCA9685 nominal 50 Hz quantisation. Actual oscillator tolerance is unmeasured.
inline int pwmCounts(int us){return (us*4096L+10000)/20000;}
inline float nominalUs(int counts){return counts*(20000.0f/4096);}
struct ServoTest {
 bool opened=false,active=false;
 int channel=0,neutral=307,counts=307,emittedCounts=0,emittedChannel=0;
 uint32_t since=0,last=0,generation=0;
 void stop(){active=false;}
 void tick(uint32_t now){if(active&&(elapsed(now,since)>=2000||elapsed(now,last)>=cfg::DEADMAN_MS))stop();}
 bool config(int ch,int centre){if(ch<0||ch>7||centre<287||centre>327)return false;stop();channel=ch;neutral=centre;counts=centre;return true;}
 bool hold(int step,uint32_t now,bool fresh){
  tick(now);
  if(!opened||(step!=-20&&step!=-4&&step!=-1&&step!=0&&step!=1&&step!=4&&step!=20))return false;
  if(fresh){if(active)return false;since=now;generation++;}
  else if(!active||counts!=neutral+step)return false;
  counts=neutral+step;last=now;active=true;return true;
 }
};
} // namespace crab
#include "drive360.h"
namespace crab {
struct Motion {
 Actuator actuator=Actuator::Unknown;
 ServoTest test;
 Continuous360 continuous;
 Drive360 drive;
 bool positional()const{return actuator==Actuator::Positional&&!test.opened&&!continuous.opened;}
 bool sequence(uint32_t id,uint32_t seq){if(!id||id!=session||seq<=lastSeq)return false;lastSeq=seq;return true;}
 bool selectActuator(bool positionalMode,uint32_t now){
  if(positionalMode&&(test.opened||continuous.opened))return false;
  const bool keepAssembly=assembly; // disarming must not silently exit the setup page
  stop();test=ServoTest{};continuous=Continuous360{};assembly=keepAssembly;raw=false;actuator=positionalMode?Actuator::Positional:Actuator::Unknown;
  amplitude=phase=0;for(auto& p:position)p=0;begin(now);return true;
 }
 bool openTest(bool active){
  if(active&&(actuator!=Actuator::Unknown||assembly||inhibit||continuous.opened))return false;
  stop();test.opened=active;return true;
 }
 bool openContinuous(bool active){
  if(active&&(actuator!=Actuator::Unknown||assembly||inhibit||test.opened))return false;
  stop();continuous.opened=active;return true;
 }
 bool continuousCommand(uint32_t id,uint32_t seq,int ch,int action,uint32_t ms,uint32_t now,bool fresh){
  if(!sequence(id,seq)||inhibit||assembly||actuator!=Actuator::Unknown||test.opened)return false;
  return continuous.hold(ch,action,ms,now,fresh);
 }
 bool testCommand(uint32_t id,uint32_t seq,int step,uint32_t now,bool fresh){
  if(!sequence(id,seq)||inhibit||assembly||actuator!=Actuator::Unknown)return false;
  continuous.stop();return test.hold(step,now,fresh);
 }
 float offsets[8]={},position[8]={};
 Vec velocity{};
 float yaw=0; // body turn share for arcs, see bodyYaw
 int dir=0;   // last accepted drive command, for the eyes
 float amplitude=0,phase=0,speed=cfg::SPEED_DEFAULT,flickHip=cfg::FLICK_HIP;
 int balance=0; // percent, see applyBalance
 float kneeLift=cfg::KNEE_LIFT;
 Pattern gaitPattern=Pattern::Trot;
 bool assembly=false,raw=false,inhibit=false,lease=false;
 bool autoMode=false; // Auto mode drives via autoDrive; cleared by any stop or manual command
 uint32_t session=0,lastSeq=0,lastCommand=0,start=0,lastTick=0;
 int enabled=0;
 uint32_t outputEpoch=0; // invalidate cached output after synchronous off/settings
 void begin(uint32_t now){start=lastTick=now;enabled=0;}
 // Boot-time arm (cfg::AUTO_ARM): same path as the page's Bật servo button.
 bool bootArm(bool driver,uint32_t now){return cfg::AUTO_ARM&&driver&&selectActuator(true,now);}
 bool setKneeLift(int deg){if(deg<cfg::KNEE_LIFT_MIN||deg>cfg::KNEE_LIFT_MAX)return false;kneeLift=float(deg);return true;}
 bool setBalance(int percent){if(percent<-cfg::BALANCE_LIMIT||percent>cfg::BALANCE_LIMIT)return false;balance=percent;return true;}
 // Emotion poses: direct joint targets in the gait's command frame (knee
 // negative lifts). Same lease/deadman as walking; release relaxes slowly.
 float pose[8]={},poseRate[8]={};
 bool posing=false,relaxing=false;
 void stop(){if(posing)relaxing=true;posing=false;autoMode=false;velocity={};yaw=0;dir=0;lease=false;test.stop();continuous.stop();drive.stop();}
 bool poseCommand(uint32_t id,uint32_t seq,const float angles[8],uint32_t ms,uint32_t now,bool fresh){
  if(!sequence(id,seq)||inhibit||assembly||test.opened||continuous.opened||!positional()||enabled<8)return false;
  if(!fresh&&(!lease||elapsed(now,lastCommand)>=cfg::DEADMAN_MS)){stop();return false;}
  for(int ch=0;ch<8;ch++)if(!std::isfinite(angles[ch]))return false;
  const float seconds=std::min(ms,uint32_t(5000))*.001f;
  for(int ch=0;ch<8;ch++){
   pose[ch]=clamp(angles[ch],-cfg::JOINT_LIMIT,cfg::JOINT_LIMIT);
   const float distance=std::fabs(pose[ch]-position[ch]);
   poseRate[ch]=seconds>0?clamp(distance/seconds,1,cfg::SLEW_DPS):cfg::SLEW_DPS;
  }
  velocity={};amplitude=0;posing=true;relaxing=false;autoMode=false;lastCommand=now;lease=true;return true;
 }
 bool command(uint32_t id,uint32_t seq,int dir,uint32_t now,bool fresh=true){
  if(dir<0||dir>8||!sequence(id,seq))return false;
  if(dir==0){stop();return true;}
  if(inhibit||assembly||test.opened||continuous.opened)return false;
  if(actuator==Actuator::Unknown)return false; //180-only release: no timed360 fallback
  if(!positional()||enabled<8)return false;
  if(!fresh&&(!lease||elapsed(now,lastCommand)>=cfg::DEADMAN_MS)){stop();return false;}
  velocity=bodyDirection(dir);yaw=bodyYaw(dir);this->dir=dir;posing=false;relaxing=false;autoMode=false;lastCommand=now;lease=true;return true;
 }
 // Auto mode: same readiness as a manual drive command, but no page session.
 bool startAuto(uint32_t now){
  if(inhibit||assembly||test.opened||continuous.opened||!positional()||enabled<8)return false;
  stop();autoMode=true;lastCommand=now;lease=true;return true;
 }
 // Called by the autopilot every frame; each call refreshes the deadman, so a
 // stalled loop still stops the crab (and ends Auto) after DEADMAN_MS.
 bool autoDrive(int dir,uint32_t now){
  if(!autoMode||dir<0||dir>8)return false;
  if(inhibit||assembly||!positional()||enabled<8){stop();return false;}
  velocity=bodyDirection(dir);yaw=bodyYaw(dir);this->dir=dir;posing=false;relaxing=false;lastCommand=now;lease=true;return true;
 }
 void newSession(uint32_t id){stop();test.opened=false;continuous.opened=false;session=id;lastSeq=0;}
 bool setAssembly(bool active){if(active&&(test.opened||continuous.opened))return false;stop();assembly=active;raw=false;return true;}
 bool centre(){if(!positional())return false;stop();assembly=true;raw=true;return true;}
 bool trim(int ch,int delta){if(!positional()||!assembly||ch<0||ch>7||(std::abs(delta)!=cfg::TRIM_FINE&&std::abs(delta)!=cfg::TRIM_COARSE))return false;raw=false;offsets[ch]=clamp(offsets[ch]+delta,-cfg::TRIM_LIMIT,cfg::TRIM_LIMIT);return true;}
 // Shared20-ms pose frames after startup;300-ms gaps on initial enable.
 // tick returns the startup channel, or0 to indicate a complete pose frame.
 // angle+offset slew is enforced in the driver, so trim also moves smoothly.
 int tick(uint32_t now){
  test.tick(now);continuous.tick(now);drive.tick(now);
  if(inhibit){test.stop();continuous.stop();drive.stop();}
  if(!positional()||inhibit){velocity={};lease=false;autoMode=false;return -1;}
  if(assembly||elapsed(now,lastCommand)>=cfg::DEADMAN_MS)stop();
  if(elapsed(now,lastTick)<cfg::FRAME_MS)return -1;
  const float dt=std::min(elapsed(now,lastTick)*.001f,.05f);lastTick=now;
  if(enabled<8){if(elapsed(now,start)<uint32_t(enabled)*cfg::ENABLE_GAP_MS)return -1;return enabled++;}
  bool moving=std::fabs(velocity.x)+std::fabs(velocity.y)+std::fabs(yaw)>.01f;
  // Flick holds the hips at up to 90 deg; trot keeps them near neutral. Do not
  // jump between the two stances mid-stride: ramp down first, then switch.
  if(moving&&amplitude>.02f&&flickActive(gaitPattern,velocity,yaw)!=flickActive(gaitPattern,heading,headingYaw))moving=false;
  // Keep last heading through amplitude decay to avoid snapping the hip target.
  amplitude=clamp(amplitude+(moving?dt*1.5f:-dt*4.0f),0,1);
  if(moving){heading=velocity;headingYaw=yaw;}
  if(moving)phase=std::fmod(phase+dt*6.2831853072f*speed/cyclePeriod(gaitPattern,heading,headingYaw),6.2831853072f);
  if(posing){for(int ch=0;ch<8;ch++)position[ch]+=clamp(pose[ch]-position[ch],-poseRate[ch]*dt,poseRate[ch]*dt);return 0;}
  float target[8]={};if(!assembly){gait(phase,heading,amplitude,target,gaitPattern,flickHip,kneeLift,headingYaw);applyBalance(target,balance);}
  const float rate=relaxing&&!moving?cfg::RELAX_DPS:cfg::SLEW_DPS;bool settled=true;
  for(int ch=0;ch<8;ch++){position[ch]+=clamp(target[ch]-position[ch],-rate*dt,rate*dt);settled=settled&&std::fabs(target[ch]-position[ch])<.01f;}
  if(settled||moving)relaxing=false;
  return 0;
 }
 private:Vec heading{};float headingYaw=0;
};
}

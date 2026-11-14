#pragma once
#include <stdint.h>
#include "config.h"
#include "eyes.h"
// Auto mode (owner, 2026-11-14): "it is a remote-control toy, make it a robot".
// Two front ultrasonic sensors (left, right) and a small state machine, no ML:
// cruise forward, veer away from a near side, and on an obstacle stop with a
// surprised face, back off turning the nose to the freer side, arc away, and
// carry on. Now and then it wanders or stops to look around. It never starts
// by itself: boot and every reset come up in Manual, and any manual command,
// STOP, a lost sensor or a stuck crab returns to Manual.
namespace crab {
namespace automsg {
constexpr const char* ON="Đang tự đi";
constexpr const char* MANUAL="Đã về lái tay";
constexpr const char* LOST="Mất cảm biến siêu âm";
constexpr const char* STUCK="Kẹt rồi, nhờ giúp";
constexpr const char* NO_SENSOR="Chưa thấy cảm biến siêu âm";
}
// Reported for an echo longer than the measured range (nothing in front).
constexpr uint16_t SONAR_FAR_CM=400;
// HC-SR04: round trip at ~343 m/s is 58 us per cm of distance.
inline uint16_t sonarCm(uint32_t us){const uint32_t cm=us/58;return uint16_t(cm>SONAR_FAR_CM?SONAR_FAR_CM:cm);}
// One sensor: median of the last three readings, so one missed or stray echo
// (soft surfaces, the other sensor's ping, the body bouncing) cannot steer.
struct SonarSide {
 uint16_t raw[3]={0,0,0};uint8_t count=0,next=0;uint32_t seenAt=0;
 void add(uint16_t cm,uint32_t now){raw[next]=cm;next=uint8_t((next+1)%3);if(count<3)count++;seenAt=now;}
 bool fresh(uint32_t now)const{return count>0&&now-seenAt<cfg::SONAR_STALE_MS;}
 uint16_t cm()const{
  if(count==0)return 0;if(count==1)return raw[(next+2)%3];
  if(count==2){const uint16_t a=raw[(next+1)%3],b=raw[(next+2)%3];return a<b?a:b;} // two: the nearer, to be safe
  const uint16_t a=raw[0],b=raw[1],c=raw[2];
  return a>b?(b>c?b:(a>c?c:a)):(a>c?a:(b>c?c:b));
 }
 // Result of one ping: a falling edge gives the width; a rise without a fall
 // within the ping period is out of range; no rise at all means no sensor
 // answered, so nothing is added and the side goes stale.
 void ping(bool rose,bool fell,uint32_t widthUs,uint32_t now){
  if(!rose)return;
  if(!fell){add(SONAR_FAR_CM,now);return;}
  if(widthUs<cfg::SONAR_MIN_US)return; // below the 2 cm blind zone: noise
  add(sonarCm(widthUs),now);
 }
};
struct Sonar {
 SonarSide side[2]; // 0 left, 1 right (robot's own sides)
 bool ok(uint32_t now)const{return side[0].fresh(now)&&side[1].fresh(now);}
};
enum class AutoState:uint8_t {Off,Cruise,Halt,Backoff,Turn,Look};
inline const char* autoStateName(AutoState s){
 switch(s){case AutoState::Cruise:return "cruise";case AutoState::Halt:return "halt";case AutoState::Backoff:return "backoff";
  case AutoState::Turn:return "turn";case AutoState::Look:return "look";default:return "off";}
}
struct Autopilot {
 AutoState state=AutoState::Off;
 uint32_t since=0,turnMs=0,nextWander=0,noteAt=0,seed=0x9e3779b9u;
 int side=1;          // +1 turn left (left is freer), -1 turn right
 uint8_t avoids=0;    // obstacles in a row without a long clear cruise
 const char* note=nullptr; // why it last stopped, shown for a few seconds
 bool active()const{return state!=AutoState::Off;}
 uint32_t rnd(uint32_t lo,uint32_t hi){seed=seed*1664525u+1013904223u;return lo+(seed>>8)%(hi-lo+1);}
 static bool due(uint32_t now,uint32_t at){return int32_t(now-at)>=0;}
 void enter(AutoState s,uint32_t now){state=s;since=now;}
 void start(uint32_t now){avoids=0;note=nullptr;nextWander=now+rnd(cfg::AUTO_WANDER_MIN_MS,cfg::AUTO_WANDER_MAX_MS);enter(AutoState::Cruise,now);}
 void stop(uint32_t now,const char* why){state=AutoState::Off;since=now;note=why;noteAt=now;}
 // Message for the screen and page: running, or why it stopped (for 5 s).
 const char* message(uint32_t now)const{return active()?automsg::ON:note&&now-noteAt<5000?note:nullptr;}
 void halt(uint32_t now,int left,int right){
  if(++avoids>=cfg::AUTO_STUCK_AVOIDS){stop(now,automsg::STUCK);return;}
  side=left>=right?1:-1;enter(AutoState::Halt,now);
 }
 // Drive command for this instant: 0 stand, 1 forward, 5/6 forward arc
 // left/right, 7/8 back arcs (car convention, see crab::bodyYaw).
 int tick(uint32_t now,const Sonar& s){
  if(!active())return 0;
  if(!s.ok(now)){stop(now,automsg::LOST);return 0;}
  const int left=s.side[0].cm(),right=s.side[1].cm(),nearest=left<right?left:right;
  const uint32_t t=now-since;
  switch(state){
   case AutoState::Cruise:
    if(nearest<cfg::AUTO_STOP_CM){halt(now,left,right);return 0;}
    if(t>=cfg::AUTO_CLEAR_MS)avoids=0;
    if(due(now,nextWander)){
     nextWander=now+rnd(cfg::AUTO_WANDER_MIN_MS,cfg::AUTO_WANDER_MAX_MS);
     if(rnd(0,2)==0){enter(AutoState::Look,now);turnMs=rnd(1500,3000);return 0;}
     side=rnd(0,1)?1:-1;turnMs=rnd(800,1800);enter(AutoState::Turn,now);return side>0?5:6;
    }
    if(left<cfg::AUTO_SLOW_CM&&left<=right)return 6; // something near on the left: veer right
    if(right<cfg::AUTO_SLOW_CM)return 5;
    return 1;
   case AutoState::Halt:
    if(t>=cfg::AUTO_HALT_MS)enter(AutoState::Backoff,now);
    return 0;
   case AutoState::Backoff:
    // Reversing with the tail swung right (8) turns the nose left, and vice versa.
    if(t>=cfg::AUTO_BACK_MS){turnMs=cfg::AUTO_TURN_MS;enter(AutoState::Turn,now);return side>0?5:6;}
    return side>0?8:7;
   case AutoState::Turn:
    if(nearest<cfg::AUTO_STOP_CM){halt(now,left,right);return 0;}
    if(t>=turnMs){enter(AutoState::Cruise,now);return 1;}
    return side>0?5:6;
   case AutoState::Look:
    if(nearest<cfg::AUTO_STOP_CM){halt(now,left,right);return 0;}
    if(t>=turnMs)enter(AutoState::Cruise,now);
    return 0;
   default:return 0;
  }
 }
 // Face: surprised at an obstacle, sad when it gave up or lost a sensor.
 Mood mood(uint32_t now)const{
  if(state==AutoState::Halt)return Mood::Surprised;
  if(!active()&&note&&note!=automsg::MANUAL&&now-noteAt<4000)return Mood::Sad;
  return Mood::Normal;
 }
};
}

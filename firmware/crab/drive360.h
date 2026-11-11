#pragma once
#include <stdint.h>
namespace crab {
// Owner: ONLY hips CH0/2/6/4. Forward = CCW/CW/CCW/CW;
// backward reverses that pattern. No knee commands, centring, lift or gait.
// ASSUMPTIONS: looking into each output shaft,205=CCW,409=CW.
// Nominal30deg =60ms using seller no-load0.12s/60deg, NOT measured.
// Equal reverse ON-time is a timing estimate, not angle feedback/holding.
struct Drive360 {
 bool active=false,returning=false,running=false,pendingStop=false,unfinished=false;
 int dir=0,sign=0,balanceMs=0;
 int counts[4]={}; // CH0,2,4,6, NEVER odd knee channels
 uint32_t last=0,accountedAt=0,phaseAt=0,generation=0;
 static constexpr uint32_t PULSE_MS=60,DEADMAN_MS=500;
 void clear(){for(auto& c:counts)c=0;}
 void stop(){pendingStop=pendingStop||running;active=false;clear();}
 bool command(int value,uint32_t now,bool fresh){
  if(value<1||value>2)return false;
  if(fresh){
   if(active||pendingStop)return false;
   dir=value;returning=unfinished&&balanceMs!=0;unfinished=true;
   sign=returning?(balanceMs>0?-1:1):(value==1?1:-1);
   active=true;running=false;last=accountedAt=now;generation++;return true;
  }
  if(!active||dir!=value||now-last>=DEADMAN_MS)return false;
  last=now;return true;
 }
 void account(uint32_t now){
  if(running)balanceMs+=sign*int(now-accountedAt);
  accountedAt=now;
 }
 void tick(uint32_t now){
  if(pendingStop){account(now);pendingStop=false;running=false;}
  if(!active)return;
  if(!running)phaseAt=now;
  account(now);
  if(now-last>=DEADMAN_MS){active=running=false;clear();return;}
  if(returning){
   // Preserve any small scheduler overshoot as signed time debt. Never lie
   // about measured zero or start another outward stroke on this press.
   if(sign*balanceMs>=0||now-phaseAt>=PULSE_MS){unfinished=sign*balanceMs<0;active=running=false;clear();return;}
  }else if((balanceMs<0?-balanceMs:balanceMs)>=int(PULSE_MS)){
   returning=true;sign=-sign;phaseAt=now;generation++;
  }
  const int forward[4]={-1,1,1,-1}; // FL,FR,RL,RR
  for(int hip=0;hip<4;hip++)counts[hip]=sign*forward[hip]>0?409:205;
  running=true;
 }
};
}

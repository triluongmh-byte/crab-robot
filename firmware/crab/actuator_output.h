#pragma once
#include "drivers.h"
//180-degree positional output only. Legacy360 helpers remain source history;
// no test/timed-rotation state can make this release emit a servo pulse.
class ActuatorOutput {
 int mode=-1;float sent[8]={};uint32_t epoch=0;
 public:
 bool service(crab::Motion& motion,ServoDriver& driver,uint32_t now){
  if(epoch!=motion.outputEpoch){mode=-1;epoch=motion.outputEpoch;}
  bool first=motion.enabled<8;int ch=motion.tick(now);
  const int wanted=(!motion.inhibit&&motion.positional())?1:0;
  if(wanted!=mode){if(!driver.disableOutputs())return fault(motion,driver);mode=wanted;}
  if(!wanted)return true;
  if(ch>=0){
   // All joints use the same sampled pose; only startup enables one channel.
   for(int channel=first?ch:0;channel<(first?ch+1:8);channel++){
    int target=crab::pulse(channel,motion.position[channel],motion.offsets[channel],motion.raw);
    const float delta=cfg::SLEW_DPS*cfg::FRAME_S*cfg::US_PER_DEG;
    if(first)sent[channel]=target;else sent[channel]+=crab::clamp(target-sent[channel],-delta,delta);
    if(!driver.pulse(channel,int(std::lround(sent[channel]))))return fault(motion,driver);
   }
  }
  return true;
 }
 private:
 bool fault(crab::Motion& motion,ServoDriver& driver){driver.allOff();motion.stop();motion.inhibit=true;mode=-1;return false;}
};

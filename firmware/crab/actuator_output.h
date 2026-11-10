#pragma once
#include "drivers.h"
// Called only under the Motion mutex. Final policy and actual PCA writes are
// host-tested together; HTTP tasks never write PWM or race this output boundary.
class ActuatorOutput {
 int mode=-1,lastChannel=-1,lastCounts=-1;
 float sent[8]={};
 uint32_t generation=0;
 public:
 bool service(crab::Motion& motion,ServoDriver& driver,uint32_t now){
  bool first=motion.enabled<8;
  int ch=motion.tick(now);
  const int wanted=motion.inhibit?0:(motion.positional()?1:(motion.test.opened&&motion.test.active?2:0));
  if(wanted!=mode||(wanted==2&&(lastChannel!=motion.test.channel||generation!=motion.test.generation))){
   if(!driver.disableOutputs())return fault(motion,driver);
   mode=wanted;lastChannel=lastCounts=-1;generation=motion.test.generation;
  }
  if(wanted==0)return true;
  if(wanted==2){
   const int channel=motion.test.channel,counts=motion.test.counts;
   if(channel!=lastChannel||counts!=lastCounts){
    if(!driver.pulseCounts(channel,counts))return fault(motion,driver);
    lastChannel=channel;lastCounts=counts;
    motion.test.emittedChannel=channel;motion.test.emittedCounts=counts;
   }
  }else if(ch>=0){
   int target=crab::pulse(ch,motion.position[ch],motion.offsets[ch],motion.raw);
   float limit=cfg::SLEW_DPS*.08f*cfg::US_PER_DEG;
   if(first)sent[ch]=target;else sent[ch]+=crab::clamp(target-sent[ch],-limit,limit);
   if(!driver.pulse(ch,int(std::lround(sent[ch]))))return fault(motion,driver);
  }
  return true;
 }
 private:
 bool fault(crab::Motion& motion,ServoDriver& driver){driver.allOff();motion.stop();motion.inhibit=true;mode=-1;return false;}
};

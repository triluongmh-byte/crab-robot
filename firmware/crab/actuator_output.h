#pragma once
#include "drivers.h"
// Called only under the Motion mutex. Final policy and actual PCA writes are
// host-tested together; HTTP may hard-off under the same mutex, never pulse.
class ActuatorOutput {
 int mode=-1,lastChannel=-1,lastCounts=-1;
 float sent[8]={};
 uint32_t generation=0,epoch=0;
 public:
 bool service(crab::Motion& motion,ServoDriver& driver,uint32_t now){
  if(epoch!=motion.outputEpoch){mode=-1;epoch=motion.outputEpoch;}
  bool first=motion.enabled<8;
  if(motion.continuous.active&&!motion.continuous.validOutput())return fault(motion,driver);
  int ch=motion.tick(now);
  if(motion.continuous.active&&!motion.continuous.validOutput()){motion.stop();return fault(motion,driver);}
  if(motion.drive.active){
   if(mode!=4||generation!=motion.drive.generation){
    if(!driver.disableOutputs())return fault(motion,driver);
    mode=4;generation=motion.drive.generation;lastChannel=lastCounts=-1;
    for(int hip=0;hip<4;hip++){
     const int counts=motion.drive.counts[hip];
     if(counts!=205&&counts!=409)return fault(motion,driver);
     if(!driver.pulseCounts(hip*2,counts))return fault(motion,driver);
    }
   }
   return true;
  }
  const int wanted=motion.inhibit?0:(motion.continuous.opened&&motion.continuous.active?3:(motion.positional()?1:(motion.test.opened&&motion.test.active?2:0)));
  if(wanted==3){
   if(mode!=3||lastChannel!=motion.continuous.channel||generation!=motion.continuous.generation){
    if(!driver.disableOutputs())return fault(motion,driver);
    mode=3;lastChannel=lastCounts=-1;generation=motion.continuous.generation;
   }
   if(lastChannel!=motion.continuous.channel||lastCounts!=motion.continuous.counts){
    if(!driver.pulseCounts(motion.continuous.channel,motion.continuous.counts))return fault(motion,driver);
    lastChannel=motion.continuous.channel;lastCounts=motion.continuous.counts;
    motion.continuous.emittedChannel=lastChannel;motion.continuous.emittedCounts=lastCounts;
   }
   return true;
  }
  if(wanted!=mode||(wanted==2&&(lastChannel!=motion.test.channel||generation!=motion.test.generation))){
   if(!driver.disableOutputs())return fault(motion,driver);
   mode=wanted;lastChannel=lastCounts=-1;generation=motion.test.generation;
  }
  if(wanted==0)return true;
  if(wanted==2){
   if(motion.test.channel<0||motion.test.channel>7||motion.test.counts<267||motion.test.counts>347)return fault(motion,driver);
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

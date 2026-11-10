#include "../crab/actuator_output.h"
#include <cassert>
#include <iostream>
FakeWire Wire;rmt_config_t rmtCapture;std::vector<rmt_item32_t> rmtBits;
struct GpioCall{int pin,value;bool mode;size_t writes;};
std::vector<GpioCall> gpioCalls;
void digitalWrite(int pin,int value){assert(pin>=0);gpioCalls.push_back({pin,value,false,Wire.writes.size()});}
void pinMode(int pin,int mode){assert(pin>=0);gpioCalls.push_back({pin,mode,true,Wire.writes.size()});}
// Replay actual register writes to count enabled outputs after every service.
static int activeOutputs(){
 bool active[16]={};
 for(const auto& w:Wire.writes){
  if(w.size()==2&&w[0]>=9&&w[0]<=69&&(w[0]-9)%4==0&&(w[1]&16))active[(w[0]-9)/4]=false;
  if(w.size()==5&&w[0]>=6&&w[0]<=66&&(w[0]-6)%4==0)active[(w[0]-6)/4]=!(w[4]&16);
 }
 int n=0;for(bool a:active)n+=a;return n;
}
static void test_output(){
 Wire.writes.clear();ServoDriver d;assert(d.begin());ActuatorOutput outputs;crab::Motion m;m.begin(0);m.newSession(1);
 for(int t=0;t<4000;t+=10){assert(outputs.service(m,d,t));assert(activeOutputs()==0);}
 assert(m.enabled==0);assert(m.openTest(true));uint32_t seq=0;
 for(int ch=0;ch<8;ch++)for(int centre:{287,307,327})for(int step:{-20,-4,-1,0,1,4,20}){
  m.stop();assert(outputs.service(m,d,4000));assert(activeOutputs()==0);
  assert(m.test.config(ch,centre));assert(m.testCommand(1,++seq,step,4000,true));
  assert(outputs.service(m,d,4000));assert(activeOutputs()==1);assert(m.test.emittedChannel==ch&&m.test.emittedCounts==centre+step);
  const auto w=Wire.writes.back();assert(w[0]==6+ch*4);int on=w[1]+(w[2]<<8),off=w[3]+(w[4]<<8);assert(((off-on)&4095)==centre+step);
  for(int t=4150;t<6000;t+=150){assert(m.testCommand(1,++seq,step,t,false));assert(outputs.service(m,d,t));assert(activeOutputs()==1);}
  assert(outputs.service(m,d,6000));assert(activeOutputs()==0&&!m.test.active);
  assert(!m.testCommand(1,++seq,step,6001,false));
 }
 assert(m.test.config(0,307));assert(m.testCommand(1,++seq,0,7000,true));assert(outputs.service(m,d,7000));assert(activeOutputs()==1);
 assert(outputs.service(m,d,7500));assert(activeOutputs()==0); // independent deadman
 assert(m.testCommand(1,++seq,0,8000,true));assert(outputs.service(m,d,8000));
 m.inhibit=true;assert(outputs.service(m,d,8010));assert(activeOutputs()==0);m.inhibit=false;
 assert(m.testCommand(1,++seq,0,8100,true));assert(outputs.service(m,d,8100));m.newSession(2);assert(outputs.service(m,d,8110));assert(activeOutputs()==0);
 assert(m.selectActuator(true,9000));for(int ch=0;ch<8;ch++){assert(outputs.service(m,d,9010+ch*300));assert(activeOutputs()==ch+1);} // preserved explicit positional startup
 assert(m.selectActuator(false,12000));assert(outputs.service(m,d,12000));assert(activeOutputs()==0);
 assert(m.openTest(true));assert(m.testCommand(2,1,0,12100,true));Wire.fail=true;assert(!outputs.service(m,d,12100));assert(m.inhibit&&!m.test.active);Wire.fail=false;
 ServoDriver absent;Wire.fail=true;assert(!absent.begin());Wire.fail=false; // finite init failure, no wait loop
}
int main(){
 ServoDriver p;
 assert(!p.pulse(0,1500));assert(Wire.writes.empty());
 assert(p.begin());assert(Wire.sda==18&&Wire.scl==17&&Wire.hz==100000);assert(Wire.writes.size()==20);
 if(cfg::INTEGRATED_BOARD){
  assert(cfg::PCA_OE_PIN==21&&cfg::POWER_PIN==-1);
  assert(gpioCalls.size()==2&&gpioCalls[0].pin==21&&gpioCalls[0].value==HIGH&&!gpioCalls[0].mode&&gpioCalls[0].writes==0);
  assert(gpioCalls[1].mode&&gpioCalls[1].value==OUTPUT&&gpioCalls[1].writes==0);
 }else assert(cfg::PCA_OE_PIN==-1&&cfg::POWER_PIN==15&&gpioCalls.empty());
 for(int i=0;i<16;i++){assert(Wire.writes[i].size()==2);assert(Wire.writes[i][0]==0x09+i*4);assert(Wire.writes[i][1]==0x10);}
 assert(Wire.writes[16]==std::vector<uint8_t>({0,0x30}));assert(Wire.writes[17]==std::vector<uint8_t>({0xfe,121}));assert(Wire.writes[19]==std::vector<uint8_t>({0,0x20}));
 for(int ch=0;ch<8;ch++){
  assert(p.pulse(ch,1500));auto w=Wire.writes.back();assert(w.size()==5&&w[0]==0x06+4*ch);int on=w[1]+(w[2]<<8),off=w[3]+(w[4]<<8);assert(on==ch*512);assert(((off-on)&4095)==307);assert((w[4]&0x10)==0);
  if(cfg::INTEGRATED_BOARD){assert(gpioCalls.back().value==LOW&&!gpioCalls.back().mode);assert(gpioCalls.back().writes==21+size_t(ch));}
 }
 auto count=Wire.writes.size();assert(!p.pulse(8,1500)&&Wire.writes.size()==count);
 auto gpioCount=gpioCalls.size();Wire.fail=true;assert(!p.pulse(0,1500));
 if(cfg::INTEGRATED_BOARD){assert(gpioCalls.size()==gpioCount+2);assert(gpioCalls[gpioCount].value==HIGH&&gpioCalls[gpioCount].writes==count+1);}
 count=Wire.writes.size();assert(!p.pulse(0,1500)&&Wire.writes.size()==count); // fault latched
 assert(!p.begin());Wire.fail=false;assert(!p.pulse(0,1500)); // init failure remains inhibited
 assert(p.begin());assert(p.pulse(0,1500));p.allOff();assert(!p.pulse(0,1500));
 test_output();
 LightDriver light;assert(light.begin());assert(rmtCapture.gpio_num==1&&rmtCapture.clk_div==8&&rmtCapture.tx_config.idle_output_en);assert(rmtBits.size()==192);
 for(auto bit:rmtBits)assert(bit.duration0==4&&bit.duration1==9); // off at boot
 light.set(true);for(int color=0;color<24;color++){int value=0;for(int b=0;b<8;b++){const auto bit=rmtBits[color*8+b];assert(bit.level0==1&&bit.level1==0);assert(bit.duration0+bit.duration1==13);value=(value<<1)|(bit.duration0==8);}assert(value==16);}
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": PCA default all16 off, one-output test across8 channels/3 neutrals/7 steps, emitted counts267-347, 2s cap, deadman/inhibit/session/fault, preserved explicit positional startup,50Hz; OE inhibited before I2C and released only after first valid pulse; RMT LED off/cap/timing\n";
}

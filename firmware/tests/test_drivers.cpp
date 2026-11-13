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
static void test_positional180(){
 Wire.writes.clear();ServoDriver d;assert(d.begin());ActuatorOutput out;crab::Motion m;m.begin(0);m.newSession(70);uint32_t seq=0;
 for(uint32_t t=0;t<4000;t+=10){assert(out.service(m,d,t));assert(activeOutputs()==0);}
 assert(!m.command(70,++seq,1,4000));assert(!m.drive.active);
 // Even stale legacy helper states cannot cross the positional output boundary.
 m.test.opened=m.test.active=true;m.test.last=m.test.since=4000;assert(out.service(m,d,4000)&&activeOutputs()==0);m.test={};
 m.drive.active=true;m.drive.last=4010;assert(out.service(m,d,4010)&&activeOutputs()==0);m.drive={};
 assert(m.setAssembly(true));assert(m.selectActuator(true,5000)&&m.assembly);assert(m.centre());
 for(int ch=0;ch<8;ch++){
  uint32_t t=5020+ch*300;assert(out.service(m,d,t));assert(activeOutputs()==ch+1);
  auto w=Wire.writes.back();assert(w.size()==5&&w[0]==6+ch*4);assert(((w[3]+256*w[4]-w[1]-256*w[2])&4095)==307);
  if(ch<7){assert(out.service(m,d,t+100));assert(activeOutputs()==ch+1);}
 }
 assert(!m.command(70,++seq,1,7200));assert(m.trim(0,1));assert(!m.raw);assert(m.setAssembly(false));
 uint32_t now=7300;
 for(int dir=1;dir<=8;dir++){
  assert(m.command(70,++seq,dir,now,true));
  for(uint32_t t=now;t<now+2500;t+=10){if(t>now&&(t-now)%150==0)assert(m.command(70,++seq,dir,t,false));assert(out.service(m,d,t));}
  assert(m.command(70,++seq,0,now+2500,false));
  for(uint32_t t=now+2500;t<now+4000;t+=10)assert(out.service(m,d,t));
  assert(m.velocity.x==0&&m.velocity.y==0&&m.amplitude==0);now+=4100;
 }
 // Independently decode every actual pulse, including trimmed channels.
 for(const auto& w:Wire.writes)if(w.size()==5){int ch=(w[0]-6)/4,on=w[1]+256*w[2],off=w[3]+256*w[4];assert(ch>=0&&ch<8);int count=(off-on)&4095;assert(count>=(ch%2?267:279)&&count<=(ch%2?347:336));}
 assert(m.command(70,++seq,1,now,true));assert(out.service(m,d,now));assert(out.service(m,d,now+510));assert(!m.lease);
 assert(!m.command(70,++seq,1,now+520,false));
 assert(m.selectActuator(false,now+600));assert(out.service(m,d,now+600)&&activeOutputs()==0);
 assert(!m.command(70,++seq,1,now+610));assert(!m.drive.active);
 assert(m.selectActuator(true,now+1000));assert(out.service(m,d,now+1020));Wire.fail=true;assert(!out.service(m,d,now+1310));assert(m.inhibit);Wire.fail=false;
}
static void test_pair_frames(){
 Wire.writes.clear();ServoDriver d;assert(d.begin());ActuatorOutput out;crab::Motion m;m.begin(0);m.newSession(81);assert(m.selectActuator(true,0));
 for(uint32_t t=0;t<=2200;t+=20)assert(out.service(m,d,t));assert(m.enabled==8);
 m.speed=1;uint32_t seq=0;int previous[8]={},checkedReturns=0,frames=0;
 for(uint32_t t=3000;t<14000;t+=10){
  if((t-3000)%150==0)assert(m.command(81,++seq,1,t,!m.lease));
  size_t before=Wire.writes.size();assert(out.service(m,d,t));size_t count=Wire.writes.size()-before;
  if(!count)continue;
  assert(count==8);int pulses[8];int grounded=0;
  for(int ch=0;ch<8;ch++){
   auto w=Wire.writes[before+ch];assert(w.size()==5&&w[0]==6+4*ch);
   pulses[ch]=((w[3]+256*w[4])-(w[1]+256*w[2]))&4095;
   if(ch%2&&std::abs(pulses[ch]-307)<=1)grounded++;
  }
  assert(std::abs(std::abs(pulses[1]-307)-std::abs(pulses[3]-307))<=1);
  assert(std::abs(std::abs(pulses[5]-307)-std::abs(pulses[7]-307))<=1);
  assert(grounded>=2); // zero trims, actual quantised output; not physical contact
  if(t>6000)for(int leg=0;leg<4;leg++){
   const float delta=(pulses[2*leg]-previous[2*leg])*crab::hipProjection(leg,crab::direction(1));
   if(delta>.5f){assert(std::abs(pulses[2*leg+1]-307)>=12);checkedReturns++;}
  }
  for(int ch=0;ch<8;ch++)previous[ch]=pulses[ch];frames++;
 }
 assert(checkedReturns>30&&frames>400);
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
 test_positional180();test_pair_frames();
 LightDriver light;assert(light.begin());assert(rmtCapture.gpio_num==1&&rmtCapture.clk_div==8&&rmtCapture.tx_config.idle_output_en);assert(rmtBits.size()==192);
 for(auto bit:rmtBits)assert(bit.duration0==4&&bit.duration1==9); // off at boot
 light.set(true);for(int color=0;color<24;color++){int value=0;for(int b=0;b<8;b++){const auto bit=rmtBits[color*8+b];assert(bit.level0==1&&bit.level1==0);assert(bit.duration0+bit.duration1==13);value=(value<<1)|(bit.duration0==8);}assert(value==16);}
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": 180-only actual PCA register replay/shared8CH20ms frames/fast pair lift clearance: boot off, sequential enable8CH,8directions, pulse bounds after trim, release/deadman settle, assembly/raw centre, explicit disarm, legacy-state refusal,50Hz; OE inhibited before I2C and released only after first valid pulse; RMT LED off/cap/timing\n";
}

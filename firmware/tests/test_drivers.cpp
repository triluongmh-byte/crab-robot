#include "../crab/drivers.h"
#include <cassert>
#include <iostream>
FakeWire Wire;rmt_config_t rmtCapture;std::vector<rmt_item32_t> rmtBits;
struct GpioCall{int pin,value;bool mode;size_t writes;};
std::vector<GpioCall> gpioCalls;
void digitalWrite(int pin,int value){assert(pin>=0);gpioCalls.push_back({pin,value,false,Wire.writes.size()});}
void pinMode(int pin,int mode){assert(pin>=0);gpioCalls.push_back({pin,mode,true,Wire.writes.size()});}
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
 LightDriver light;assert(light.begin());assert(rmtCapture.gpio_num==1&&rmtCapture.clk_div==8&&rmtCapture.tx_config.idle_output_en);assert(rmtBits.size()==192);
 for(auto bit:rmtBits)assert(bit.duration0==4&&bit.duration1==9); // off at boot
 light.set(true);for(int color=0;color<24;color++){int value=0;for(int b=0;b<8;b++){const auto bit=rmtBits[color*8+b];assert(bit.level0==1&&bit.level1==0);assert(bit.duration0+bit.duration1==13);value=(value<<1)|(bit.duration0==8);}assert(value==16);}
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": PCA all16 off, 50 Hz, staggered CH0-7, fault latch; OE inhibited before I2C and released only after first valid pulse; RMT LED off/cap/timing\n";
}

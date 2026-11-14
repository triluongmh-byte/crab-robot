#include <string>
#include "../crab/display.h"
#include <iostream>
#include <fstream>
struct Call{int pin,value;};static std::vector<Call> gpio;
void digitalWrite(int pin,int value){assert(pin>=0);gpio.push_back({pin,value});}
void pinMode(int pin,int mode){assert(pin>=0&&mode==OUTPUT);}
int main(int argc,char** argv){
 assert(argc==2);(void)argv;
 Screen s;assert(s.begin());assert(gapX==0&&gapY==35);
 assert(gpio.back().pin==38&&gpio.back().value==HIGH);
#if CRAB_INTEGRATED_BOARD
 assert(spiCalls==1&&i80Calls==0);
 assert(spiBus.sclk_io_num==8&&spiBus.mosi_io_num==39&&spiBus.miso_io_num==-1);
 assert(spiConfig.cs_gpio_num==6&&spiConfig.dc_gpio_num==7&&spiConfig.spi_mode==0&&spiConfig.pclk_hz==10000000);
 std::ofstream trace(std::string(argv[1])+"/panel-commands.txt");
 for(const auto& c:commands){trace<<c.cmd;for(auto b:c.bytes)trace<<" "<<int(b);trace<<"\n";}trace.close();
 assert(commands.size()==17&&commands.back().cmd==0x36&&commands.back().bytes==std::vector<uint8_t>({0xb0}));
 for(auto c:gpio)assert(c.pin==5||c.pin==38); // no unused i80 or GPIO15
 // Exhaustive address window: short axis 35..204, long axis 0..319.
 assert(waveshare::GAP_X+319==319&&waveshare::GAP_Y+169==204);
 assert((waveshare::MADCTL^0x70)==0xc0); // panel turned 180 degrees
#else
 assert(spiCalls==0&&i80Calls==1&&parallelConfig.wr_gpio_num==8);
 const int pins[]={39,40,41,42,45,46,47,48};for(int i=0;i<8;i++)assert(parallelConfig.data_gpio_nums[i]==pins[i]);
 assert(gpio[0].pin==15&&gpio[0].value==HIGH);
#endif
 assert(s.show("WIFI:T:WPA;S:CuaRobot-1234;P:cuarobot;;","Wi-Fi","192.168.4.1","CuaRobot-1234"));assert(draws==1);
#if CRAB_INTEGRATED_BOARD
 gpio.clear();failCommand=0xbb;Screen failure;assert(!failure.begin());
 for(auto c:gpio)assert(c.pin!=38||c.value==LOW); // failed init never lights BL
#endif
 // Pet face: open eyes are white at their centres on black, a blink narrows them,
 // a glance shifts them, happy draws arcs; the status line sits at the bottom.
 {Screen& f=s;crab::EyeFrame open;const int before=draws;
  assert(f.face(open,"Đã vào Wi-Fi 172.168.20.249")&&draws==before+1);
  assert(f.at(160-52,70)==0xffff&&f.at(160+52,70)==0xffff&&f.at(160,70)==0&&f.at(5,5)==0);
  assert(f.at(160-52,70-40)==0xffff&&f.at(160-52,70+40)==0xffff);
  bool lineInk=false;for(int y=150;y<170;y++)for(int x=0;x<320;x++)lineInk=lineInk||f.at(x,y)==0xffff;assert(lineInk);
  bool eyeRows=true;for(int y=0;y<150;y++)for(int x:{2,317})eyeRows=eyeRows&&f.at(x,y)==0;assert(eyeRows);
  crab::EyeFrame shut;shut.open=10;assert(f.face(shut,""));assert(f.at(160-52,70)==0xffff&&f.at(160-52,70-20)==0);
  crab::EyeFrame right;right.look=1;assert(f.face(right,""));assert(f.at(160-52+24,70)==0xffff&&f.at(160-52-28,70)==0);
  crab::EyeFrame happy;happy.happy=true;assert(f.face(happy,""));assert(f.at(160-52,70+16-26)==0xffff&&f.at(160-52,70+16)==0&&f.at(160-52,70+16+10)==0);}
 // Status line fits one row: long Wi-Fi failure drops the message, keeps the address.
 {Screen& f=s;char b[192];
  assert(std::string(f.statusLine("Đã vào Wi-Fi","172.168.20.249",b,sizeof b))=="Đã vào Wi-Fi  172.168.20.249");
  const char* ap="CuaRobot-6C13 192.168.4.1";
  assert(std::string(f.statusLine("Sai mật khẩu hoặc mất sóng",ap,b,sizeof b))==ap);
  assert(std::string(f.statusLine("Lỗi dây PCA9685","",b,sizeof b))=="Lỗi dây PCA9685");
  crab::EyeFrame open;assert(f.face(open,"Sai mật khẩu hoặc mất sóng",ap));
  for(int y=150;y<170;y++)for(int x=0;x<10;x++)assert(f.at(x,y)==0);} // centred, so it fit
 // Animation: blinks within 2.5-5.5 s, lasting 160 ms; glances come and go; walking is happy.
 {crab::Eyes e;int blinks=0,glances=0;bool wasShut=false;int8_t last=0;
  for(uint32_t t=0;t<60000;t+=20){auto fr=e.frame(t,false);assert(!fr.happy&&fr.open>=10&&fr.open<=100);
   const bool shut=fr.open<50;if(shut&&!wasShut)blinks++;wasShut=shut;if(fr.look!=0&&last==0)glances++;last=fr.look;}
  assert(blinks>=10&&blinks<=25&&glances>=3&&glances<=12);
  assert(e.frame(60000,true).happy&&e.frame(60020,true).open==100);
  crab::Eyes w;w.nextBlink=0xfffffff0;assert(w.frame(0xfffffff0,false).open==100&&w.frame(0x40,false).open<100);} // wrap-safe
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": actual Screen begin bus/pins/init/offset/rotation, QR draw callback; init failure stays dark; pet eyes face/blink/glance/happy\n";
}

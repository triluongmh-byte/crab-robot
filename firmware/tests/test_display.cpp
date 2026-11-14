#include <string>
#include "../crab/core.h"
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
 // Pet face: open eyes at their centres on black, a blink narrows them, a
 // glance shifts them, moods change the shape; the status line sits at the bottom.
 {Screen& f=s;crab::EyeFrame open;const int before=draws;const int L=160-52,R=160+52;
  assert(f.face(open,"Đã vào Wi-Fi 172.168.20.249")&&draws==before+1);
  assert(f.at(L,70)==0xffff&&f.at(R,70)==0xffff&&f.at(160,70)==0&&f.at(5,5)==0);
  assert(f.at(L,70-40)==0xffff&&f.at(L,70+40)==0xffff);
  bool lineInk=false;for(int y=150;y<170;y++)for(int x=0;x<320;x++)lineInk=lineInk||f.at(x,y)==0xffff;assert(lineInk);
  bool eyeRows=true;for(int y=0;y<150;y++)for(int x:{2,317})eyeRows=eyeRows&&f.at(x,y)==0;assert(eyeRows);
  crab::EyeFrame shut;shut.open=10;assert(f.face(shut,""));assert(f.at(L,70)==0xffff&&f.at(L,70-20)==0);
  crab::EyeFrame right;right.lookX=24;assert(f.face(right,""));assert(f.at(L+24,70)==0xffff&&f.at(L-28,70)==0);
  crab::EyeFrame up;up.lookY=-12;assert(f.face(up,""));assert(f.at(L,70-50)==0xffff&&f.at(L,70+38)==0);
  // Colour: eyes take the lamp's hue at full brightness; the panel gets
  // RGB565 high byte first (byte-swapped in the little-endian buffer).
  assert(crab::eyeColor(0)==0xffff&&crab::eyeColor(0xffffff)==0xffff&&crab::eyeColor(0xff0000)==0xf800&&crab::eyeColor(0x0000ff)==0x001f);
  assert(crab::eyeColor(0x100400)==crab::eyeColor(0xff4000)&&crab::eyeColor(0xff0f0f)==0xf861);
  crab::EyeFrame red;red.color=crab::eyeColor(0xff0f0f);assert(f.face(red,"Đã vào Wi-Fi"));
  assert(f.at(L,70)==0xf861&&f.raw(L,70)==0x61f8&&f.at(160,70)==0);
  bool whiteLine=false;for(int y=150;y<170;y++)for(int x=0;x<320;x++)whiteLine=whiteLine||f.at(x,y)==0xffff;assert(whiteLine); // status stays white
  using crab::Mood;
  auto mood=[&](Mood m){crab::EyeFrame e;e.mood=m;assert(f.face(e,""));};
  mood(Mood::Happy);assert(f.at(L,70+16-26)==0xffff&&f.at(L,70+16)==0&&f.at(L,70+16+10)==0);
  // Sad: lids droop at the outer corners; angry: at the inner corners.
  mood(Mood::Normal);assert(f.at(L-22,70-30)==0xffff&&f.at(L+22,70-30)==0xffff);
  mood(Mood::Sad);assert(f.at(L-22,70-30)==0&&f.at(R+22,70-30)==0&&f.at(L+22,70-30)==0xffff&&f.at(L,70+20)==0xffff);
  mood(Mood::Angry);assert(f.at(L+22,70-30)==0&&f.at(R-22,70-30)==0&&f.at(L-22,70-30)==0xffff&&f.at(L,70+20)==0xffff);
  mood(Mood::Surprised);assert(f.at(L-33,70)==0xffff&&f.at(L,70+44)==0xffff);   // wider and taller
  mood(Mood::Love);assert(f.at(L,70-6)==0xffff&&f.at(L-17,70-14)==0xffff&&f.at(L,70-6+17*3/2+4)==0&&f.at(L,70-30)==0);
  mood(Mood::Asleep);assert(f.at(L,70-4+25)==0xffff&&f.at(L,70-4)==0&&f.at(L,70-30)==0);
  mood(Mood::Wink);assert(f.at(L,70+16-26)==0xffff&&f.at(L,70+16)==0&&f.at(R,70)==0xffff); // left closed, right open
  {crab::EyeFrame e;e.mood=Mood::Sleepy;e.open=45;assert(f.face(e,""));assert(f.at(L,90)==0xffff&&f.at(L,60)==0);}} // heavy lids, sitting low
 // QR guide: every line of the right column fits its 154 px.
 {Screen& f=s;for(const char* t:{"1. Quét QR vào Wi-Fi cua","3. Chọn Wi-Fi nhà","Giữ BOOT 8s: xóa Wi-Fi"})assert(f.textWidth(t)<=2*154);
  assert(f.textWidth("Giữ BOOT 8s: xóa Wi-Fi")<=154&&f.textWidth("2. Mở 192.168.4.1")<=154);
  for(const char* m:{crab::msg::SETUP,crab::msg::FAILED,crab::msg::WRONG_PASS,crab::msg::NOT_FOUND,crab::msg::LOST,crab::msg::DRIVER})assert(f.textWidth(m)<=2*150);
  // Auto mode lines replace the Wi-Fi message on the face and must keep the address beside them.
  for(const char* m:{crab::automsg::ON,crab::automsg::MANUAL,crab::automsg::LOST,crab::automsg::STUCK})assert(f.textWidth(m)+f.textWidth("  192.168.100.200")<=Screen::STATUS_MAX_PX);
  const int before=draws;assert(f.show("WIFI:T:nopass;S:CuaRobot-6C13;;",crab::msg::WRONG_PASS,"192.168.4.1","CuaRobot-6C13")&&draws==before+1);}
 // Status line fits one row: long Wi-Fi failure drops the message, keeps the address.
 {Screen& f=s;char b[192];
  assert(std::string(f.statusLine("Đã vào Wi-Fi","172.168.20.249",b,sizeof b))=="Đã vào Wi-Fi  172.168.20.249");
  const char* ap="CuaRobot-6C13 192.168.4.1";
  assert(std::string(f.statusLine("Sai mật khẩu hoặc mất sóng",ap,b,sizeof b))==ap);
  assert(std::string(f.statusLine("Lỗi dây PCA9685","",b,sizeof b))=="Lỗi dây PCA9685");
  crab::EyeFrame open;assert(f.face(open,"Sai mật khẩu hoặc mất sóng",ap));
  for(int y=150;y<170;y++)for(int x=0;x<10;x++)assert(f.at(x,y)==0);} // centred, so it fit
 // Animation: blinks (some double), smooth glances in four directions, rare
 // quirks; walking is happy and looks towards the travel side; sleepy, asleep,
 // and a surprised wake-up.
 {crab::Eyes e;int blinks=0,glances=0,quirks=0,ups=0;bool wasShut=false;int8_t lastX=0;crab::Mood lastMood=crab::Mood::Normal;int maxStep=0;int8_t px=0;
  for(uint32_t t=0;t<120000;t+=20){auto fr=e.frame(t,false);assert(fr.open>=10&&fr.open<=100);
   const bool shut=fr.open<50;if(shut&&!wasShut)blinks++;wasShut=shut;if(fr.lookX!=0&&lastX==0)glances++;lastX=fr.lookX;if(fr.lookY<-6)ups++;
   if(fr.mood!=crab::Mood::Normal&&lastMood==crab::Mood::Normal)quirks++;lastMood=fr.mood;
   maxStep=std::max(maxStep,std::abs(fr.lookX-px));px=fr.lookX;assert(fr.mood!=crab::Mood::Sleepy&&fr.mood!=crab::Mood::Asleep);}
  assert(blinks>=25&&blinks<=70&&glances>=6&&glances<=30&&quirks>=3&&quirks<=10&&ups>0&&maxStep<=6); // eased, not jumping
  auto w=e.frame(120000,true);assert(w.mood==crab::Mood::Happy&&w.open==100);
  crab::Eyes wrap;wrap.nextBlink=0xfffffff0;assert(wrap.frame(0xfffffff0,false).open==100&&wrap.frame(0x40,false).open<100);} // wrap-safe
 {crab::Eyes e;crab::EyeInput in;in.walking=true;crab::travelLook(3,in.sideX,in.sideY);assert(in.sideX==cfg::EYE_LOOK_SIGN&&in.sideY==0);
  crab::EyeFrame fr;for(uint32_t t=0;t<400;t+=20)fr=e.frame(t,in);assert(fr.mood==crab::Mood::Happy&&fr.lookX==24*cfg::EYE_LOOK_SIGN);
  int8_t x,y;crab::travelLook(1,x,y);assert(x==0&&y==-1);crab::travelLook(8,x,y);assert(x==-cfg::EYE_LOOK_SIGN&&y==1);crab::travelLook(0,x,y);assert(x==0&&y==0);
  in=crab::EyeInput{};in.posing=true;in.mood=crab::Mood::Angry;assert(e.frame(500,in).mood==crab::Mood::Angry);
  in=crab::EyeInput{};in.idleMs=cfg::SLEEPY_MS;fr=e.frame(1000,in);assert(fr.mood==crab::Mood::Sleepy&&fr.open<=45);
  in.idleMs=cfg::ASLEEP_MS;assert(e.frame(1100,in).mood==crab::Mood::Asleep);
  in=crab::EyeInput{};in.walking=true;assert(e.frame(1200,in).mood==crab::Mood::Surprised);   // woken up
  assert(e.frame(2000,in).mood==crab::Mood::Happy);
  crab::EyeInput c;c.color=crab::eyeColor(0x2050ff);assert(e.frame(2100,c).color==c.color);
  crab::Mood m;assert(crab::moodFromName("love",m)&&m==crab::Mood::Love&&!crab::moodFromName("lov",m)&&!crab::moodFromName("lovee",m)&&std::string(crab::moodName(crab::Mood::Wink))=="wink");}
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": actual Screen begin bus/pins/init/offset/rotation, QR draw callback; init failure stays dark; pet eyes in lamp colour (byte order), 9 moods, blink/double blink/eased glance/quirks/walk look/sleepy/asleep/wake, QR join guide\n";
}

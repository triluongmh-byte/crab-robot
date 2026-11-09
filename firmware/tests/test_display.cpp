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
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": actual Screen begin bus/pins/init/offset/rotation, QR draw callback; init failure stays dark\n";
}

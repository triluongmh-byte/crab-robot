#include "../crab/config.h"
#include <cassert>
#include <iostream>
int main(){
 static_assert(cfg::SDA_PIN==18&&cfg::SCL_PIN==17&&cfg::LED_PIN==1&&cfg::BOOT_PIN==0,"contract pins");
 static_assert(cfg::USB_DM==19&&cfg::USB_DP==20,"native USB");
 static_assert(cfg::LCD_BL==38&&cfg::LCD_RST==5&&cfg::LCD_CS==6&&cfg::LCD_DC==7,"LCD common controls");
#if CRAB_INTEGRATED_BOARD
 static_assert(cfg::LCD_SPI&&cfg::LCD_SCLK==8&&cfg::LCD_MOSI==39&&cfg::LCD_SPI_HZ==10000000,"final SPI netlist");
 static_assert(cfg::POWER_PIN==-1&&cfg::PCA_OE_PIN==21,"GPIO21 OE; GPIO15 NC");
 static_assert(cfg::SONAR_TRIG[0]==-1&&cfg::SONAR_TRIG[1]==-1&&cfg::SONAR_ECHO[0]==-1&&cfg::SONAR_ECHO[1]==-1,"no ultrasonic header");
 static_assert(cfg::LCD_RD==-1&&cfg::LCD_WR==-1&&cfg::LCD_ROTATION_DEG==270,"case D15 rotation; no i80 pins");
 for(int pin:cfg::LCD_DATA)assert(pin==-1);
#else
 static_assert(!cfg::LCD_SPI&&cfg::POWER_PIN==15&&cfg::PCA_OE_PIN==-1,"LILYGO power unchanged");
 static_assert(cfg::SONAR_TRIG[0]==10&&cfg::SONAR_ECHO[0]==11&&cfg::SONAR_TRIG[1]==12&&cfg::SONAR_ECHO[1]==13,"front ultrasonics on free header GPIOs");
 static_assert(cfg::LCD_WR==8&&cfg::LCD_RD==9&&cfg::LCD_ROTATION_DEG==90,"LILYGO LCD unchanged");
 const int data[8]={39,40,41,42,45,46,47,48};for(int i=0;i<8;i++)assert(cfg::LCD_DATA[i]==data[i]);
#endif
 static_assert(cfg::PCA_ADDR==0x40&&cfg::PWM_HZ==50&&cfg::LED_COUNT==8,"devices");
 const int signs[8]={1,1,1,-1,1,-1,1,1};for(int i=0;i<8;i++)assert(cfg::SIGN[i]==signs[i]);
 std::cout<<"PASS: compiled target "<<cfg::HARDWARE_TARGET<<" pin/USB/display/channel/sign contract\n";
}

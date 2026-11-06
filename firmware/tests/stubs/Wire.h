#pragma once
#include <array>
#include <vector>
#include <cstdint>
inline void delay(int){}
struct MockWire {
 std::array<uint8_t,256> regs{};std::vector<uint8_t> tx;bool fail=false;int sda=-1,scl=-1,clock=0,timeout=0;uint8_t address=0;
 void begin(int a,int b,int c){sda=a;scl=b;clock=c;}
 void setTimeOut(int t){timeout=t;}
 void beginTransmission(uint8_t a){address=a;tx.clear();}
 void write(uint8_t value){tx.push_back(value);}
 int endTransmission(){
  if(fail)return 4;
  uint8_t reg=tx.at(0);
  for(size_t i=1;i<tx.size();i++,reg++){
   regs[reg]=tx[i];
   // Datasheet 7.3.4: ALL registers broadcast the pattern to each channel.
   if(reg>=0xFA&&reg<=0xFD)for(int ch=0;ch<16;ch++)regs[6+4*ch+(reg-0xFA)]=tx[i];
  }
  return 0;
 }
} inline Wire;

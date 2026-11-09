#pragma once
#include <vector>
#include <cstdint>
#include <cassert>
struct FakeWire{
 std::vector<std::vector<uint8_t>> writes;std::vector<uint8_t> buffer;bool fail=false;int sda=-1,scl=-1;uint32_t hz=0;
 void begin(int a,int b,uint32_t h){sda=a;scl=b;hz=h;}void setTimeOut(int){}
 void beginTransmission(uint8_t addr){assert(addr==0x40);buffer.clear();}void write(uint8_t v){buffer.push_back(v);}
 int endTransmission(){writes.push_back(buffer);return fail?4:0;}
};
extern FakeWire Wire;

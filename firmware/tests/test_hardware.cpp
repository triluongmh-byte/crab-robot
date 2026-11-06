#include "Hardware.h"
#include <cassert>
#include <iostream>
int main(){
 crab::Pca pca;
 // Simulate warm reset with retained non-zero pulse registers.
 Wire.regs.fill(0xFF);assert(pca.begin());
 assert(Wire.sda==18&&Wire.scl==17&&Wire.clock==400000&&Wire.timeout==10&&Wire.address==0x40);
 assert(Wire.regs[0xFE]==121&&Wire.regs[0]==0xA0&&Wire.regs[1]==4);
 for(int ch=0;ch<16;ch++)assert(Wire.regs[9+4*ch]&16);
 for(int count=0;count<8;count++){
  int ch=cfg::enableOrder[count];assert(pca.servo(ch,90));
  int on=Wire.regs[6+4*ch]+(Wire.regs[7+4*ch]<<8),off=Wire.regs[8+4*ch]+(Wire.regs[9+4*ch]<<8);
  assert(on==ch*512&&((off-on)&4095)==307);
  int active=0;for(int n=0;n<16;n++)if(!(Wire.regs[9+4*n]&16))active++;assert(active==count+1);
 }
 assert(pca.allOff());for(int ch=0;ch<16;ch++)assert(Wire.regs[9+4*ch]&16);
 Wire.fail=true;assert(!pca.begin()&&!pca.servo(0,90)&&!pca.allOff());
 std::cout<<"PASS PCA register mock: warm-reset outputs stay off, only scheduled channels enabled, 50Hz prescale, pulse phase, I2C failure\n";
}

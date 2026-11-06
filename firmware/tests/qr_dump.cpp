#include "QrEncoder.h"
#include <iostream>
#include <fstream>
#include <cassert>
int main(int argc,char** argv){
 assert(argc==3);QRCode qr;uint8_t data[128];assert(qrcode_initText(&qr,data,3,ECC_MEDIUM,argv[1])>=0);
 std::ofstream f(argv[2]);constexpr int scale=4,quiet=4;int size=(qr.size+2*quiet)*scale;
 f<<"P1\n"<<size<<" "<<size<<"\n";
 for(int y=0;y<size;y++){for(int x=0;x<size;x++){
 int u=x/scale-quiet,v=y/scale-quiet;
 bool black=u>=0&&v>=0&&u<qr.size&&v<qr.size&&qrcode_getModule(&qr,u,v);
 f<<(black?1:0)<<' ';}f<<'\n';}
}

#include "../../firmware/crab/core.h"
#include "../../firmware/crab/qrcodegen.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
using namespace crab;
static void ready(Motion& m,uint32_t now=0){m.selectActuator(true,now);for(int ch=0;ch<8;ch++){int seen=m.tick(now+10+ch*cfg::ENABLE_GAP_MS);assert(seen==ch);}assert(m.enabled==8);}
static void test_network(){
 Network n;n.begin(false,0);assert(n.state==NetState::Setup&&!n.saved);
 n.connect(true,100);n.tick(18100,false);assert(n.state==NetState::Setup&&!n.saved&&!n.saveRequested);assert(std::string(n.message)==msg::FAILED);
 n.connect(true,20000);n.tick(21000,true);assert(n.state==NetState::Online&&n.saved&&n.saveRequested);n.saveRequested=false;
 n.tick(22000,false);assert(n.state==NetState::Setup);n.tick(51999,false);assert(!n.retryRequested);n.tick(52000,false);assert(n.retryRequested&&n.state==NetState::Connecting);
 n.tick(53000,true);assert(n.state==NetState::Online&&!n.saveRequested);
 n.erase(54000);assert(!n.saved&&!n.pending&&n.state==NetState::Setup);n.tick(90000,false);assert(!n.retryRequested);
 n.begin(true,0xfffffff0);n.tick(0x00005000,false);assert(n.state==NetState::Setup); // timer wrap
 Network ap;ap.begin(true,0);ap.tick(100,false,false,true);
 assert(ap.state==NetState::Setup&&ap.pauseRequested&&!ap.retryRequested);
 ap.pauseRequested=false;
 for(uint32_t t=1000;t<180000;t+=1000){ap.tick(t,false,false,true);assert(ap.state==NetState::Setup&&!ap.retryRequested);}
 ap.tick(180000,false,false,false);assert(ap.retryRequested&&ap.state==NetState::Connecting);
 ap.retryRequested=false;ap.tick(180100,false,false,true);assert(ap.pauseRequested&&ap.state==NetState::Setup);
 ap.connect(true,181000);ap.tick(182000,false,false,true);assert(ap.pending&&ap.state==NetState::Connecting); // manual join still allowed
 ap.tick(182100,false,true,true);assert(ap.state==NetState::Setup&&!ap.pending&&std::string(ap.message)==msg::FAILED);
 ap.tick(220000,false,false,true);assert(!ap.retryRequested); // error remains visible on AP

}
static void test_button(){HoldButton b;assert(!b.tick(false,0));assert(!b.tick(true,100));assert(!b.tick(true,8099));assert(b.tick(true,8100));assert(!b.tick(true,8200));assert(!b.tick(false,8300));assert(!b.tick(true,9000));assert(b.tick(true,17000));}
static void test_case_knee_lift(){
 // Case D7/model.py: FR and RL each mirror FL once; RR mirrors twice.
 // Independent mounting parity converts the emitted pulse back to FL geometry.
 const int mirrorParity[4]={1,-1,-1,1};
 for(int leg=0;leg<4;leg++){
  const int ch=2*leg+1;
  const double shaftDeg=(pulse(ch,-15,0)-1500)/(2000.0/180.0);
  const double theta=mirrorParity[leg]*shaftDeg*3.141592653589793/180;
  // FOOT_TIP relative to knee: 15 mm outward, 64.6 mm below (+t axis).
  const double lift=-15*std::sin(theta)-64.6*std::cos(theta)+64.6;
  if(!(lift>5.5&&lift<6.5))std::cerr<<"Case knee lift failed: leg="<<leg<<" liftMm="<<lift<<"\n";
  assert(lift>5.5&&lift<6.5);
 }
}
static void test_unknown(){
 Motion m;m.begin(0);m.newSession(3);
 for(uint32_t t=10;t<5000;t+=10)assert(m.tick(t)==-1);
 assert(m.enabled==0&&!m.positional()&&!m.command(3,1,1,5000));
 assert(!m.centre()&&!m.trim(0,1));assert(m.setAssembly(true));assert(!m.centre());
 assert(!m.openTest(true));m.setAssembly(false);assert(m.openTest(true));
 assert(!m.selectActuator(true,5000));assert(m.test.config(7,327));
 assert(!m.test.config(8,307)&&!m.test.config(0,286)&&!m.test.config(0,328));
 assert(!m.testCommand(3,2,21,5000,true));assert(m.testCommand(3,3,20,5000,true));
 assert(m.test.counts==347&&m.test.active);m.tick(5499);assert(m.test.active);m.tick(5500);assert(!m.test.active);
 assert(!m.testCommand(3,4,20,5501,false));assert(m.testCommand(3,5,-20,5600,true));
 for(uint32_t t=5750;t<7600;t+=150)assert(m.testCommand(3,m.lastSeq+1,-20,t,false));
 m.tick(7600);assert(!m.test.active);assert(!m.testCommand(3,m.lastSeq+1,-20,7601,false));
 m.newSession(4);assert(!m.test.opened&&!m.test.active);
 assert(m.openTest(true));assert(m.testCommand(4,1,0,0xffffff00,true));m.tick(0x100);assert(!m.test.active); // wrap +512 ms deadman
 assert(pwmCounts(1500)==307&&std::fabs(nominalUs(307)-1499.0234f)<.01f);
}
static void test_motion(){
 Motion m;m.newSession(12);m.begin(0);assert(!m.command(12,1,1,0));assert(m.enabled==0);ready(m);
 assert(m.command(12,2,1,2200,true));assert(m.velocity.x==1);assert(!m.command(12,1,2,2210));
 m.tick(2699);assert(m.velocity.x==1);m.tick(2709);assert(m.velocity.x==0&&!m.lease);
 assert(!m.command(12,3,1,2710,false));assert(m.command(12,4,1,2720,true));
 assert(m.command(12,6,0,2730,false));assert(!m.command(12,5,1,2740,false));assert(!m.lease);
 assert(!m.command(13,7,1,2800));m.setAssembly(true);assert(!m.command(12,7,1,2810));
 m.centre();assert(m.raw);assert(pulse(2,25,12,true)==1500);
 assert(m.trim(2,1));assert(!m.raw&&m.offsets[2]==1);for(int i=0;i<99;i++)m.trim(2,1);assert(m.offsets[2]==cfg::TRIM_LIMIT);
 assert(!m.trim(8,1));assert(!m.trim(2,22));m.setAssembly(false);assert(!m.trim(2,-1));
 m.inhibit=true;assert(!m.command(12,8,1,2900));m.inhibit=false;assert(m.command(12,9,1,3000));m.newSession(99);assert(!m.lease&&!m.command(12,10,1,3010));
 for(int ch=0;ch<8;ch++)for(float a:{-100.f,-30.f,0.f,30.f,100.f})for(float o:{-99.f,0.f,99.f}){int p=pulse(ch,a,o);assert(p>=1033&&p<=1967);}
 Motion wrap;ready(wrap,0xfffff000);wrap.newSession(2);assert(wrap.command(2,1,1,0xffffff00));wrap.tick(0x200);assert(!wrap.lease);
 // Long realistic run tests the production scheduler, lease renewal, limits, ramp and exact startup order.
 for(int dir=1;dir<=8;dir++){
  Motion sim;ready(sim);sim.newSession(1);uint32_t seq=0;float previous[8]={};
  for(uint32_t t=2200;t<32200;t+=10){if(t%150==100)assert(sim.command(1,++seq,dir,t,!sim.lease));int ch=sim.tick(t);if(ch>=0){assert(std::fabs(sim.position[ch])<=cfg::JOINT_LIMIT);assert(std::fabs(sim.position[ch]-previous[ch])<=cfg::SLEW_DPS*.08f+.0001f);previous[ch]=sim.position[ch];}}
  sim.stop();for(uint32_t t=32200;t<38200;t+=10)sim.tick(t);assert(sim.amplitude==0);for(float v:sim.position)assert(std::fabs(v)<.001);
 }
}
static void test_qr(const std::string& path){
 assert(apName(0xABCD)=="CuaRobot-ABCD");assert(wifiQr(apName(0x1234))=="WIFI:T:nopass;S:CuaRobot-1234;;");assert(webQr("192.168.1.245")=="http://192.168.1.245/");
 const std::string cases[]={wifiQr(apName(0x1234)),webQr("192.168.1.245")};int index=0;
 for(auto& payload:cases){uint8_t tmp[qrcodegen_BUFFER_LEN_FOR_VERSION(5)],qr[qrcodegen_BUFFER_LEN_FOR_VERSION(5)];assert(qrcodegen_encodeText(payload.c_str(),tmp,qr,qrcodegen_Ecc_MEDIUM,1,5,qrcodegen_Mask_AUTO,true));int n=qrcodegen_getSize(qr);int scale=std::min(4,160/(n+8));assert(scale>=3);int side=(n+8)*scale;std::ofstream out(path+"/qr"+std::to_string(++index)+".pgm",std::ios::binary);out<<"P5\n"<<side<<" "<<side<<"\n255\n";for(int y=0;y<side;y++)for(int x=0;x<side;x++){int qx=x/scale-4,qy=y/scale-4;unsigned char c=qrcodegen_getModule(qr,qx,qy)?0:255;out.write((char*)&c,1);}}
}
static void simulation(const std::string& dir){
 std::ofstream out(dir+"/gait.csv");out<<"direction,phase,hip_fl,knee_fl,hip_fr,knee_fr,hip_rl,knee_rl,hip_rr,knee_rr,grounded_mask\n";
 std::ofstream report(dir+"/gait-summary.json");report<<"{\"model\":\"diagonal trot; ideal knee-angle contact and tangent stance projection; not physical stability or CAD collision proof\",\"contactToleranceDeg\":0.0001,\"directions\":[";
 for(int d=1;d<=8;d++){
  Vec v=direction(d);double sx=0,sy=0,maxAngle=0;int samples=720,minGrounded=4,maxLifted=0;
  int unilateralSupport=0,supportMasks[16]={};
  for(int k=0;k<samples;k++){
   float phase=k*6.2831853072f/samples,outAngles[8];gait(phase,v,1,outAngles);out<<d<<","<<phase;
   for(float a:outAngles){out<<","<<a;assert(std::fabs(a)<=cfg::JOINT_LIMIT);maxAngle=std::max(maxAngle,double(std::fabs(a)));}
   // Infer contact from the production knee output, not from the phase table:
   // negative knee = raised foot. Tolerance ignores float roundoff at zero.
   unsigned grounded=0;int count=0;
   for(int leg=0;leg<4;leg++)if(outAngles[2*leg+1]>=-0.0001f){grounded|=1u<<leg;count++;}
   out<<","<<grounded<<"\n";supportMasks[grounded]++;
   minGrounded=std::min(minGrounded,count);maxLifted=std::max(maxLifted,4-count);
   const bool bothSides=(grounded&0x5u)&&(grounded&0xAu); // FL/RL and FR/RR
   if(!bothSides)unilateralSupport++;
   if(!bothSides)std::cerr<<"Unilateral support: direction="<<d<<" sample="<<k<<" groundedMask="<<grounded<<"\n";
   assert(bothSides); // regression: the old quarter-phase gait fails here
   assert(count>=2&&(grounded&0x3u)&&(grounded&0xCu)); // front and rear too
   for(int leg=0;leg<4;leg++){
    const float p=phase+cfg::PHASE[leg];if(!(grounded&(1u<<leg)))continue;
    // hip derivative in stance; minus average ground velocity estimates body travel.
    double dq=cfg::HIP_AMPLITUDE*hipProjection(leg,v)*std::sin(p);
    sx-=dq*(-std::sin(cfg::RADIAL[leg]));sy-=dq*std::cos(cfg::RADIAL[leg]);
   }
  }
  double along=sx*v.x+sy*v.y,cross=sx*v.y-sy*v.x;assert(along>1);assert(std::fabs(cross)<along*.02);
  if(d>1)report<<",";report<<"{\"direction\":"<<d<<",\"forwardProjection\":"<<along<<",\"crossProjection\":"<<cross<<",\"maxJointDeg\":"<<maxAngle<<",\"samples\":"<<samples
   <<",\"minGroundedFeet\":"<<minGrounded<<",\"maxLiftedFeet\":"<<maxLifted<<",\"unilateralSupportSamples\":"<<unilateralSupport<<",\"groundedMaskSamples\":{";
  bool first=true;for(int mask=0;mask<16;mask++)if(supportMasks[mask]){if(!first)report<<",";first=false;report<<"\""<<mask<<"\":"<<supportMasks[mask];}report<<"}}";
 }
 report<<"],\"sidewaysSupportedByModel\":true,\"hardwareTested\":false}\n";
}
int main(int argc,char**argv){assert(argc==2);test_network();test_unknown();test_button();test_case_knee_lift();test_motion();test_qr(argv[1]);simulation(argv[1]);std::cout<<"PASS: unknown default/no startup, test bounds/deadman/cap/wrap, network, BOOT, lease, assembly, explicit positional startup, case knee lift from pulses, gait direction and diagonal foot support, pulse bounds, QR encoding\n";}

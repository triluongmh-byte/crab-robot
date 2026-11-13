#include "../../firmware/crab/core.h"
#include "../../firmware/crab/qrcodegen.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <vector>
using namespace crab;
static void ready(Motion& m,uint32_t now=0){m.selectActuator(true,now);for(int ch=0;ch<8;ch++){int seen=m.tick(now+20+ch*cfg::ENABLE_GAP_MS);assert(seen==ch);}assert(m.enabled==8);}
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
  const double shaftDeg=(pulse(ch,-15,0)-1500)/(1000.0/180.0);
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
 assert(m.enabled==0&&!m.positional()&&!m.command(3,1,1,5000));m.stop();
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
// Notes15/16: exercise the production policy, no invented shop speed.
static void test_manual90(){
 Continuous360 c;assert(!c.referenceValid&&c.viewpoint==Continuous360::Viewpoint::Pending);
 c.opened=true;
 for(int ch=0;ch<8;ch++)assert(c.configure(ch,307,267,347));
 assert(c.confirmReference());assert(!c.move(0,1,5,0,true)); // uncalibrated
 assert(std::string(c.reason).find("Chưa hiệu chỉnh")!=std::string::npos);
 assert(c.calibrate(0,1,267,20,100));assert(!c.referenceValid&&!c.active);
 assert(c.confirmReference());assert(!c.move(0,1,20,0,true)); // pending viewpoint
 assert(std::string(c.reason).find("Góc nhìn")!=std::string::npos);
 assert(c.setViewpoint(1));assert(!c.referenceValid&&!c.channels[0].cw.calibrated);
 // Check both directions on every hip and knee against independent expected budgets.
 const float cw[8]={25,35,25,35,55,35,55,35},ccw[8]={55,35,55,35,25,35,25,35};
 for(int ch=0;ch<8;ch++)for(int dir=1;dir<=2;dir++){
  assert(c.calibrate(ch,dir,dir==1?267:347,20,100));assert(!c.active&&!c.referenceValid);
  assert(c.confirmReference());assert(c.move(ch,dir,60,1000,true));
  float expected=dir==1?cw[ch]:ccw[ch];
  assert(c.clipped&&c.duration==uint32_t(expected/.2f));
  assert(c.validOutput());assert(!c.move((ch+1)%8,dir,60,1010,false));
  c.tick(1050);assert(std::fabs(c.estimated[ch]-(dir==1?10:-10))<.001);
  assert(c.move(ch,dir,60,1050,false)); // renewal never extends hard cap
  c.tick(1000+c.duration);assert(!c.active&&!c.referenceValid);
  assert(std::fabs(c.estimated[ch]-(dir==1?expected:-expected))<.001);
  assert(!c.move(ch,dir,60,2000,true)); // cannot chain bursts after expiry
  assert(c.confirmReference());c.estimated[ch]=(dir==1?1:-1)*(expected-1);
  assert(!c.move(ch,dir,60,3000,true)); // <50ms budget refuses, does not overrun
 }
 // Estimate integrates to partial time, then every manual off invalidates the pose.
 assert(c.confirmReference());assert(c.move(0,1,5,4000,true,100)==false); // <50ms at .2deg/ms
 assert(c.move(0,1,20,4000,true,50));assert(c.duration==50&&c.clipped);
 c.tick(4010);assert(std::fabs(c.estimated[0]-2)<.001);c.stop();assert(!c.referenceValid&&!c.active);
 assert(!c.move(0,1,20,4020,false));
 assert(c.confirmReference());assert(c.estimated[0]==0);assert(c.configure(0,307,267,347));assert(!c.referenceValid);
 assert(c.confirmReference());assert(c.calibrate(0,1,267,20,100));assert(!c.referenceValid);
 assert(!c.calibrate(0,2,267,20,100)); // no identical counts for opposite observed directions
 assert(!c.calibrate(0,2,347,NAN,100));assert(!c.calibrate(0,2,347,INFINITY,100));
 assert(!c.calibrate(0,2,347,20,0));assert(!c.calibrate(0,2,347,180,50));
 assert(c.confirmReference());assert(c.setViewpoint(2));assert(!c.referenceValid);
 assert(c.setViewpoint(0)); // knees symmetric, do not require pending hip viewpoint
 assert(c.calibrate(1,1,267,20,100));assert(c.confirmReference());assert(c.move(1,1,20,0xfffffff0,true));c.tick(0x54);assert(!c.referenceValid); // expiry across wrap
 Continuous360 reset;assert(!reset.referenceValid&&!reset.channels[0].cw.calibrated); // reset / power loss
 Motion m;m.newSession(1);assert(m.openContinuous(true));assert(m.continuous.confirmReference());
 m.newSession(2);assert(!m.continuous.referenceValid);
 assert(m.openContinuous(true));assert(m.continuous.confirmReference());m.inhibit=true;m.tick(1);assert(!m.continuous.referenceValid); // fault
 m.inhibit=false;assert(m.continuous.confirmReference());m.stop();assert(!m.continuous.referenceValid); // disconnect / global off
 assert(m.continuous.confirmReference());assert(m.openContinuous(false));assert(!m.continuous.referenceValid); // mode/settings
 assert(m.openTest(true));assert(m.test.config(0,307));assert(m.testCommand(2,1,4,100,true));assert(!m.continuous.referenceValid); // untracked motion
}
static void test_pair_sequence(){
 for(int group=0;group<2;group++)for(float u:{.1f,.3f,.55f,.6f,.7f,.8f,.9f,.95f}){
  float fwd[8],back[8];const float cycle=u+group*.5f;
  const float phase=(cycle-.25f)*6.2831853072f;
  gait(phase,direction(1),1,fwd);gait(phase,direction(2),1,back);
  const int first=group*2;
  for(int leg=0;leg<4;leg++){
   assert(std::fabs(fwd[2*leg]+back[2*leg])<.001f);
   assert(std::fabs(fwd[2*leg+1]-back[2*leg+1])<.001f);
  }
  assert(std::fabs(fwd[2*first+1]-fwd[2*(first+1)+1])<.001f);
  assert(std::fabs(fwd[2*first]+fwd[2*(first+1)])<.001f); // mirrored hip push
  if(u<.5f)assert(fwd[2*first+1]==0);
  if(u>.5f&&u<.625f)assert(std::fabs(std::fabs(fwd[2*first])-25)<.001f);
  if(u>.625f&&u<.875f)assert(std::fabs(fwd[2*first+1]+30)<.001f);
  if(u>.875f)assert(std::fabs(std::fabs(fwd[2*first])-25)<.001f);
 }
 // First forward frame commands front hips from neutral towards the rear.
 float initial[8],after[8];gait(0,direction(1),1,initial);gait(.02f,direction(1),1,after);
 assert(std::fabs(initial[0])<.001f&&std::fabs(initial[2])<.001f);
 assert(after[0]>initial[0]&&after[2]<initial[2]&&after[1]==0&&after[3]==0);
}
static void test_normal_speed(){
 Motion m;assert(std::fabs(m.speed-.65f)<.001f);assert(cfg::SLEW_DPS==180);
 // Half a second of Normal advances about0.19 of a paired cycle.
 ready(m);m.newSession(91);uint32_t seq=0;const uint32_t begin=2200;
 const float phase=m.phase;
 for(uint32_t t=begin;t<begin+500;t+=10){if((t-begin)%150==0)assert(m.command(91,++seq,1,t,true));m.tick(t);}
 const float advance=m.phase-phase;assert(advance>1.1f&&advance<1.3f);
 m.stop();for(uint32_t t=begin+500;t<begin+1000;t+=10)m.tick(t);assert(!m.lease&&m.amplitude==0);
}
static void test_motion(){
 Motion m;m.newSession(12);m.begin(0);assert(!m.command(12,1,1,0));m.stop();assert(m.enabled==0);ready(m);
 assert(m.command(12,2,1,2200,true));assert(m.velocity.x==1);assert(!m.command(12,1,2,2210));
 m.tick(2699);assert(m.velocity.x==1);m.tick(2709);assert(m.velocity.x==0&&!m.lease);
 assert(!m.command(12,3,1,2710,false));assert(m.command(12,4,1,2720,true));
 assert(m.command(12,6,0,2730,false));assert(!m.command(12,5,1,2740,false));assert(!m.lease);
 assert(!m.command(13,7,1,2800));m.setAssembly(true);assert(!m.command(12,7,1,2810));
 m.centre();assert(m.raw);assert(pulse(2,25,12,true)==1500);
 assert(m.trim(2,1));assert(!m.raw&&m.offsets[2]==1);for(int i=0;i<99;i++)m.trim(2,1);assert(m.offsets[2]==cfg::TRIM_LIMIT);
 assert(!m.trim(8,1));assert(!m.trim(2,22));m.setAssembly(false);assert(!m.trim(2,-1));
 m.inhibit=true;assert(!m.command(12,8,1,2900));m.inhibit=false;assert(m.command(12,9,1,3000));m.newSession(99);assert(!m.lease&&!m.command(12,10,1,3010));
 for(int ch=0;ch<8;ch++)for(float a:{-100.f,-30.f,0.f,30.f,100.f})for(float o:{-99.f,0.f,99.f}){int p=pulse(ch,a,o);assert(p>=1033&&p<=1967);const int limit=ch%2?195:139;assert(std::abs(p-1500)<=limit);}
 Motion wrap;ready(wrap,0xfffff000);wrap.newSession(2);assert(wrap.command(2,1,1,0xffffff00));wrap.tick(0x200);assert(!wrap.lease);
 // Long realistic run tests the production scheduler, lease renewal, limits, ramp and exact startup order.
 for(int dir=1;dir<=8;dir++){
  Motion sim;ready(sim);sim.newSession(1);uint32_t seq=0;float previous[8]={};
  for(uint32_t t=2200;t<32200;t+=10){if(t%150==100)assert(sim.command(1,++seq,dir,t,!sim.lease));int ch=sim.tick(t);if(ch>=0)for(int joint=0;joint<8;joint++){assert(std::fabs(sim.position[joint])<=cfg::JOINT_LIMIT);assert(std::fabs(sim.position[joint]-previous[joint])<=cfg::SLEW_DPS*.05f+.0001f);previous[joint]=sim.position[joint];}}
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
 std::ofstream report(dir+"/gait-summary.json");report<<"{\"model\":\"front/rear pair gait; ideal knee-angle contact and tangent stance projection; not physical stability or CAD collision proof\",\"contactToleranceDeg\":0.0001,\"directions\":[";
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
   assert(count>=2); // front or rear pair; no front/rear support guarantee
   for(int leg=0;leg<4;leg++){
    if(!(grounded&(1u<<leg)))continue;
    // Finite differences of the actual gait, independent of its phase formula.
    float next[8];gait(phase+.0001f,v,1,next);
    double dq=(next[2*leg]-outAngles[2*leg])/.0001;
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
int main(int argc,char**argv){assert(argc==2);test_network();test_unknown();test_button();test_case_knee_lift();test_pair_sequence();test_normal_speed();test_motion();test_manual90();test_qr(argv[1]);simulation(argv[1]);std::cout<<"PASS: manual90 reference/invalidation/calibration pending/CW viewpoint/all8 budgets both directions/clipping/refusal/estimate; unknown default/no startup, test bounds/deadman/cap/wrap, network, BOOT, lease, assembly, explicit positional startup, case knee lift from pulses, front-rear pair push/lift/return/lower/full hip stroke/forward-back reversal, pulse bounds, QR encoding\n";}

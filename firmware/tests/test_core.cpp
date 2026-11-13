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
 // Boot attempt hard-fails early but the link comes up anyway: adopt it, never
 // retry (retry = WiFi.disconnect of a working link every 30 s).
 {Network late;late.begin(true,0);late.tick(600,false,true);assert(late.state==NetState::Setup&&std::string(late.message)==msg::FAILED);
  late.tick(5000,true);assert(late.state==NetState::Online&&std::string(late.message)==msg::ONLINE);
  for(uint32_t t=6000;t<200000;t+=1000){late.tick(t,true);assert(late.state==NetState::Online&&!late.retryRequested);}
  Network fresh;fresh.begin(false,0);fresh.tick(100,true);assert(fresh.state==NetState::Setup);} // no saved network: unchanged
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
  gait(phase,direction(1),1,fwd,Pattern::Pairs);gait(phase,direction(2),1,back,Pattern::Pairs);
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
 float initial[8],after[8];gait(0,direction(1),1,initial,Pattern::Pairs);gait(.02f,direction(1),1,after,Pattern::Pairs);
 assert(std::fabs(initial[0])<.001f&&std::fabs(initial[2])<.001f);
 assert(after[0]>initial[0]&&after[2]<initial[2]&&after[1]==0&&after[3]==0);
}
static void test_trot_sequence(){
 // Diagonal pairs FL+RR (legs0,3) and FR+RL (legs1,2), half a cycle apart.
 const int pairs[2][2]={{0,3},{1,2}};
 const cfg::GaitPattern& g=cfg::TROT;
 for(int group=0;group<2;group++)for(float u:{.1f,.3f,.5f,.6f,.62f,.7f,.8f,.95f}){
  float fwd[8],back[8];const float cycle=u+group*.5f;
  const float phase=(cycle-g.start)*6.2831853072f;
  gait(phase,direction(1),1,fwd);gait(phase,direction(2),1,back);
  const int a=pairs[group][0],b=pairs[group][1];
  for(int leg=0;leg<4;leg++){
   assert(std::fabs(fwd[2*leg]+back[2*leg])<.001f);
   assert(std::fabs(fwd[2*leg+1]-back[2*leg+1])<.001f);
  }
  assert(std::fabs(fwd[2*a+1]-fwd[2*b+1])<.001f); // diagonal knees together
  assert(std::fabs(fwd[2*a]+fwd[2*b])<.001f); // opposite tangents: mirrored command, same foot motion
  if(u<g.stance)assert(fwd[2*a+1]==0);
  if(u>g.stance+g.lift&&u<g.stance+g.lift+g.swing)assert(std::fabs(fwd[2*a+1]+cfg::KNEE_LIFT)<.001f);
 }
 // Linear stance: grounded hips move at one constant rate (no scrub in overlap).
 float x0[8],x1[8],x2[8];gait(.5f,direction(1),1,x0);gait(.6f,direction(1),1,x1);gait(.7f,direction(1),1,x2);
 assert(std::fabs((x1[0]-x0[0])-(x2[0]-x1[0]))<.001f);
 // First forward frame: every hip starts from neutral.
 float initial[8];gait(0,direction(1),1,initial);for(int leg=0;leg<4;leg++)assert(std::fabs(initial[2*leg])<.001f);
 // Default Motion pattern is the trot.
 Motion m;assert(m.gaitPattern==Pattern::Trot&&std::string(patternName(m.gaitPattern))=="trot"&&std::string(patternName(Pattern::Pairs))=="pairs");
}
static void test_tracking(){
 // At Fast the slew limit must not make joints lag their targets; a lagging
 // hip would still be returning when the knee lowers (foot lands mid-swing).
 for(Pattern which:{Pattern::Trot,Pattern::Pairs,Pattern::Flick})for(int dir=1;dir<=4;dir++){
  Motion m;ready(m);m.newSession(5);m.speed=1;m.gaitPattern=which;uint32_t seq=0;double worst=0;
  for(uint32_t t=2200;t<12200;t+=10){
   if(t%150==100)assert(m.command(5,++seq,dir,t,!m.lease));
   if(m.tick(t)!=0||t<6200)continue;
   float target[8];gait(m.phase,bodyDirection(dir),m.amplitude,target,which);
   for(int ch=0;ch<8;ch++)worst=std::max(worst,double(std::fabs(target[ch]-m.position[ch])));
  }
  if(worst>=2.5)std::cerr<<"Tracking lag: pattern="<<int(which)<<" dir="<<dir<<" worstDeg="<<worst<<"\n";
  assert(worst<2.5);
 }
}
static void test_flick(){
 assert(std::string(patternName(Pattern::Flick))=="flick");
 // Owner frame: CH0 is rear right, so Forward/Left are rotated 180 deg into CAD.
 assert(cfg::FRONT_IS_CH46&&bodyDirection(1).x==-1&&bodyDirection(2).x==1&&bodyDirection(3).y==-1&&bodyDirection(4).y==1);
 assert(flickActive(Pattern::Flick,direction(1))&&flickActive(Pattern::Flick,direction(2)));
 assert(!flickActive(Pattern::Flick,direction(3))&&!flickActive(Pattern::Flick,direction(5))&&!flickActive(Pattern::Trot,direction(1)));
 assert(cyclePeriod(Pattern::Flick,direction(1))==cfg::FLICK_PERIOD_S&&cyclePeriod(Pattern::Flick,direction(3))==cfg::PERIOD_S);
 // Left/Right in flick mode are exactly the trot.
 for(int d:{3,4})for(float ph:{0.f,1.f,2.5f,4.f}){float a[8],b[8];gait(ph,direction(d),1,a,Pattern::Flick);gait(ph,direction(d),1,b);for(int i=0;i<8;i++)assert(a[i]==b[i]);}
 // Knee profile of one leg over a cycle: when it first reaches full lift and
 // when it is next back near the ground.
 auto profile=[](int dir,int leg,double& rise,double& fall){
  rise=fall=-1;
  for(int k=0;k<1000;k++){float o[8];gait(k*6.2831853072f/1000,bodyDirection(dir),1,o,Pattern::Flick);const double u=k/1000.;
   if(rise<0&&o[2*leg+1]<=-cfg::KNEE_LIFT+.001f)rise=u;
   if(rise>=0&&fall<0&&o[2*leg+1]>=-.05f&&u>rise)fall=u;}
  assert(rise>=0&&fall>rise);
 };
 for(int dir:{1,2}){
  float first[8];gait(0,bodyDirection(dir),1,first,Pattern::Flick);
  for(int k=0;k<1000;k++){
   float o[8];gait(k*6.2831853072f/1000,bodyDirection(dir),1,o,Pattern::Flick);
   // Hips hold the 90 deg stance: CAD legs 0,1 (CH0-3, physical rear) towards
   // CAD +X = physical rear; CH4-7 (physical front) towards physical front.
   for(int leg=0;leg<4;leg++)assert(o[2*leg]==first[2*leg]&&std::fabs(std::fabs(o[2*leg])-cfg::FLICK_HIP)<.001f);
   assert(o[0]<-89.9f&&o[2]>89.9f&&o[4]>89.9f&&o[6]<-89.9f);
   for(int leg=0;leg<4;leg++)assert(o[2*leg+1]<=0.0001f&&o[2*leg+1]>=-cfg::KNEE_LIFT-.0001f);
   // Same-side legs (same stance) run the same profile half a cycle apart.
   float h[8];gait((k/1000.f+.5f)*6.2831853072f,bodyDirection(dir),1,h,Pattern::Flick);
   assert(std::fabs(o[1]-h[3])<.001f&&std::fabs(o[7]-h[5])<.001f);
  }
  // Physical Forward (dir 1): rear legs (CH1 knee) trail and get the fast
  // drop; front legs (CH7 knee) lead and snap up fast. Backward swaps them.
  double rr,rf,fr,ff;profile(dir,0,rr,rf);profile(dir,3,fr,ff);
  const bool rearTrails=dir==1;
  const double trailRise=rearTrails?rr:fr,trailFall=rearTrails?rf:ff,leadRise=rearTrails?fr:rr,leadFall=rearTrails?ff:rf;
  assert(trailRise>.7&&trailFall-trailRise<=cfg::FLICK_STROKE+.01);
  assert(leadRise<=cfg::FLICK_STROKE+.01&&leadFall-leadRise>.7);
 }
 // Owner hip slider scales the stance; it never exceeds FLICK_HIP.
 {float o[8];gait(0,bodyDirection(1),1,o,Pattern::Flick,45);for(int leg=0;leg<4;leg++)assert(std::fabs(std::fabs(o[2*leg])-45)<.001f);
  gait(0,bodyDirection(1),1,o,Pattern::Flick,200);for(int leg=0;leg<4;leg++)assert(std::fabs(std::fabs(o[2*leg])-cfg::FLICK_HIP)<.001f);
  Motion m;assert(m.flickHip==cfg::FLICK_HIP);}
 // Heading trim: physical right legs are CH0 (rear right) and CH4 (front right).
 assert(physicalRight(0)&&!physicalRight(1)&&physicalRight(2)&&!physicalRight(3));
 {float o[8]={10,5,10,5,10,5,10,5};applyBalance(o,20);assert(std::fabs(o[0]-12)<1e-4f&&std::fabs(o[2]-8)<1e-4f&&std::fabs(o[4]-12)<1e-4f&&std::fabs(o[6]-8)<1e-4f&&o[1]==5&&o[7]==5);
  float c[8]={10,0,10,0,10,0,10,0};applyBalance(c,99);assert(std::fabs(c[0]-13)<1e-4f&&std::fabs(c[2]-7)<1e-4f);} // clamped to 30%
 {Motion m;assert(m.balance==0&&m.setBalance(-30)&&m.balance==-30&&!m.setBalance(31)&&!m.setBalance(-31)&&m.balance==-30);}
 {// Walking applies the trim to the hip targets the joints track.
  Motion a,b;ready(a);ready(b);a.newSession(3);b.newSession(3);b.setBalance(25);
  for(uint32_t t=2200;t<5200;t+=10){if(t%150==100){assert(a.command(3,a.lastSeq+1,1,t,!a.lease));assert(b.command(3,b.lastSeq+1,1,t,!b.lease));}a.tick(t);b.tick(t);}
  double ra=0,rb=0,la=0,lb=0;for(int leg=0;leg<4;leg++){if(physicalRight(leg)){ra+=std::fabs(a.position[2*leg]);rb+=std::fabs(b.position[2*leg]);}else{la+=std::fabs(a.position[2*leg]);lb+=std::fabs(b.position[2*leg]);}}
  assert(rb>ra*1.15&&lb<la*.85);}
 // Boot arm follows the Bật servo path, only with a working driver.
 {Motion m;assert(cfg::AUTO_ARM&&!m.bootArm(false,0)&&!m.positional());assert(m.bootArm(true,0)&&m.positional()&&m.enabled==0);
  for(uint32_t t=0;t<3000;t+=10)m.tick(t);assert(m.enabled==8);}
 // The fix for IMG_2637: Forward and Backward knee patterns now differ.
 float f[8],b[8];bool differ=false;
 for(int k=0;k<100;k++){gait(k*.0628f,bodyDirection(1),1,f,Pattern::Flick);gait(k*.0628f,bodyDirection(2),1,b,Pattern::Flick);for(int i=1;i<8;i+=2)differ=differ||std::fabs(f[i]-b[i])>1;}
 assert(differ);
}
static void test_pose(){
 Motion m;const float a[8]={20,-30,-20,-30,10,0,-10,0};
 assert(!m.poseCommand(1,1,a,300,0,true)); // not armed
 ready(m);m.newSession(5);uint32_t t=2200;
 float bad[8]={0,0,0,0,0,0,0,NAN};assert(!m.poseCommand(5,1,bad,300,t,true)&&!m.posing);
 assert(m.poseCommand(5,2,a,300,t,true)&&m.posing&&m.lease);
 // Move over the requested 300 ms (not instantly), and clamp to JOINT_LIMIT.
 for(uint32_t k=t;k<t+150;k+=10)m.tick(k);assert(m.position[1]<-10&&m.position[1]>-20);
 for(uint32_t k=t+150;k<t+400;k+=10){if(k%100==0)assert(m.poseCommand(5,m.lastSeq+1,a,0,k,false));m.tick(k);}
 for(int ch=0;ch<8;ch++)assert(std::fabs(m.position[ch]-a[ch])<.01f);
 float big[8]={90,-90,0,0,0,0,0,0};assert(m.poseCommand(5,m.lastSeq+1,big,0,t+400,false)&&m.pose[0]==cfg::JOINT_LIMIT&&m.pose[1]==-cfg::JOINT_LIMIT);
 assert(m.poseCommand(5,m.lastSeq+1,a,0,t+410,false));for(uint32_t k=t+410;k<t+500;k+=10)m.tick(k);
 // Deadman: no renewal for 500 ms -> relax towards standing at RELAX_DPS.
 uint32_t k=t+500;while(m.posing){m.tick(k);k+=10;}assert(m.relaxing&&k-(t+410)>=cfg::DEADMAN_MS&&k-(t+410)<=cfg::DEADMAN_MS+30);
 const float before=m.position[1];m.tick(k+=20);m.tick(k+=20);assert(std::fabs(m.position[1]-before)<=cfg::RELAX_DPS*.07f&&std::fabs(m.position[1]-before)>0);
 for(int i=0;i<200;i++)m.tick(k+=20);for(float v:m.position)assert(std::fabs(v)<.01f);assert(!m.relaxing);
 // Stale non-fresh pose refused; walking command cancels a pose; assembly blocks poses.
 assert(!m.poseCommand(5,m.lastSeq+1,a,0,k,false));
 assert(m.poseCommand(5,m.lastSeq+1,a,0,k,true));assert(m.command(5,m.lastSeq+1,1,k+10,true)&&!m.posing&&!m.relaxing);
 m.stop();m.setAssembly(true);assert(!m.poseCommand(5,m.lastSeq+1,a,0,k+20,true));
}
static void test_normal_speed(){
 Motion m;assert(std::fabs(m.speed-cfg::SPEED_DEFAULT)<.001f&&cfg::SPEED_DEFAULT==.9f);assert(cfg::SLEW_DPS==600&&cfg::PERIOD_S==0.8f);
 // Half a second at the 90% default advances about 0.56 of a cycle (0.89 s period).
 ready(m);m.newSession(91);uint32_t seq=0;const uint32_t begin=2200;
 const float phase=m.phase;
 for(uint32_t t=begin;t<begin+500;t+=10){if((t-begin)%150==0)assert(m.command(91,++seq,1,t,true));m.tick(t);}
 const float advance=m.phase-phase;assert(advance>3.46f&&advance<3.95f);
 m.stop();for(uint32_t t=begin+500;t<begin+1000;t+=10)m.tick(t);assert(!m.lease&&m.amplitude==0);
}
static void test_motion(){
 Motion m;m.newSession(12);m.begin(0);assert(!m.command(12,1,1,0));m.stop();assert(m.enabled==0);ready(m);
 assert(m.command(12,2,1,2200,true));assert(m.velocity.x==-1);assert(!m.command(12,1,2,2210));
 m.tick(2699);assert(m.velocity.x==-1);m.tick(2709);assert(m.velocity.x==0&&!m.lease);
 assert(!m.command(12,3,1,2710,false));assert(m.command(12,4,1,2720,true));
 assert(m.command(12,6,0,2730,false));assert(!m.command(12,5,1,2740,false));assert(!m.lease);
 assert(!m.command(13,7,1,2800));m.setAssembly(true);assert(!m.command(12,7,1,2810));
 m.centre();assert(m.raw);assert(pulse(2,25,12,true)==1500);
 assert(m.trim(2,1));assert(!m.raw&&m.offsets[2]==1);for(int i=0;i<99;i++)m.trim(2,1);assert(m.offsets[2]==cfg::TRIM_LIMIT);
 assert(!m.trim(8,1));assert(!m.trim(2,22));m.setAssembly(false);assert(!m.trim(2,-1));
 m.inhibit=true;assert(!m.command(12,8,1,2900));m.inhibit=false;assert(m.command(12,9,1,3000));m.newSession(99);assert(!m.lease&&!m.command(12,10,1,3010));
 for(int ch=0;ch<8;ch++)for(float a:{-100.f,-30.f,0.f,30.f,100.f})for(float o:{-99.f,0.f,99.f}){int p=pulse(ch,a,o);assert(p>=1000&&p<=2000);const int limit=ch%2?195:500;assert(std::abs(p-1500)<=limit);}
 // Hips reach the full 90 deg flick stance; knees still stop at 35 deg.
 assert(pulse(0,90,0)==2000&&pulse(0,-90,0)==1000&&pulse(1,90,0)==1667&&pulse(1,90,12)==1694);
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
static void simulatePattern(Pattern which,std::ofstream& out,std::ofstream& report){
 const bool trot=which==Pattern::Trot;
 for(int d=1;d<=8;d++){
  Vec v=direction(d);double sx=0,sy=0,maxAngle=0,maxYaw=0;int samples=720,minGrounded=4,maxLifted=0,fourFoot=0;
  int unilateralSupport=0,supportMasks[16]={};
  for(int k=0;k<samples;k++){
   float phase=k*6.2831853072f/samples,outAngles[8];gait(phase,v,1,outAngles,which);out<<patternName(which)<<","<<d<<","<<phase;
   for(float a:outAngles){out<<","<<a;assert(std::fabs(a)<=cfg::JOINT_LIMIT);maxAngle=std::max(maxAngle,double(std::fabs(a)));}
   // Infer contact from the production knee output, not from the phase table:
   // negative knee = raised foot. Tolerance ignores float roundoff at zero.
   unsigned grounded=0;int count=0;
   for(int leg=0;leg<4;leg++)if(outAngles[2*leg+1]>=-0.0001f){grounded|=1u<<leg;count++;}
   out<<","<<grounded<<"\n";supportMasks[grounded]++;if(count==4)fourFoot++;
   minGrounded=std::min(minGrounded,count);maxLifted=std::max(maxLifted,4-count);
   const bool bothSides=(grounded&0x5u)&&(grounded&0xAu); // FL/RL and FR/RR
   if(!bothSides)unilateralSupport++;
   if(!bothSides)std::cerr<<"Unilateral support: direction="<<d<<" sample="<<k<<" groundedMask="<<grounded<<"\n";
   assert(bothSides); // regression: the old quarter-phase gait fails here
   assert(count>=2);
   // Trot support always includes a full diagonal, which passes under the body centre.
   if(trot)assert((grounded&0x9u)==0x9u||(grounded&0x6u)==0x6u);
   // Feet sit on rays RADIAL[leg] at equal reach R: yaw of a grounded foot about
   // the body centre is R^2*dq, so body yaw rate is proportional to the sum of
   // grounded hip rates (hip SIGN is +1 on every leg).
   float next[8];gait(phase+.0001f,v,1,next,which);double yaw=0;
   for(int leg=0;leg<4;leg++){
    if(!(grounded&(1u<<leg)))continue;
    // Finite differences of the actual gait, independent of its phase formula.
    double dq=(next[2*leg]-outAngles[2*leg])/.0001;
    sx-=dq*(-std::sin(cfg::RADIAL[leg]));sy-=dq*std::cos(cfg::RADIAL[leg]);yaw+=dq;
   }
   maxYaw=std::max(maxYaw,std::fabs(yaw));
  }
  // Trot is yaw-free in every direction; owner pairs only for Forward/Backward.
  if(trot||d<=2){if(maxYaw>.01)std::cerr<<"Yaw: pattern="<<patternName(which)<<" direction="<<d<<" maxYaw="<<maxYaw<<"\n";assert(maxYaw<.01);}
  if(trot)assert(fourFoot>=samples/10);
  double along=sx*v.x+sy*v.y,cross=sx*v.y-sy*v.x;assert(along>1);assert(std::fabs(cross)<along*.02);
  if(d>1)report<<",";report<<"{\"direction\":"<<d<<",\"forwardProjection\":"<<along<<",\"crossProjection\":"<<cross<<",\"maxYawRate\":"<<maxYaw<<",\"maxJointDeg\":"<<maxAngle<<",\"samples\":"<<samples
   <<",\"minGroundedFeet\":"<<minGrounded<<",\"maxLiftedFeet\":"<<maxLifted<<",\"fourFootSamples\":"<<fourFoot<<",\"unilateralSupportSamples\":"<<unilateralSupport<<",\"groundedMaskSamples\":{";
  bool first=true;for(int mask=0;mask<16;mask++)if(supportMasks[mask]){if(!first)report<<",";first=false;report<<"\""<<mask<<"\":"<<supportMasks[mask];}report<<"}}";
 }
}
static void simulation(const std::string& dir){
 std::ofstream out(dir+"/gait.csv");out<<"pattern,direction,phase,hip_fl,knee_fl,hip_fr,knee_fr,hip_rl,knee_rl,hip_rr,knee_rr,grounded_mask\n";
 std::ofstream report(dir+"/gait-summary.json");report<<"{\"model\":\"default diagonal trot plus owner front/rear pairs option; ideal knee-angle contact, tangent stance projection and equal-reach yaw; not physical stability or CAD collision proof\",\"contactToleranceDeg\":0.0001,\"defaultPattern\":\"trot\",\"directions\":[";
 simulatePattern(Pattern::Trot,out,report);
 report<<"],\"ownerPairsDirections\":[";
 simulatePattern(Pattern::Pairs,out,report);
 report<<"],\"sidewaysSupportedByModel\":true,\"hardwareTested\":false}\n";
}
int main(int argc,char**argv){assert(argc==2);test_network();test_unknown();test_button();test_case_knee_lift();test_pair_sequence();test_trot_sequence();test_flick();test_pose();test_tracking();test_normal_speed();test_motion();test_manual90();test_qr(argv[1]);simulation(argv[1]);std::cout<<"PASS: manual90 reference/invalidation/calibration pending/CW viewpoint/all8 budgets both directions/clipping/refusal/estimate; unknown default/no startup, test bounds/deadman/cap/wrap, network, BOOT, lease, assembly, explicit positional startup, case knee lift from pulses, diagonal trot default/owner knee flick forward-back with held hip pose/emotion pose timing/clamp/lease/deadman relax/walk cancel/assembly block/four-foot overlap/zero yaw all 8 directions/Fast slew tracking, owner front-rear pairs option push/lift/return/lower/full hip stroke/forward-back reversal, pulse bounds, QR encoding\n";}

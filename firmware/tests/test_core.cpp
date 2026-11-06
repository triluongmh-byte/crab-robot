#include "Robot.h"
#include <cassert>
#include <iostream>
#include <vector>
#include <cmath>
using namespace crab;
struct Memory:Storage {
 std::map<Str,Str> data;bool writable=true;
 Str get(const Str& k)override{return data[k];}
 bool put(const Str& k,const Str& v)override{if(!writable)return false;data[k]=v;return true;}
 bool erase(const Str& k)override{if(!writable)return false;data.erase(k);return true;}
};
struct MockRadio:Radio {
 bool up=false,ap=false;Str ssid,password,ip="192.168.1.42";int joins=0;
 void accessPoint(const Str&)override{ap=true;}
 void join(const Str& s,const Str& p)override{ssid=s;password=p;up=false;joins++;}
 void stopAP()override{ap=false;}
 void disconnect()override{up=false;}
 bool connected()override{return up;}
 Str address()override{return ip;}
};
struct Fixture {
 Memory store;MockRadio radio;Wifi wifi{store,radio,"CuaRobot-ABCD"};Robot robot{store};Api api{robot,wifi};
 Fixture(){wifi.begin(0);robot.begin(0);for(uint32_t t=0;t<=2200;t+=10)robot.tick(t);robot.network(true);}
 Response post(Str path,std::map<Str,Str> args={},uint32_t now=2500){return api.handle({"POST",path,args},now);}
 Response move(Str dir,uint32_t seq=1,uint32_t now=2500){return post("/api/move",{{"client","phone"},{"seq",std::to_string(seq)},{"dir",dir}},now);}
};
void wifiTests(){
 Memory mem;MockRadio radio;Wifi wifi(mem,radio,"CuaRobot-A01F");wifi.begin(7);
 assert(wifi.state==WifiState::Portal&&radio.ap);assert(wifi.qr()=="WIFI:T:nopass;S:CuaRobot-A01F;;");
 assert(!wifi.submit("","secret",10));assert(!wifi.submit(Str(33,'a'),"secret",10));
 assert(wifi.submit("Nhà","not-echoed",20));assert(wifi.state==WifiState::Connecting);assert(mem.get("wifi").empty());
 assert(!wifi.submit("Other","x",30));wifi.tick(15019);assert(wifi.state==WifiState::Connecting);
 wifi.tick(15020);assert(wifi.state==WifiState::Portal&&radio.ap);assert(wifi.message.find("Sai mật khẩu")!=Str::npos);assert(mem.get("wifi").empty());
 assert(wifi.submit("Home","good-password",16000));radio.up=true;wifi.tick(16001);
 assert(wifi.state==WifiState::Online&&!radio.ap);assert(wifi.qr()=="http://192.168.1.42/");assert(mem.get("wifi")=="4:Homegood-password");
 Wifi reboot(mem,radio,"CuaRobot-A01F");reboot.begin(18000);assert(reboot.state==WifiState::Connecting);assert(radio.ssid=="Home"&&radio.password=="good-password");
 radio.up=true;reboot.tick(18001);radio.up=false;reboot.tick(18002);assert(reboot.state==WifiState::Portal&&radio.ap);
 assert(reboot.reset());assert(mem.get("wifi").empty());
 mem.data["wifi"]="90:broken";reboot.begin(20000);assert(reboot.state==WifiState::Portal);
 mem.writable=false;assert(reboot.submit("Home","pass",21000));radio.up=true;reboot.tick(21001);assert(reboot.state==WifiState::Portal);assert(reboot.message.find("lưu")!=Str::npos);
 Wifi wrap(mem,radio,"CuaRobot-A01F");mem.writable=true;mem.data.clear();wrap.begin(UINT32_MAX-10000);assert(wrap.submit("A","",UINT32_MAX-10000));wrap.tick(4999);assert(wrap.state==WifiState::Portal);
}
void commandTests(){
 Fixture f;
 assert(f.robot.isReady()&&!f.robot.moving()&&!f.robot.light);
 assert(f.move("forward").status==200&&f.robot.moving());f.robot.tick(3099);assert(f.robot.moving());f.robot.tick(3100);assert(!f.robot.moving());
 assert(f.move("back",2,3200).status==200);f.robot.network(false);assert(!f.robot.moving());assert(f.move("back",3,3210).status==409);
 f.robot.network(true);assert(f.move("left",4,3300).status==200);
 assert(f.post("/api/stop",{{"client","phone"},{"seq","6"}}).status==200);assert(!f.robot.moving());assert(f.move("left",5,3400).status==409);assert(f.move("left",7,3400).status==200);
 assert(f.post("/api/move",{{"client","other"},{"seq","1"},{"dir","forward"}},3410).status==409);
 assert(f.move("bad",8,3420).status==400);assert(f.post("/api/move",{{"client","phone"},{"seq","-1"},{"dir","left"}}).status==400);
 assert(f.api.handle({"GET","/api/move",{}},3500).status==405);
 f.post("/api/assembly",{{"op","enter"}});assert(!f.robot.moving()&&f.robot.assembly);assert(f.move("forward",9).status==409);
 f.post("/api/assembly",{{"op","exit"}});assert(!f.robot.moving());assert(f.move("forward",10).status==200);
 f.robot.hardwareFault();assert(!f.robot.moving());assert(f.move("forward",11).status==409);
 auto light=f.post("/api/light",{{"on","1"}});assert(light.status==200&&!f.robot.light);
 auto status=f.api.handle({"GET","/api/status",{}},4000);assert(status.status==200&&status.body.find("not-echoed")==Str::npos);
 Fixture g;assert(g.post("/api/wifi",{{"ssid","Home"},{"password","UNIQUE_SECRET"}}).body.find("UNIQUE_SECRET")==Str::npos);
 assert(g.api.handle({"GET","/api/status",{}},5000).body.find("UNIQUE_SECRET")==Str::npos);
}
void assemblyTests(){
 Fixture f;assert(f.post("/api/trim",{{"ch","0"},{"delta","1"}}).status==400);
 f.post("/api/assembly",{{"op","enter"}});for(int i=0;i<25;i++)assert(f.post("/api/trim",{{"ch","0"},{"delta","1"}}).status==200);assert(f.robot.trim[0]==15);
 for(int i=0;i<40;i++)f.post("/api/trim",{{"ch","7"},{"delta","-1"}});assert(f.robot.trim[7]==-15);
 assert(f.post("/api/trim",{{"ch","8"},{"delta","1"}}).status==400);assert(f.post("/api/trim",{{"ch","0"},{"delta","999"}}).status==400);
 assert(f.post("/api/assembly",{{"op","save"}}).status==200);
 Robot reboot(f.store);reboot.begin(0);assert(reboot.trim[0]==15&&reboot.trim[7]==-15);
 f.post("/api/assembly",{{"op","center"}});for(uint32_t t=2300;t<10000;t+=10)f.robot.tick(t);for(float a:f.robot.angle)assert(std::fabs(a-90)<.01);
 f.post("/api/trim",{{"ch","2"},{"delta","1"}});assert(!f.robot.rawCenter);
 f.post("/api/assembly",{{"op","reset"}});for(int t:f.robot.trim)assert(t==0);
 f.store.writable=false;assert(f.post("/api/assembly",{{"op","save"}}).status==409);
 f.store.data["t0"]="garbage";f.store.data["t7"]="10000";reboot.begin(0);assert(reboot.trim[0]==0&&reboot.trim[7]==0);
}
void startupBootTests(){
 Memory mem;Robot robot(mem);robot.begin(1000);assert(robot.enabledCount()==0);
 for(int i=0;i<8;i++){robot.tick(1000+i*300);assert(robot.enabledCount()==i+1);assert(robot.isReady()==(i==7));assert(!robot.moving());}
 BootHold b;assert(!b.update(true,100));assert(b.remaining(7100)==1);assert(!b.update(true,8099));assert(b.update(true,8100));assert(!b.update(true,9000));b.update(false,9001);assert(!b.update(true,10000));assert(b.update(true,18000));
 BootHold c;assert(!c.update(true,UINT32_MAX-3999));assert(c.update(true,4000));
 uint32_t n;assert(!unsignedNumber("4294967296",n)&&unsignedNumber("4294967295",n));
 assert(jsonString("\"\\\n")=="\"\\\"\\\\\\u000a\"");
}
void gaitTests(){
 // Independent case geometry: larger pulses lower FL/RR, raise FR/RL.
 // Positive gait knee angles must raise feet after the servo sign conversion.
 constexpr int kneePulseUp[4]={-1,1,1,-1};
 const char* names[]={"forward","back","left","right","fl","fr","bl","br"};
 for(int direction=1;direction<=8;direction++){
  auto wanted=directionVector(Direction(direction));float bx=0,by=0;
  constexpr float offsets[4]={0,.5f,.75f,.25f},sx[4]={1,1,-1,-1},sy[4]={1,-1,1,-1};
  constexpr int samples=3200;
  for(int n=0;n<samples;n++){
   float phase=float(n)/samples;auto a=gait(Direction(direction),phase),b=gait(Direction(direction),phase+1.f/samples);
   for(int leg=0;leg<4;leg++){
    float p=phase-offsets[leg];p-=std::floor(p);if(p<.25f)continue;
    float dq=b[leg*2]-a[leg*2];bx+=sy[leg]*dq;by-=sx[leg]*dq;
   }
  }
  float along=bx*wanted.x+by*wanted.y,cross=bx*wanted.y-by*wanted.x;
  assert(along>1&&std::fabs(cross)<.05*along);
 }

 for(const char* name:names){
  Direction dir;assert(parseDirection(name,dir));auto v=directionVector(dir);assert(std::fabs(v.x*v.x+v.y*v.y-1)<.0001);
  Fixture f;auto old=f.robot.angle;float oldVelocity[8]={},peakLiftUs[4]={};unsigned seq=0;int maximumFast=0;
  for(uint32_t t=2210;t<2210+3*cfg::gaitPeriodMs;t+=10){
   if(t%200==10)assert(f.move(name,++seq,t).status==200);
   f.robot.tick(t);int fast=0;
   for(int i=0;i<8;i++){
    float vel=(f.robot.angle[i]-old[i])*100;
    assert(f.robot.angle[i]>=65&&f.robot.angle[i]<=115);
    assert(std::fabs(vel)<=cfg::swingRate+.05);
    assert(std::fabs(vel-oldVelocity[i])<=cfg::acceleration*.01+.12);
    if(std::fabs(vel)>10)fast++;
    old[i]=f.robot.angle[i];oldVelocity[i]=vel;
   }
   assert(fast<=4);maximumFast=std::max(maximumFast,fast);
   for(int leg=0;leg<4;leg++){
    float liftUs=(f.robot.angle[leg*2+1]-90)*cfg::pulseUsPerDegree*kneePulseUp[leg];
    assert(liftUs>=-1); // No commanded swing may push a foot below neutral.
    peakLiftUs[leg]=std::max(peakLiftUs[leg],liftUs);
   }
   auto target=gait(dir,float(t%cfg::gaitPeriodMs)/cfg::gaitPeriodMs);int lifted=0;
   for(int leg=0;leg<4;leg++){
    int knee=leg*2+1;
    float footLift=target[knee]*cfg::signs[knee]*kneePulseUp[leg];
    assert(footLift>=0);
    if(footLift>.001)lifted++;
   }
   assert(lifted<=1);
  }
  for(float lift:peakLiftUs)assert(lift>80); // Every real output lifts, all eight directions.
  f.robot.stop("phone",++seq);for(uint32_t t=27000;t<37000;t+=10)f.robot.tick(t);
  for(float angle:f.robot.angle)assert(std::fabs(angle-90)<.01);
  std::cout<<name<<": max >10deg/s joints="<<maximumFast<<"\n";
 }
 for(int d=1;d<=8;d++){
  auto a=gait(Direction(d),.12f),b=gait(Direction(d),1.12f);for(int i=0;i<8;i++)assert(std::fabs(a[i]-b[i])<.0001);
 }
}
int main(int argc,char** argv){Str group=argc>1?argv[1]:"all";
 if(group=="all"||group=="wifi")wifiTests();
 if(group=="all"||group=="api")commandTests();
 if(group=="all"||group=="assembly")assemblyTests();
 if(group=="all"||group=="boot")startupBootTests();
 if(group=="all"||group=="gait")gaitTests();
 std::cout<<"PASS "<<group<<"\n";
}

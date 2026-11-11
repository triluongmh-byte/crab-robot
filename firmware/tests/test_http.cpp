#include "../crab/core.h"
#include "http_stubs.h"
// Use the exact embedded page served by the device.
#include "../crab/web_ui.h"
#include "../crab/network_http.h"
#include <iostream>
int main(){
 configureHttp();motion.begin(0);
 server.request("/api/session");assert(server.code==200&&motion.session==42);
 clockMs=2200;
 server.request("/api/move",{{"token","42"},{"seq","1"},{"dir","1"},{"fresh","1"}});
 assert(server.code==409&&server.body.find("Servo 360")!=String::npos&&!motion.lease);
 server.request("/api/centre",{{"token","42"}});assert(server.code==409&&!motion.raw);
 server.request("/api/light",{{"token","42"}});assert(server.code==200&&light.on);light.on=false;lightOn=false;
 server.request("/api/assembly",{{"token","42"},{"active","1"}});assert(server.code==200);
 server.request("/api/centre",{{"token","42"}});assert(server.code==409);
 server.request("/api/save",{{"token","42"}});assert(server.code==409&&trimStore.data.empty());
 server.request("/api/trim",{{"token","42"},{"ch","0"},{"delta","1"}});assert(server.code==409);
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200);
 server.request("/api/stand",{{"token","42"}});assert(server.code==409);
 server.request("/api/actuator",{{"token","42"},{"seq","1"},{"value","positional"}});assert(server.code==400);
 server.request("/api/test",{{"token","42"},{"seq","1"},{"active","1"}});assert(server.code==200);
 server.request("/api/test/config",{{"token","42"},{"seq","2"},{"ch","6"},{"neutral","307"}});assert(server.code==200);
 server.request("/api/test/hold",{{"token","42"},{"seq","3"},{"step","4"},{"fresh","1"}});assert(server.code==200&&motion.test.active&&motion.test.counts==311);
 server.request("/api/status");assert(server.body.find("\"requestedCounts\":311")!=String::npos&&server.body.find("\"testChannel\":6")!=String::npos);
 server.request("/api/test/hold",{{"token","42"},{"seq","4"},{"step","21"},{"fresh","1"}});assert(server.code==400);
 server.request("/api/move",{{"token","42"},{"seq","4"},{"dir","0"},{"fresh","0"}});assert(server.code==200&&!motion.test.active);
 server.request("/api/test/hold",{{"token","42"},{"seq","3"},{"step","4"},{"fresh","1"}});assert(server.code==409); // delayed hold after release
 server.request("/api/test",{{"token","42"},{"seq","5"},{"active","0"}});assert(server.code==200);
 server.request("/api/actuator",{{"token","42"},{"seq","6"},{"value","positional"},{"confirm","1"}});assert(server.code==200);
 motion.enabled=8;motion.newSession(42); // existing AP regressions exercise positional control explicitly

 server.request("/api/status");assert(server.code==200&&server.body.find("\"online\":false")!=String::npos);
 driverReady=false;server.request("/api/status");assert(server.code==200&&server.body.find("\"driver\":false")!=String::npos);driverReady=true;
 for(const char* path:{"/","/generate_204","/hotspot-detect.html","/connecttest.txt"}){
  server.request(path);assert(server.code==200&&server.body==WEB_UI);
 }
 server.request("/api/move",{{"token","42"},{"seq","1"},{"dir","1"},{"fresh","1"}});
 assert(server.code==200&&motion.lease&&motion.velocity.x==1); // no STA connection
 server.request("/api/light",{{"token","42"}});assert(server.code==200&&light.on);
 server.request("/api/assembly",{{"token","42"},{"active","1"}});assert(server.code==200&&motion.assembly);
 server.request("/api/centre",{{"token","42"}});assert(server.code==200&&motion.raw);
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200&&!motion.assembly);
 server.request("/api/move",{{"token","42"},{"seq","2"},{"dir","1"},{"fresh","1"}});assert(server.code==200);
 // Loss of STA changes status only; AP command lease survives until the real watchdog expires.
 storedSsid="Saved";network.begin(true,clockMs);WiFi.ssid=storedSsid;WiFi.state=WL_CONNECTED;stationHasIp=true;
 serviceNetwork(clockMs);assert(network.state==crab::NetState::Online);
 stationHasIp=false;WiFi.state=0;serviceNetwork(++clockMs);assert(motion.lease&&motion.velocity.x==1);
 for(int i=0;i<200;i++){serviceNetwork(clockMs+=1000);assert(WiFi.beginCalls==0);}
 // Renew over AP even though saved network is unreachable.
 server.request("/api/move",{{"token","42"},{"seq","3"},{"dir","2"},{"fresh","1"}});assert(server.code==200);
 WiFi.apClients=0;serviceNetwork(clockMs+=30000);assert(WiFi.beginCalls==1);
 WiFi.apClients=1;serviceNetwork(++clockMs);assert(network.state==crab::NetState::Setup);
 assert(WiFi.disconnectCalls>=2);for(int i=0;i<100;i++)serviceNetwork(clockMs+=1000);assert(WiFi.beginCalls==1);
 // A manual scan preempts a background retry instead of returning 18 seconds of busy.
 network.connect(false,clockMs);server.request("/api/scan");assert(server.code==200&&WiFi.scanCalls==1);
 WiFi.scanState=4;server.request("/api/scan");assert(server.code==200&&server.body.find("Other")!=String::npos);
 // Manual credentials can replace an in-flight background or previous manual attempt.
 network.connect(false,clockMs);
 server.request("/api/wifi",{{"ssid","New"},{"password","wrong-password"}});assert(server.code==200&&network.pending);
 server.request("/api/wifi",{{"ssid","Newer"},{"password","wrong-password"}});assert(server.code==200);
 WiFi.state=WL_CONNECT_FAILED;serviceNetwork(clockMs+=1000);
 assert(network.state==crab::NetState::Setup&&!network.pending&&wifiStore.data.empty());
 assert(candidatePass.empty());server.request("/api/status");assert(server.body.find(crab::msg::FAILED)!=String::npos);
 assert(server.body.find("wrong-password")==String::npos);
 server.request("/api/move",{{"token","42"},{"seq","4"},{"dir","3"},{"fresh","1"}});assert(server.code==200);
 server.request("/api/wifi",{{"ssid","Absent"},{"password","private-password"}});assert(server.code==200);
 serviceNetwork(clockMs+=18000);assert(network.state==crab::NetState::Setup&&wifiStore.data.empty());
 server.request("/api/status");assert(server.body.find(crab::msg::FAILED)!=String::npos);
 server.request("/api/wifi",{{"ssid","Good"},{"password","private-password"}});assert(server.code==200);
 WiFi.state=WL_CONNECTED;stationHasIp=true;serviceNetwork(++clockMs);
 assert(network.state==crab::NetState::Online&&wifiStore.data["ssid"]=="Good"&&wifiStore.data["pass"]=="private-password");
 server.request("/api/status");assert(server.body.find("private-password")==String::npos);
 motion.tick(clockMs+501);assert(!motion.lease);
 // Note14 actual routes; every response is checked by Server::send outside Guard.
 motion=crab::Motion{};motion.newSession(42);uint32_t n=0;
 server.request("/api/360",{{"token","42"},{"seq",String(++n)},{"active","1"}});assert(server.code==200&&motion.continuous.opened);
 server.request("/api/360/hold",{{"token","42"},{"seq",String(++n)},{"ch","0"},{"action","1"},{"duration","200"},{"fresh","1"}});assert(server.code==409); // candidates never armed
 for(int ch=0;ch<8;ch++){
  server.request("/api/360/config",{{"token","42"},{"seq",String(++n)},{"ch",String(ch)},{"stop",String(300+ch)},{"forward","347"},{"reverse","267"}});assert(server.code==200&&!motion.continuous.active);
  if(ch==0){server.request("/api/360/viewpoint",{{"token","42"},{"seq",String(++n)},{"value","1"}});assert(server.code==200);}
  for(int dir=1;dir<=2;dir++){server.request("/api/360/calibrate",{{"token","42"},{"seq",String(++n)},{"ch",String(ch)},{"direction",String(dir)},{"counts",dir==1?"347":"267"},{"degrees","10"},{"ms","2000"}});assert(server.code==200&&!motion.continuous.referenceValid&&!motion.continuous.active);}
  server.request("/api/360/reference",{{"token","42"},{"seq",String(++n)},{"confirm","manual90"}});assert(server.code==200&&motion.continuous.referenceValid);
  int offCalls=servos.offCalls;
  server.request("/api/360/hold",{{"token","42"},{"seq",String(++n)},{"ch",String(ch)},{"action","1"},{"duration","200"},{"fresh","1"}});assert(server.code==200&&motion.continuous.counts==347);
  server.request("/api/status");assert(server.body.find("\"continuousRequested\":347")!=String::npos&&server.body.find("\"forward\":347")!=String::npos);
  server.request("/api/360/config",{{"token","42"},{"seq",String(++n)},{"ch",String(ch)},{"stop","320"},{"forward","267"},{"reverse","347"}});assert(server.code==200&&!motion.continuous.active&&servos.offCalls>offCalls);
 }
 for(const char* bad:{"204","410","4294967295","-1","307.5"}){server.request("/api/360/config",{{"token","42"},{"seq",String(++n)},{"ch","0"},{"stop",bad},{"forward","267"},{"reverse","347"}});assert(server.code==400);}
 server.request("/api/360/hold",{{"token","42"},{"seq",String(++n)},{"ch","0"},{"action","1"},{"duration","501"},{"fresh","1"}});assert(server.code==400);
 server.request("/api/360/hold",{{"token","99"},{"seq",String(++n)},{"ch","0"},{"action","1"},{"duration","200"},{"fresh","1"}});assert(server.code==409);
 server.request("/api/360/calibrate",{{"token","42"},{"seq",String(++n)},{"ch","0"},{"direction","1"},{"counts","267"},{"degrees","10"},{"ms","2000"}});assert(server.code==200);
 server.request("/api/360/reference",{{"token","42"},{"seq",String(++n)},{"confirm","manual90"}});assert(server.code==200);
 server.request("/api/360/hold",{{"token","42"},{"seq",String(++n)},{"ch","0"},{"action","1"},{"duration","200"},{"fresh","1"}});assert(server.code==200);
 server.request("/api/move",{{"token","42"},{"seq",String(++n)},{"dir","0"},{"fresh","0"}});assert(server.code==200&&!motion.continuous.active);
 server.request("/api/360/hold",{{"token","42"},{"seq",String(n-1)},{"ch","0"},{"action","1"},{"duration","200"},{"fresh","1"}});assert(server.code==409);
 server.request("/api/centre",{{"token","42"}});assert(server.code==409&&!motion.raw);
 int offCalls=servos.offCalls;server.request("/api/session");assert(server.code==200&&!motion.continuous.opened&&servos.offCalls>offCalls);
 motion=crab::Motion{};motion.newSession(42);assert(motion.openContinuous(true));n=0;
 server.request("/api/360/move",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"direction","1"},{"degrees","60"},{"cap","500"},{"fresh","1"}});assert(server.code==409&&server.body.find("Chưa hiệu chỉnh")!=String::npos);
 server.request("/api/360/reference",{{"token","42"},{"seq",String(++n)},{"confirm","yes"}});assert(server.code==400&&!motion.continuous.referenceValid);
 server.request("/api/360/config",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"stop","307"},{"forward","267"},{"reverse","347"}});assert(server.code==200);
 server.request("/api/360/calibrate",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"direction","1"},{"counts","267"},{"degrees","20"},{"ms","100"}});assert(server.code==200&&!motion.continuous.active);
 server.request("/api/360/move",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"direction","1"},{"degrees","60"},{"cap","500"},{"fresh","1"}});assert(server.code==409&&server.body.find("90°")!=String::npos);
 server.request("/api/360/reference",{{"token","42"},{"seq",String(++n)},{"confirm","manual90"}});assert(server.code==200&&!motion.continuous.active);
 server.request("/api/360/move",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"direction","1"},{"degrees","60"},{"cap","500"},{"fresh","1"}});assert(server.code==200&&server.body.find("\"clipped\":true")!=String::npos&&motion.continuous.duration==175);
 motion.tick(clockMs+100);server.request("/api/status");assert(server.body.find("\"estimated\":20.00")!=String::npos);
 server.request("/api/speed",{{"token","42"},{"value","0.4"}});assert(server.code==200&&!motion.continuous.active&&!motion.continuous.referenceValid);
 server.request("/api/360/move",{{"token","42"},{"seq",String(++n)},{"ch","1"},{"direction","1"},{"degrees","60"},{"cap","501"},{"fresh","1"}});assert(server.code==400);
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": continuous360 routes/config8CH/unconfirmed refusal/count-duration bounds/ordered stop/session-off/HTTP never under mutex; actual HTTP routes, unknown gait/centre/trim/save refusal, RAM-only actuator/test routes, ordered release, AP-only control/light/Ráp/status, captive landing, STA loss independent, saved retries paused, manual scan/preemption, wrong password, NVS success, watchdog\n";
}

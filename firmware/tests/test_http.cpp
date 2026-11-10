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
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<": actual HTTP routes, unknown gait/centre/trim/save refusal, RAM-only actuator/test routes, ordered release, AP-only control/light/Ráp/status, captive landing, STA loss independent, saved retries paused, manual scan/preemption, wrong password, NVS success, watchdog\n";
}

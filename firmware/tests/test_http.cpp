#include "../crab/core.h"
#include "http_stubs.h"
// Use the exact embedded page served by the device.
#include "../crab/web_ui.h"
#include "../crab/network_http.h"
#include <iostream>
int main(){
 configureHttp();motion.begin(0);server.request("/api/session");assert(server.code==200&&motion.session==42);
 clockMs=2200;server.request("/api/status");assert(server.body.find("positional180-v10")!=String::npos&&server.body.find("\"positional\":false")!=String::npos&&server.body.find("\"drive360\":false")!=String::npos&&server.body.find("\"gait\":\"trot\"")!=String::npos);
 // Telemetry must never arm, write, or manufacture measured angles.
 int writes=servos.offCalls;servos.samples[0].known=servos.samples[0].active=true;servos.samples[0].pulseUs=1556;servos.samples[0].counts=319;
 server.request("/api/servos");assert(server.code==200&&servos.offCalls==writes&&!motion.positional());
 assert(server.body.find("\"feedback\":false")!=String::npos&&server.body.find("\"angleDeg\":100.1")!=String::npos);
 assert(server.body.find("\"angleDeg\":null")!=String::npos&&server.body.find("\"counts\":319")!=String::npos);
 servos.samples[0].known=false;server.request("/api/servos");assert(server.body.find("100.1")==String::npos);
 server.request("/api/move",{{"token","42"},{"seq","1"},{"dir","1"},{"fresh","1"}});assert(server.code==409&&!motion.drive.active&&!motion.lease);
 server.request("/api/centre",{{"token","42"}});assert(server.code==409);
 for(const char* path:{"/api/test","/api/test/config","/api/test/hold","/api/360","/api/360/config","/api/360/hold","/api/360/move","/api/360/reference"}){server.request(path,{{"token","42"}});assert(server.code==404);}
 server.request("/api/actuator",{{"token","42"},{"seq","1"},{"value","positional"}});assert(server.code==400);
 server.request("/api/assembly",{{"token","42"},{"active","1"}});assert(server.code==200);
 server.request("/api/actuator",{{"token","42"},{"seq","1"},{"value","positional"},{"confirm","1"}});assert(server.code==200&&motion.positional()&&motion.assembly&&motion.enabled==0);
 server.request("/api/centre",{{"token","42"}});assert(server.code==200&&motion.raw);
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200);
 server.request("/api/gait",{{"token","42"},{"value","walk"}});assert(server.code==400&&motion.gaitPattern==crab::Pattern::Trot);
 server.request("/api/gait",{{"token","7"},{"value","pairs"}});assert(server.code==409&&motion.gaitPattern==crab::Pattern::Trot);
 server.request("/api/gait",{{"token","42"},{"value","pairs"}});assert(server.code==200&&motion.gaitPattern==crab::Pattern::Pairs&&!motion.lease&&motion.positional()); // stays armed
 server.request("/api/status");assert(server.body.find("\"gait\":\"pairs\"")!=String::npos);
 server.request("/api/gait",{{"token","42"},{"value","flick"}});assert(server.code==200&&motion.gaitPattern==crab::Pattern::Flick);server.request("/api/status");assert(server.body.find("\"gait\":\"flick\"")!=String::npos);
 server.request("/api/gait",{{"token","42"},{"value","trot"}});assert(server.code==200&&motion.gaitPattern==crab::Pattern::Trot);
 server.request("/api/move",{{"token","42"},{"seq","2"},{"dir","1"},{"fresh","1"}});assert(server.code==409); // not enabled8 yet
 for(int ch=0;ch<8;ch++)motion.tick(clockMs+20+300*ch);
 motion.newSession(42);assert(motion.enabled==8);
 server.request("/api/status");assert(server.code==200&&server.body.find("\"online\":false")!=String::npos);
 driverReady=false;server.request("/api/status");assert(server.code==200&&server.body.find("\"driver\":false")!=String::npos);driverReady=true;
 for(const char* path:{"/","/generate_204","/hotspot-detect.html","/connecttest.txt"}){
  server.request(path);assert(server.code==200&&server.body==WEB_UI);
 }
 // Emotion studio: page, pose validation/lease, LED colour, saved list.
 server.request("/emo");assert(server.code==200&&server.body==EMOTE_UI);
 const char* poseA="10,-20,-10,-20,10,-20,-10,-20";
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","1"},{"ms","300"},{"a","1,2,3"}});assert(server.code==400&&!motion.posing);
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","1"},{"ms","300"},{"a","1,2,3,4,5,6,7,99"}});assert(server.code==400);
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","1"},{"ms","300"},{"a","1,2,3,4,5,6,7,8x"}});assert(server.code==400);
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","1"},{"ms","9000"},{"a",poseA}});assert(server.code==400);
 server.request("/api/pose",{{"token","7"},{"seq","1"},{"fresh","1"},{"ms","300"},{"a",poseA}});assert(server.code==409&&!motion.posing);
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","1"},{"ms","300"},{"a",poseA}});assert(server.code==200&&motion.posing&&motion.pose[1]==-20&&motion.lease);
 server.request("/api/pose",{{"token","42"},{"seq","1"},{"fresh","0"},{"ms","0"},{"a",poseA}});assert(server.code==409); // replayed sequence
 server.request("/api/pose",{{"token","42"},{"seq","2"},{"fresh","0"},{"ms","0"},{"a",poseA}});assert(server.code==200&&motion.posing);
 server.request("/api/move",{{"token","42"},{"seq","3"},{"dir","0"},{"fresh","0"}});assert(server.code==200&&!motion.posing&&motion.relaxing);
 server.request("/api/led",{{"token","42"},{"r","300"},{"g","0"},{"b","0"}});assert(server.code==400);
 server.request("/api/led",{{"token","7"},{"r","255"},{"g","0"},{"b","0"}});assert(server.code==409);
 server.request("/api/led",{{"token","42"},{"r","255"},{"g","64"},{"b","0"}});assert(server.code==200&&light.r==255&&light.g==64&&light.b==0&&lightOn);
 server.request("/api/led",{{"token","42"},{"r","0"},{"g","0"},{"b","0"}});assert(server.code==200&&!lightOn);
 server.request("/api/emotions");assert(server.code==200&&server.body=="[]");
 server.request("/api/emotions/save",{{"token","42"},{"data","{\"n\":1}"}});assert(server.code==400);
 server.request("/api/emotions/save",{{"token","42"},{"data","[\"a\nb\"]"}});assert(server.code==400);
 server.request("/api/emotions/save",{{"token","42"},{"data",String(3801,'[')}});assert(server.code==400);
 server.request("/api/emotions/save",{{"token","7"},{"data","[]"}});assert(server.code==409);
 server.request("/api/emotions/save",{{"token","42"},{"data","[{\"n\":\"Vui\"}]"}});assert(server.code==200);
 server.request("/api/emotions");assert(server.code==200&&server.body=="[{\"n\":\"Vui\"}]");
 motion.newSession(42);
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
 server.request("/api/move",{{"token","42"},{"seq","50"},{"dir","0"},{"fresh","0"}});assert(server.code==200);
 server.request("/api/move",{{"token","42"},{"seq","49"},{"dir","1"},{"fresh","1"}});assert(server.code==409&&!motion.lease);
 int off=servos.offCalls;server.request("/api/actuator",{{"token","42"},{"seq","51"},{"value","unknown"}});assert(server.code==200&&!motion.positional()&&servos.offCalls>off);
 server.request("/api/move",{{"token","42"},{"seq","52"},{"dir","1"},{"fresh","1"}});assert(server.code==409&&!motion.drive.active);
 server.request("/api/assembly",{{"token","42"},{"active","1"}});assert(server.code==200&&motion.assembly);
 server.request("/api/actuator",{{"token","42"},{"seq","53"},{"value","positional"},{"confirm","1"}});assert(server.code==200&&motion.assembly);
 server.request("/api/actuator",{{"token","42"},{"seq","54"},{"value","unknown"}});assert(server.code==200&&motion.assembly&&!motion.positional());
 server.request("/api/actuator",{{"token","42"},{"seq","55"},{"value","positional"},{"confirm","1"}});assert(server.code==200&&motion.assembly);
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<":180-only HTTP/status/arm/disarm/assembly/centre; removed360 endpoints; sequence release; saved Wi-Fi/AP/QR/scan/errors and credentials preserved; HTTP outside mutex\n";
}

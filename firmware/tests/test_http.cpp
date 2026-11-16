#include <cmath>
#include "../crab/core.h"
#include "../crab/ota.h"
#include "http_stubs.h"
// Use the exact embedded page served by the device.
#include "../crab/web_ui.h"
#include "../crab/network_http.h"
#include <iostream>
int main(){
 configureHttp();motion.begin(0);server.request("/api/session");assert(server.code==200&&motion.session==42);
 clockMs=2200;server.request("/api/status");assert(server.body.find("positional180-v26")!=String::npos&&server.body.find("\"positional\":false")!=String::npos&&server.body.find("\"drive360\":false")!=String::npos&&server.body.find("\"brownoutHold\":false")!=String::npos);
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
 // Trim: fine 1 or coarse 3 deg, no output blanking (epoch unchanged), bad deltas refused.
 {const uint32_t epoch=motion.outputEpoch;const float before=motion.offsets[1];
  server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta","3"}});assert(server.code==200&&motion.offsets[1]==before+3&&!motion.raw&&motion.outputEpoch==epoch);
  server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta","-1"}});assert(server.code==200&&motion.offsets[1]==before+2);
  for(const char* bad:{"2","0","","x","-4"}){server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta",bad}});assert(server.code!=200&&motion.offsets[1]==before+2);}
  server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta","-2"}});assert(server.code==409);
  server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta","-1"}});server.request("/api/trim",{{"token","42"},{"ch","1"},{"delta","-1"}});assert(motion.offsets[1]==before);}
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200);
 // Only the trot is left (v23): the gait and flick-hip endpoints are gone.
 server.request("/api/gait",{{"token","42"},{"value","pairs"}});assert(server.code==404&&motion.positional());
 server.request("/api/flickhip",{{"token","42"},{"value","55"}});assert(server.code==404);
 server.request("/api/status");assert(server.body.find("\"gait\"")==String::npos&&server.body.find("\"flickHip\"")==String::npos&&server.body.find("\"brownoutHold\":false")!=String::npos);
 // Speed slider: decimal fraction .2-1, default .9; malformed or out-of-range refused.
 assert(std::fabs(crab::Motion{}.speed-.9f)<1e-6f);
 server.request("/api/speed",{{"token","42"},{"value","0.55"}});assert(server.code==200&&std::fabs(motion.speed-.55f)<1e-4f);
 server.request("/api/speed",{{"token","42"},{"value","1"}});assert(server.code==200&&motion.speed==1.f);
 server.request("/api/speed",{{"token","42"},{"value",".2"}});assert(server.code==200&&std::fabs(motion.speed-.2f)<1e-4f);
 for(const char* bad:{"0.1","1.5","","abc","0.5.5","-0.5","0.900001","nan"}){server.request("/api/speed",{{"token","42"},{"value",bad}});assert(server.code==400&&std::fabs(motion.speed-.2f)<1e-4f);}
 server.request("/api/speed",{{"token","7"},{"value","0.9"}});assert(server.code==409);
 // Heading trim: signed percent -30..30, persisted, in status.
 server.request("/api/balance",{{"token","42"},{"value","-12"}});assert(server.code==200&&motion.balance==-12&&trimStore.getInt("balance",0)==-12);
 server.request("/api/balance",{{"token","42"},{"value","15"}});assert(server.code==200&&motion.balance==15&&trimStore.getInt("balance",0)==15);
 for(const char* bad:{"31","-31","","abc","1.5","--3","-"}){server.request("/api/balance",{{"token","42"},{"value",bad}});assert(server.code==400&&motion.balance==15&&trimStore.getInt("balance",0)==15);}
 server.request("/api/balance",{{"token","7"},{"value","0"}});assert(server.code==409&&motion.balance==15);
 server.request("/api/status");assert(server.body.find("\"balance\":15")!=String::npos);
 server.request("/api/balance",{{"token","42"},{"value","0"}});assert(server.code==200&&motion.balance==0);
 server.request("/api/knee",{{"token","42"},{"value","55"}});assert(server.code==200&&motion.kneeLift==55&&trimStore.getInt("knee",0)==55);
 for(const char* bad:{"19","61","","x","-30"}){server.request("/api/knee",{{"token","42"},{"value",bad}});assert(server.code==400&&motion.kneeLift==55);}
 server.request("/api/knee",{{"token","7"},{"value","40"}});assert(server.code==409&&motion.kneeLift==55);
 server.request("/api/status");assert(server.body.find("\"knee\":55")!=String::npos);
 server.request("/api/move",{{"token","42"},{"seq","2"},{"dir","1"},{"fresh","1"}});assert(server.code==409); // not enabled8 yet
 for(int ch=0;ch<8;ch++)motion.tick(clockMs+20+300*ch);
 motion.newSession(42);assert(motion.enabled==8);
 server.request("/api/status");assert(server.code==200&&server.body.find("\"online\":false")!=String::npos&&server.body.find("\"rssi\":null")!=String::npos); // no station: no signal reading
 driverReady=false;server.request("/api/status");assert(server.code==200&&server.body.find("\"driver\":false")!=String::npos);driverReady=true;
 for(const char* path:{"/","/generate_204","/hotspot-detect.html","/connecttest.txt"}){
  server.request(path);assert(server.code==200&&server.body==String((const char*)WEB_UI_GZ,WEB_UI_GZ_LEN)&&server.headers["Content-Encoding"]=="gzip"&&server.headers["Cache-Control"]=="no-store");
  assert(WEB_UI_GZ_LEN<sizeof(WEB_UI)/2&&WEB_UI_GZ[0]==0x1f&&WEB_UI_GZ[1]==0x8b); // gzip, well under half the page
 }
 // Emotion studio: page, pose validation/lease, LED colour, saved list.
 server.request("/emo");assert(server.code==200&&server.body==String((const char*)EMOTE_UI_GZ,EMOTE_UI_GZ_LEN)&&server.headers["Content-Encoding"]=="gzip"&&EMOTE_UI_GZ_LEN<sizeof(EMOTE_UI)/2);
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
 assert(server.code==200&&motion.lease&&motion.velocity.x==crab::bodyDirection(1).x); // no STA connection; Forward heads to CH4/CH6
 server.request("/api/light",{{"token","42"}});assert(server.code==200&&lightOn&&light.r==255&&light.g==255&&light.b==255);
 // Lamp colour beside the light button: saved hex, turns the lamp on, toggle keeps it.
 server.request("/api/lightcolor",{{"token","42"},{"value","ff8000"}});assert(server.code==200&&lightOn&&light.r==255&&light.g==128&&light.b==0&&trimStore.getInt("led",0)==0xff8000);
 server.request("/api/status");assert(server.body.find("\"lightColor\":\"#ff8000\"")!=String::npos);
 server.request("/api/light",{{"token","42"}});assert(!lightOn&&light.r==0&&light.g==0&&light.b==0);
 server.request("/api/light",{{"token","42"}});assert(lightOn&&light.r==255&&light.g==128&&light.b==0);
 for(const char* bad:{"","fff","gg0000","#ff0000","ff00001"}){server.request("/api/lightcolor",{{"token","42"},{"value",bad}});assert(server.code==400&&trimStore.getInt("led",0)==0xff8000);}
 server.request("/api/lightcolor",{{"token","7"},{"value","00ff00"}});assert(server.code==409&&light.g==128);
 server.request("/api/lightcolor",{{"token","42"},{"value","FFFFFF"}});assert(server.code==200&&light.b==255);
 // Eyes follow the lamp: the saved colour, or an emotion's colour while it runs.
 assert(shownRgb==0xffffff&&!ledOverride);
 server.request("/api/led",{{"token","42"},{"r","32"},{"g","80"},{"b","255"}});assert(server.code==200&&shownRgb==0x2050ff&&ledOverride);
 applyLight();assert(shownRgb==0xffffff&&!ledOverride&&light.r==255);
 server.request("/api/eyes",{{"token","42"},{"mood","sad"}});assert(server.code==200&&emoteMood==crab::Mood::Sad);
 for(const char* bad:{"","SAD","sadd","happy1","normalnormalx"}){server.request("/api/eyes",{{"token","42"},{"mood",bad}});assert(server.code==400&&emoteMood==crab::Mood::Sad);}
 server.request("/api/eyes",{{"token","7"},{"mood","happy"}});assert(server.code==409&&emoteMood==crab::Mood::Sad);
 server.request("/api/eyes",{{"token","42"},{"mood","normal"}});assert(server.code==200&&emoteMood==crab::Mood::Normal);
 server.request("/api/assembly",{{"token","42"},{"active","1"}});assert(server.code==200&&motion.assembly);
 server.request("/api/centre",{{"token","42"}});assert(server.code==200&&motion.raw);
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200&&!motion.assembly);
 server.request("/api/move",{{"token","42"},{"seq","2"},{"dir","1"},{"fresh","1"}});assert(server.code==200);
 // Slanted buttons 5..8 walk forward/back while turning.
 server.request("/api/move",{{"token","42"},{"seq","20"},{"dir","5"},{"fresh","1"}});assert(server.code==200&&motion.yaw>0&&motion.velocity.x==crab::bodyDirection(1).x&&motion.dir==5);
 server.request("/api/move",{{"token","42"},{"seq","21"},{"dir","8"},{"fresh","1"}});assert(server.code==200&&motion.yaw>0&&motion.velocity.x==crab::bodyDirection(2).x);
 server.request("/api/move",{{"token","42"},{"seq","22"},{"dir","9"},{"fresh","1"}});assert(server.code==400);
 server.request("/api/move",{{"token","42"},{"seq","23"},{"dir","1"},{"fresh","1"}});assert(server.code==200&&motion.yaw==0);
 // Auto mode: refused without both sensors, a wrong token or unarmed servos;
 // status reports it; a manual move or STOP takes over.
 server.request("/api/status");assert(server.body.find("\"auto\":false")!=String::npos&&server.body.find("\"sonarOk\":false")!=String::npos&&server.body.find("\"sonar\":[null,null]")!=String::npos&&server.body.find("\"autoNote\":null")!=String::npos);
 assert(server.body.find(cfg::INTEGRATED_BOARD?"\"autoSupported\":false":"\"autoSupported\":true")!=String::npos);
 server.request("/api/auto",{{"token","42"},{"active","1"}});assert(server.code==409&&!autopilot.active()&&!motion.autoMode&&server.body.find("cảm biến siêu âm")!=String::npos);
 for(int i=0;i<3;i++){sonar.side[0].add(120,clockMs);sonar.side[1].add(crab::SONAR_FAR_CM,clockMs);}
 server.request("/api/auto",{{"token","7"},{"active","1"}});assert(server.code==409&&!autopilot.active());
 for(const char* bad:{"2","","x"}){server.request("/api/auto",{{"token","42"},{"active",bad}});assert(server.code==400&&!autopilot.active());}
 server.request("/api/auto",{{"token","42"},{"active","1"}});assert(server.code==200&&autopilot.active()&&motion.autoMode&&motion.velocity.x==0);
 server.request("/api/status");assert(server.body.find("\"auto\":true")!=String::npos&&server.body.find("\"autoState\":\"cruise\"")!=String::npos&&server.body.find("\"sonar\":[120,400]")!=String::npos&&server.body.find("\"sonarOk\":true")!=String::npos);
 server.request("/api/move",{{"token","42"},{"seq","24"},{"dir","2"},{"fresh","1"}});assert(server.code==200&&!motion.autoMode&&motion.dir==2);
 autopilot.stop(clockMs,crab::automsg::MANUAL); // what the loop's serviceAuto does next
 server.request("/api/status");assert(server.body.find("\"auto\":false")!=String::npos&&server.body.find(crab::automsg::MANUAL)!=String::npos);
 server.request("/api/auto",{{"token","42"},{"active","1"}});assert(server.code==200&&motion.autoMode);
 server.request("/api/auto",{{"token","42"},{"active","0"}});assert(server.code==200&&!autopilot.active()&&!motion.autoMode&&!motion.lease);
 server.request("/api/assembly",{{"token","42"},{"active","1"}});server.request("/api/auto",{{"token","42"},{"active","1"}});assert(server.code==409&&!autopilot.active()&&!motion.autoMode);
 server.request("/api/assembly",{{"token","42"},{"active","0"}});assert(server.code==200);
 clockMs+=cfg::SONAR_STALE_MS;server.request("/api/auto",{{"token","42"},{"active","1"}});assert(server.code==409&&!autopilot.active());
 server.request("/api/status");assert(server.body.find("\"sonar\":[null,null]")!=String::npos);
 server.request("/api/move",{{"token","42"},{"seq","25"},{"dir","1"},{"fresh","1"}});assert(server.code==200);
 // Loss of STA changes status only; AP command lease survives until the real watchdog expires.
 storedSsid="Saved";network.begin(true,clockMs);WiFi.ssid=storedSsid;WiFi.state=WL_CONNECTED;stationHasIp=true;
 serviceNetwork(clockMs);assert(network.state==crab::NetState::Online);
 server.request("/api/status");assert(server.body.find("\"rssi\":-67")!=String::npos);
 stationHasIp=false;WiFi.state=0;serviceNetwork(++clockMs);assert(motion.lease&&motion.velocity.x==crab::bodyDirection(1).x);
 for(int i=0;i<200;i++){serviceNetwork(clockMs+=1000);assert(WiFi.beginCalls==0);}
 // Renew over AP even though saved network is unreachable.
 server.request("/api/move",{{"token","42"},{"seq","26"},{"dir","2"},{"fresh","1"}});assert(server.code==200);
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
 // A wrong password reports two auth failures (one retry), then fails.
 {const int begins=WiFi.beginCalls;staFail=uint8_t(crab::WifiFail::Auth);serviceNetwork(clockMs+=1000);assert(network.state==crab::NetState::Connecting&&WiFi.beginCalls==begins+1&&WiFi.ssid=="Newer");}
 staFail=uint8_t(crab::WifiFail::Auth);serviceNetwork(clockMs+=1000);
 assert(network.state==crab::NetState::Setup&&!network.pending&&wifiStore.data.empty());
 assert(candidatePass.empty());server.request("/api/status");assert(server.body.find(crab::msg::WRONG_PASS)!=String::npos);
 assert(server.body.find("wrong-password")==String::npos);
 server.request("/api/move",{{"token","42"},{"seq","27"},{"dir","3"},{"fresh","1"}});assert(server.code==200);
 server.request("/api/wifi",{{"ssid","Absent"},{"password","private-password"}});assert(server.code==200);
 serviceNetwork(clockMs+=18000);assert(network.state==crab::NetState::Setup&&wifiStore.data.empty());
 server.request("/api/status");assert(server.body.find(crab::msg::FAILED)!=String::npos);
 // Owner, 2026-11-14: at home after the office Wi-Fi was not found, WiFi.status()
 // still read NO_SSID_AVAIL from that old attempt. Kết nối must not fail (and
 // disconnect) the new join on that stale value 0.5 s later.
 server.request("/api/wifi",{{"ssid","Good"},{"password","private-password"}});assert(server.code==200);
 {const int drops=WiFi.disconnectCalls;WiFi.state=WL_NO_SSID_AVAIL;
  for(int i=0;i<5;i++){serviceNetwork(clockMs+=600);assert(network.state==crab::NetState::Connecting&&network.pending&&WiFi.disconnectCalls==drops);}
  // A real "not found" from this attempt scans again instead of giving up.
  const int begins=WiFi.beginCalls;staFail=uint8_t(crab::WifiFail::NotFound);serviceNetwork(clockMs+=600);
  assert(network.state==crab::NetState::Connecting&&WiFi.beginCalls==begins+1&&WiFi.ssid=="Good"&&staFail==0);}
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
 // OTA (v24): marker scan, PIN on the screen, then the upload.
 {const std::string m=crab::OTA_MARKER;assert(m=="crab-ota-target="+std::string(cfg::HARDWARE_TARGET)+";"&&m.find(m[0],1)==std::string::npos);
  crab::MarkerScan a;const std::string t="xxcrab-ocrab-ota-target="+std::string(cfg::HARDWARE_TARGET)+";yy";for(char c:t)a.feed((const uint8_t*)&c,1);assert(a.found);
  crab::MarkerScan b;const std::string u=m.substr(0,m.size()-1)+"!";b.feed((const uint8_t*)u.data(),u.size());assert(!b.found);
  crab::OtaPin p;assert(!p.shown(0));p.issue(1000,7);assert(p.pin==100007&&p.shown(1000+crab::OTA_PIN_MS-1)&&!p.shown(1000+crab::OTA_PIN_MS));
  assert(!p.take(100008,2000)&&!p.take(100007,2000)); // one wrong guess burns it
  p.issue(0,899999);assert(p.pin==999999&&p.take(999999,5)&&!p.take(999999,6));}
 {std::string img(6000,'\x11');img[0]='\xE9';img.replace(1430,sizeof(crab::OTA_MARKER)-1,crab::OTA_MARKER); // marker spans two chunks
  std::string other(6000,'\x11');other[0]='\xE9';
  const uint32_t t0=clockMs;
  // Upload without a PIN, or with a non-owner token: refused before flash is touched.
  server.uploadFile("/api/ota",{{"token","42"},{"pin","123456"}},img);assert(server.code==403&&!Update.switched&&Update.written.empty());
  server.request("/api/ota/begin",{{"token","7"}});assert(server.code==409&&!otaPin.shown(clockMs));
  server.request("/api/ota/begin",{{"token","42"}});assert(server.code==200&&otaPin.shown(clockMs)&&server.body.find("\"seconds\":120")!=String::npos&&server.body.find("\"pin\"")==String::npos); // own open AP: screen only
  {const auto keep=network.state;network.state=crab::NetState::Online;server.cl.local={"192.168.1.2"};
   server.request("/api/ota/begin",{{"token","42"}});assert(server.code==200&&server.body.find("\"pin\":\""+std::to_string(otaPin.pin)+"\"")!=String::npos); // home Wi-Fi: returned
   server.cl.local={"192.168.4.1"};server.request("/api/ota/begin",{{"token","42"}});assert(server.body.find("\"pin\"")==String::npos); // AP client while online: still screen only
   network.state=keep;server.request("/api/status");assert(server.body.find("\"updateHold\":false")!=String::npos);}
  server.request("/api/status");assert(server.body.find("\"otaPin\":true")!=String::npos&&server.body.find(std::to_string(otaPin.pin))==String::npos&&server.body.find("\"slot\":\"app0\"")!=String::npos&&server.body.find(crab::OTA_MARKER)!=String::npos);
  const std::string pin=std::to_string(otaPin.pin);
  server.uploadFile("/api/ota",{{"token","7"},{"pin",pin}},img);assert(server.code==409&&!Update.switched&&otaPin.shown(clockMs)); // wrong owner does not burn the PIN
  server.uploadFile("/api/ota",{{"token","42"},{"pin","100000"}},img);assert(server.code==403&&!otaPin.shown(clockMs)); // a wrong PIN burns it
  server.uploadFile("/api/ota",{{"token","42"},{"pin",pin}},img);assert(server.code==403&&!Update.switched);
  // Expired PIN.
  server.request("/api/ota/begin",{{"token","42"}});clockMs+=crab::OTA_PIN_MS;
  server.uploadFile("/api/ota",{{"token","42"},{"pin",std::to_string(otaPin.pin)}},img);assert(server.code==403&&!Update.switched);
  // Not a crab image for this board: written, then refused before the boot slot switches.
  server.request("/api/actuator",{{"token","42"},{"seq","60"},{"value","positional"},{"confirm","1"}});assert(server.code==200&&motion.positional());
  int aborts=Update.aborts;server.request("/api/ota/begin",{{"token","42"}});
  server.uploadFile("/api/ota",{{"token","42"},{"pin",std::to_string(otaPin.pin)}},other);assert(server.code==400&&server.body.find("không phải firmware")!=String::npos&&!Update.switched&&Update.aborts==aborts+1&&!motion.positional()&&!restartAt);
  // Client drops mid-upload: aborted, old firmware stays.
  server.request("/api/ota/begin",{{"token","42"}});server.uploadFile("/api/ota",{{"token","42"},{"pin",std::to_string(otaPin.pin)}},img,1436,true);assert(!Update.switched&&!Update.running&&Update.aborts==aborts+2&&!restartAt);
  // Flash write error.
  Update.failWrite=true;server.request("/api/ota/begin",{{"token","42"}});server.uploadFile("/api/ota",{{"token","42"},{"pin",std::to_string(otaPin.pin)}},img);assert(server.code==500&&!Update.switched);Update.failWrite=false;
  // Success: servos off, Tự đi ended, exact bytes written, slot switched, restart scheduled after the reply.
  server.request("/api/actuator",{{"token","42"},{"seq","61"},{"value","positional"},{"confirm","1"}});assert(server.code==200&&motion.positional());
  server.request("/api/ota/begin",{{"token","42"}});server.uploadFile("/api/ota",{{"token","42"},{"pin",std::to_string(otaPin.pin)}},img,1000);
  assert(server.code==200&&server.body.find("\"restarting\":true")!=String::npos&&Update.switched&&Update.written==img&&!motion.positional()&&restartAt&&!otaPin.shown(clockMs));
  (void)t0;}
 std::cout<<"PASS "<<cfg::HARDWARE_TARGET<<":180-only HTTP/status/arm/disarm/assembly/centre; removed360 endpoints; sequence release; saved Wi-Fi/AP/QR/scan/errors and credentials preserved; HTTP outside mutex; Auto mode sensors/token/arming/status/manual takeover; gzip pages, RSSI; OTA PIN returned only over station Wi-Fi; OTA marker scan/PIN issue-expiry-burn/owner/target refusal/drop/write error/success\n";
}

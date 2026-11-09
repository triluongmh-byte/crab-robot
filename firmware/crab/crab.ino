// SPDX-License-Identifier: GPL-3.0-or-later
#include <Arduino.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <Preferences.h>
#include <atomic>
#include "core.h"
#include "drivers.h"
#include "display.h"
#include "web_ui.h"
WebServer server(80);DNSServer dns;
Preferences wifiStore,trimStore;
crab::Motion motion;crab::Network network;crab::HoldButton boot;
ServoDriver servos;LightDriver light;Screen screen;
SemaphoreHandle_t motionLock;
std::atomic<bool> driverReady(false);
std::atomic<bool> eraseHold(false),stationHasIp(false);
String ap,storedSsid,storedPass,candidateSsid,candidatePass;
bool lightOn=false,displayOk=false;
uint32_t lastDraw=0;String drawnKey;
struct Guard{Guard(){xSemaphoreTake(motionLock,portMAX_DELAY);}~Guard(){xSemaphoreGive(motionLock);}};
String jsonString(const String& s){String out="\"";for(size_t i=0;i<s.length();i++){unsigned char c=s[i];if(c=='"'||c=='\\'){out+='\\';out+=char(c);}else if(c<32){char b[7];snprintf(b,sizeof(b),"\\u%04x",c);out+=b;}else out+=char(c);}return out+"\"";}
void json(int code,const String& s){server.sendHeader("Cache-Control","no-store");server.sendHeader("X-Content-Type-Options","nosniff");server.send(code,"application/json; charset=utf-8",s);}
void ok(){json(200,"{\"ok\":true}");}
void error(int code=400){json(code,"{\"error\":\"Lệnh chưa hợp lệ hoặc chưa sẵn sàng\"}");}
bool uintArg(const char* name,uint32_t& value){String s=server.arg(name);if(s.length()==0||s.length()>10)return false;uint64_t v=0;for(char c:s){if(c<'0'||c>'9')return false;v=v*10+c-'0';if(v>0xffffffffULL)return false;}value=(uint32_t)v;return true;}
bool owns(){uint32_t t;if(!uintArg("token",t))return false;Guard g;return t&&t==motion.session;}
void stopMotion(){Guard g;motion.stop();}
void motionTask(void*){
 float sent[8];for(auto& p:sent)p=cfg::CENTRE_US;
 TickType_t wake=xTaskGetTickCount();
 for(;;){
  int ch=-1,target=1500;bool active=false,first=false;
  {
   Guard g;motion.inhibit=eraseHold.load()||!driverReady.load();
   first=motion.enabled<8;ch=motion.tick(millis());
   if(ch>=0){target=crab::pulse(ch,motion.position[ch],motion.offsets[ch],motion.raw);active=true;}
  }
  if(active&&driverReady.load()){
   // Includes trim and raw-centre commands in the final pulse slew limiter.
   float limit=cfg::SLEW_DPS*.08f*cfg::US_PER_DEG;
   if(first)sent[ch]=target;else sent[ch]+=crab::clamp(target-sent[ch],-limit,limit);
   if(!servos.pulse(ch,int(std::lround(sent[ch])))){driverReady=false;servos.allOff();stopMotion();}
  }
  vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}
void connectStation(const String& ssid,const String& pass){WiFi.disconnect(false,false);stationHasIp=false;WiFi.begin(ssid.c_str(),pass.c_str());}
void configureHttp(){
 server.on("/api/status",HTTP_GET,[]{bool assembly;{Guard g;assembly=motion.assembly;}String url=network.state==crab::NetState::Online?String("http://")+WiFi.localIP().toString()+"/":"http://192.168.4.1/";
  json(200,String("{\"message\":")+jsonString(network.message)+",\"url\":"+jsonString(url)+",\"online\":"+(network.state==crab::NetState::Online?"true":"false")+",\"driver\":"+(driverReady?"true":"false")+",\"assembly\":"+(assembly?"true":"false")+"}");});
 server.on("/api/session",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;{Guard g;motion.newSession(token);}json(200,"{\"token\":\""+String(token)+"\"}");});
 server.on("/api/move",HTTP_POST,[]{uint32_t token,seq,dir,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("dir",dir)||!uintArg("fresh",fresh)||fresh>1||dir>8){error();return;}bool accepted;{Guard g;accepted=motion.command(token,seq,int(dir),millis(),fresh==1);}if(accepted)ok();else error(409);});
 server.on("/api/scan",HTTP_POST,[]{
  if(network.state==crab::NetState::Connecting){json(200,"{\"busy\":true}");return;}
  int n=WiFi.scanComplete();if(n==WIFI_SCAN_FAILED){WiFi.scanNetworks(true);json(200,"{\"busy\":true}");return;}
  if(n==WIFI_SCAN_RUNNING){json(200,"{\"busy\":true}");return;}
  String s="{\"busy\":false,\"networks\":[";int count=0;
  for(int i=0;i<n&&count<30;i++){String name=WiFi.SSID(i);if(name.length()==0)continue;bool dup=false;for(int j=0;j<i;j++)if(WiFi.SSID(j)==name)dup=true;if(dup)continue;if(count++)s+=',';s+=jsonString(name);}s+="]}";WiFi.scanDelete();json(200,s);
 });
 server.on("/api/wifi",HTTP_POST,[]{
  String ssid=server.arg("ssid"),pass=server.arg("password");
  if(ssid.length()<1||ssid.length()>32||pass.length()>63||(pass.length()>0&&pass.length()<8)||network.state==crab::NetState::Connecting){error();return;}
  stopMotion();candidateSsid=ssid;candidatePass=pass;network.connect(true,millis());connectStation(ssid,pass);ok();
 });
 server.on("/api/light",HTTP_POST,[]{if(!owns()){error(409);return;}lightOn=!lightOn;light.set(lightOn);ok();});
 server.on("/api/speed",HTTP_POST,[]{if(!owns()){error(409);return;}String s=server.arg("value");if(s!="0.4"&&s!="0.65"&&s!="1"){error();return;}{Guard g;motion.speed=s.toFloat();}ok();});
 server.on("/api/assembly",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t a;if(!uintArg("active",a)||a>1){error();return;}{Guard g;motion.setAssembly(a);}ok();});
 server.on("/api/centre",HTTP_POST,[]{if(!owns()){error(409);return;}{Guard g;motion.centre();}ok();});
 server.on("/api/stand",HTTP_POST,[]{if(!owns()){error(409);return;}{Guard g;motion.setAssembly(true);}ok();});
 server.on("/api/trim",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t ch;String s=server.arg("delta");if(!uintArg("ch",ch)||ch>7||(s!="-1"&&s!="1")){error();return;}bool accepted;float offset;{Guard g;accepted=motion.trim(ch,s.toInt());offset=motion.offsets[ch];}if(!accepted){error(409);return;}json(200,"{\"offset\":"+String(offset,0)+"}");});
 server.on("/api/save",HTTP_POST,[]{if(!owns()){error(409);return;}float offsets[8];{Guard g;if(!motion.assembly){error(409);return;}memcpy(offsets,motion.offsets,sizeof(offsets));}
  if(trimStore.putBytes("offsets",offsets,sizeof(offsets))!=sizeof(offsets)){error(500);return;}ok();});
 // Captive portal probes (Android/iOS/Windows) all land on our embedded page.
 server.onNotFound([]{if(server.uri().startsWith("/api/")){error(404);return;}server.sendHeader("Cache-Control","no-store");server.send_P(200,"text/html; charset=utf-8",WEB_UI);});
 server.begin();
}
void setup(){
 // No Serial logging, no hardcoded credentials, no hardware discovery.
 servos.inhibit();
 pinMode(cfg::BOOT_PIN,INPUT_PULLUP);
 motionLock=xSemaphoreCreateMutex();
 displayOk=screen.begin();light.begin();driverReady=servos.begin();
 wifiStore.begin("cua-wifi",false);trimStore.begin("cua-trim",false);
 {Guard g;if(trimStore.getBytesLength("offsets")==sizeof(motion.offsets)){trimStore.getBytes("offsets",motion.offsets,sizeof(motion.offsets));for(auto& v:motion.offsets)if(!std::isfinite(v)||std::fabs(v)>cfg::TRIM_LIMIT)v=0;}motion.begin(millis());}
 xTaskCreatePinnedToCore(motionTask,"cua-motion",4096,nullptr,3,nullptr,1);
 WiFi.onEvent([](WiFiEvent_t event){if(event==ARDUINO_EVENT_WIFI_STA_GOT_IP)stationHasIp=true;else if(event==ARDUINO_EVENT_WIFI_STA_DISCONNECTED)stationHasIp=false;});
 WiFi.persistent(false);WiFi.mode(WIFI_AP_STA);WiFi.setAutoReconnect(false);
 ap=crab::apName(uint32_t(ESP.getEfuseMac()>>32)).c_str();
 WiFi.softAPConfig(IPAddress(192,168,4,1),IPAddress(192,168,4,1),IPAddress(255,255,255,0));WiFi.softAP(ap.c_str());
 dns.start(53,"*",IPAddress(192,168,4,1));
 storedSsid=wifiStore.getString("ssid","");storedPass=wifiStore.getString("pass","");network.begin(!storedSsid.isEmpty(),millis());
 if(!storedSsid.isEmpty())connectStation(storedSsid,storedPass);
 configureHttp();
}
void loop(){
 uint32_t now=millis();bool pressed=digitalRead(cfg::BOOT_PIN)==LOW;eraseHold=pressed;
 if(pressed)stopMotion();
 if(boot.tick(pressed,now)){
  stopMotion();wifiStore.clear();storedSsid="";storedPass="";candidateSsid="";candidatePass="";
  WiFi.disconnect(false,false);network.erase(now);drawnKey="";
 }
 bool connected=stationHasIp.load()&&WiFi.status()==WL_CONNECTED&&WiFi.SSID()==(network.pending?candidateSsid:storedSsid);
 bool candidateWas=network.pending;
 network.tick(now,connected,crab::elapsed(now,network.since)>500&&(WiFi.status()==WL_CONNECT_FAILED||WiFi.status()==WL_NO_SSID_AVAIL));
 if(network.saveRequested){
  storedSsid=candidateSsid;storedPass=candidatePass;wifiStore.putString("ssid",storedSsid);wifiStore.putString("pass",storedPass);
  candidatePass="";candidateSsid="";network.saveRequested=false;
 }
 if(candidateWas&&!network.pending&&!connected){candidateSsid="";candidatePass="";WiFi.disconnect(false,false);}
 if(network.retryRequested){connectStation(storedSsid,storedPass);network.retryRequested=false;}
 // A lost station link stops motion, even if the AP is still available.
 static bool wasConnected=false;if(wasConnected&&!connected)stopMotion();wasConnected=connected;
 dns.processNextRequest();server.handleClient();
 if(now-lastDraw>=250){lastDraw=now;String url=network.state==crab::NetState::Online?String("http://")+WiFi.localIP().toString()+"/":"192.168.4.1";
  String message=driverReady?String(network.message):String(crab::msg::DRIVER);String key=url+message;
  if(displayOk&&key!=drawnKey){String payload=network.state==crab::NetState::Online?crab::webQr(WiFi.localIP().toString().c_str()).c_str():crab::wifiQr(ap.c_str()).c_str();if(screen.show(payload.c_str(),message.c_str(),url.c_str(),ap.c_str()))drawnKey=key;}
 }
 delay(1); // RTOS yield; motion and its 500-ms watchdog run independently
}

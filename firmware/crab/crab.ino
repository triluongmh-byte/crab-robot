// SPDX-License-Identifier: GPL-3.0-or-later
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <Adafruit_NeoPixel.h>
#include <atomic>
#include "Robot.h"
#include "Hardware.h"
#include "Display.h"
#include "Web.h"
using namespace crab;
class NvsStorage:public Storage {
 Preferences prefs;
 public:
 bool begin(){return prefs.begin("cua",false);}
 Str get(const Str& key)override{return prefs.getString(key.c_str(),"").c_str();}
 bool put(const Str& key,const Str& value)override{return prefs.putString(key.c_str(),value.c_str())==value.size();}
 bool erase(const Str& key)override{return !prefs.isKey(key.c_str())||prefs.remove(key.c_str());}
} storage;
DNSServer dns;
class EspRadio:public Radio {
 public:
 void accessPoint(const Str& ssid)override{WiFi.mode(WIFI_AP_STA);WiFi.softAPConfig(IPAddress(192,168,4,1),IPAddress(192,168,4,1),IPAddress(255,255,255,0));WiFi.softAP(ssid.c_str());dns.start(53,"*",IPAddress(192,168,4,1));}
 void join(const Str& ssid,const Str& password)override{WiFi.disconnect(false,false);WiFi.begin(ssid.c_str(),password.c_str());}
 void stopAP()override{dns.stop();WiFi.softAPdisconnect(true);WiFi.mode(WIFI_STA);}
 void disconnect()override{WiFi.disconnect(false,false);}
 bool connected()override{return WiFi.status()==WL_CONNECTED;}
 Str address()override{return WiFi.localIP().toString().c_str();}
} radio;
Robot robot(storage);
Wifi* wifi=nullptr;
Api* api=nullptr;
WebServer server(80);
Display display;
Pca pca;
Adafruit_NeoPixel leds(cfg::ledCount,CRAB_LED_PIN,NEO_GRB+NEO_KHZ800);
SemaphoreHandle_t robotMutex;
std::atomic<bool> online{false}, resetPending{false};
std::atomic<int> bootCountdown{-1};
bool nvsOk=false,pcaOk=false;
class Guard {
 public:Guard(){xSemaphoreTake(robotMutex,portMAX_DELAY);}~Guard(){xSemaphoreGive(robotMutex);}
};
void actuatorTask(void*){
 BootHold boot;
 int oldPulse[8]={-1,-1,-1,-1,-1,-1,-1,-1};
 bool oldLight=false;
 TickType_t lastWake=xTaskGetTickCount();
 for(;;){
  uint32_t now=millis();bool down=digitalRead(CRAB_BOOT_PIN)==LOW;
  if(boot.update(down,now))resetPending=true;
  bootCountdown=down?boot.remaining(now):-1;
  std::array<float,8> angles;uint8_t count;bool light,fault;
  {
   Guard guard;robot.network(online.load()&&!down&&!resetPending.load());robot.tick(now);
   angles=robot.angle;count=robot.enabledCount();light=robot.light;fault=robot.isFault();
  }
  if(!fault){
   for(uint8_t index=0;index<count;index++){
    uint8_t ch=cfg::enableOrder[index];int pulse=cfg::pulseNeutralUs+int((angles[ch]-90)*cfg::pulseUsPerDegree);
    if(pulse==oldPulse[ch])continue;
    if(!pca.servo(ch,angles[ch])){pca.allOff();Guard guard;robot.hardwareFault();fault=true;break;}
    oldPulse[ch]=pulse;
   }
  }
  if(fault)light=false;
  if(light!=oldLight){leds.fill(light?leds.Color(255,210,140):0);leds.show();oldLight=light;}
  vTaskDelayUntil(&lastWake,pdMS_TO_TICKS(cfg::motionTickMs));
 }
}
Request request(){
 Request req;req.path=server.uri().c_str();req.method=server.method()==HTTP_GET?"GET":server.method()==HTTP_POST?"POST":"OTHER";
 for(int i=0;i<server.args();i++)req.args[server.argName(i).c_str()]=server.arg(i).c_str();return req;
}
void sendResponse(const Response& response){
 server.sendHeader("Cache-Control","no-store");server.sendHeader("X-Content-Type-Options","nosniff");
 server.send(response.status,response.type.c_str(),response.body.c_str());
}
void handleApi(){
 Request req=request();
 if(req.path=="/api/wifi"){
  online=false;{Guard guard;robot.network(false);}
  // Radio/NVS calls run outside the motion mutex. The 100Hz task keeps stopping.
  sendResponse(api->handle(req,millis()));
 }else{Response response;{Guard guard;response=api->handle(req,millis());}sendResponse(response);}
}
void handleScan(){
 if(wifi->state==WifiState::Connecting){sendResponse({200,"application/json","{\"pending\":true,\"ssids\":[]}"});return;}
 int count=WiFi.scanComplete();
 if(count==WIFI_SCAN_FAILED){WiFi.scanNetworks(true,false,false,100);sendResponse({200,"application/json","{\"pending\":true,\"ssids\":[]}"});return;}
 if(count==WIFI_SCAN_RUNNING){sendResponse({200,"application/json","{\"pending\":true,\"ssids\":[]}"});return;}
 Str body="{\"pending\":false,\"ssids\":[";std::map<Str,bool> seen;bool first=true;
 for(int i=0;i<count;i++){Str ssid=WiFi.SSID(i).c_str();if(ssid.empty()||seen[ssid])continue;seen[ssid]=true;if(!first)body+=",";first=false;body+=jsonString(ssid);}
 body+="]}";WiFi.scanDelete();sendResponse({200,"application/json; charset=utf-8",body});
}
void servePage(){
 if(server.uri()=="/rap"){Guard guard;robot.enterAssembly();}
 server.sendHeader("Cache-Control","no-store");server.send(200,"text/html; charset=utf-8",web::page);
}
void setup(){
 pinMode(CRAB_BOOT_PIN,INPUT_PULLUP);pinMode(CRAB_POWER_ON,OUTPUT);digitalWrite(CRAB_POWER_ON,HIGH);
 // No serial credential output, no wait for a host USB connection.
 robotMutex=xSemaphoreCreateMutex();
 leds.begin();leds.setBrightness(cfg::ledBrightness);leds.clear();leds.show();
 pcaOk=pca.begin();display.begin();nvsOk=storage.begin();
 robot.begin(millis());if(!nvsOk||!pcaOk)robot.hardwareFault();
 WiFi.persistent(false);WiFi.setAutoReconnect(false);WiFi.mode(WIFI_AP_STA);
 uint64_t mac=ESP.getEfuseMac();char name[24];snprintf(name,sizeof(name),"CuaRobot-%04X",unsigned((mac>>32)&0xFFFF));
 wifi=new Wifi(storage,radio,name);api=new Api(robot,*wifi);
 wifi->begin(millis());
 server.on("/",HTTP_GET,servePage);server.on("/rap",HTTP_GET,servePage);
 server.on("/api/scan",HTTP_GET,handleScan);
 for(const char* path:{"/api/status","/api/move","/api/stop","/api/light","/api/wifi","/api/assembly","/api/trim"})server.on(path,HTTP_ANY,handleApi);
 // Captive-portal probes receive the local page; unknown paths redirect to it.
 for(const char* path:{"/generate_204","/gen_204","/hotspot-detect.html","/connecttest.txt","/ncsi.txt","/fwlink"})server.on(path,HTTP_GET,servePage);
 server.onNotFound([](){server.sendHeader("Location",wifi->url.c_str(),true);server.send(302,"text/plain","");});server.begin();
 xTaskCreatePinnedToCore(actuatorTask,"cua-motion",6144,nullptr,2,nullptr,1);
}
void loop(){
 if(resetPending.exchange(false)){online=false;wifi->reset();}
 wifi->tick(millis());online=wifi->state==WifiState::Online;
 dns.processNextRequest();server.handleClient();
 bool fault;{Guard guard;fault=robot.isFault();}
 Str message=wifi->message;
 int countdown=bootCountdown.load();
 if(countdown>=0)message="Giữ BOOT "+std::to_string(countdown)+" giây để xóa Wi-Fi";
 else if(!nvsOk)message="Lỗi lưu bộ nhớ, thử bật lại";
 else if(fault)message="Không thấy PCA9685. Kiểm tra dây";
 display.show(wifi->qr(),message,wifi->state==WifiState::Online?wifi->url:"192.168.4.1");
 delay(2); // Scheduler yield only; motion, leases and BOOT run on the independent task.
}

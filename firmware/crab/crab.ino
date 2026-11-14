// SPDX-License-Identifier: GPL-3.0-or-later
#include <Arduino.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <Preferences.h>
#include <atomic>
#include "core.h"
#include "drivers.h"
#include "actuator_output.h"
#include "display.h"
#include "web_ui.h"
WebServer server(80);DNSServer dns;
Preferences wifiStore,trimStore,emoteStore;
crab::Motion motion;crab::Network network;crab::HoldButton boot;
ServoDriver servos;LightDriver light;Screen screen;
SemaphoreHandle_t motionLock;
std::atomic<bool> driverReady(false);
std::atomic<bool> eraseHold(false),stationHasIp(false);
String ap,storedSsid,storedPass,candidateSsid,candidatePass;
bool lightOn=true,displayOk=false;
uint32_t lightRgb=0xffffff; // owner-picked lamp colour, saved as "led"
crab::Eyes eyes;crab::EyeFrame drawnEyes;bool faceShown=false;
uint32_t lastDraw=0;String drawnKey;
struct Guard{Guard(){xSemaphoreTake(motionLock,portMAX_DELAY);}~Guard(){xSemaphoreGive(motionLock);}};
#include "network_http.h"
void motionTask(void*){
 ActuatorOutput outputs;
 TickType_t wake=xTaskGetTickCount();
 for(;;){
  {
   Guard g;motion.inhibit=eraseHold.load()||!driverReady.load();
   if(driverReady.load()&&!outputs.service(motion,servos,millis()))driverReady=false;
   else if(!driverReady.load()){motion.stop();motion.tick(millis());}
  }
  vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}
void setup(){
 // No Serial logging, no hardcoded credentials, no hardware discovery.
 servos.inhibit();
 pinMode(cfg::BOOT_PIN,INPUT_PULLUP);
 motionLock=xSemaphoreCreateMutex();
 displayOk=screen.begin();light.begin();driverReady=servos.begin();
 wifiStore.begin("cua-wifi",false);trimStore.begin("cua-180-v1",false);emoteStore.begin("cua-emote",false);
 {Guard g;if(trimStore.getBytesLength("offsets")==sizeof(motion.offsets)){trimStore.getBytes("offsets",motion.offsets,sizeof(motion.offsets));for(auto& v:motion.offsets)if(!std::isfinite(v)||std::fabs(v)>cfg::TRIM_LIMIT)v=0;}
  if(!motion.setBalance(trimStore.getInt("balance",0)))motion.balance=0;
  lightRgb=uint32_t(trimStore.getInt("led",0xffffff))&0xffffff;
  if(!motion.setKneeLift(trimStore.getInt("knee",int(cfg::KNEE_LIFT))))motion.kneeLift=cfg::KNEE_LIFT;
  motion.begin(millis());motion.bootArm(driverReady.load(),millis());}
 applyLight();
 xTaskCreatePinnedToCore(motionTask,"cua-motion",4096,nullptr,3,nullptr,1);
 WiFi.onEvent([](WiFiEvent_t event){if(event==ARDUINO_EVENT_WIFI_STA_GOT_IP)stationHasIp=true;else if(event==ARDUINO_EVENT_WIFI_STA_DISCONNECTED)stationHasIp=false;});
 WiFi.persistent(false);WiFi.mode(WIFI_AP_STA);WiFi.setAutoReconnect(false);
 // Modem sleep naps the radio between beacons: owner saw the page hang with
 // 60% ping loss and up to 800 ms latency. Keep the radio awake (USB/bank powered).
 WiFi.setSleep(false);
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
 serviceNetwork(now);
 dns.processNextRequest();server.handleClient();
 // Owner: pet eyes on the screen, Wi-Fi as one small line at the bottom. The
 // QR join screen stays only for first setup (no saved Wi-Fi).
 const bool face=network.saved||network.state!=crab::NetState::Setup;
 if(displayOk&&face&&now-lastDraw>=40){lastDraw=now;
  bool active;{Guard g;active=motion.amplitude>.05f||motion.posing;}
  const crab::EyeFrame f=eyes.frame(now,active);
  const String message=driverReady?String(network.message):String(crab::msg::DRIVER);
  const String address=!driverReady?String():network.state==crab::NetState::Online?WiFi.localIP().toString():ap+" 192.168.4.1";
  const String line=message+"|"+address;
  if(!faceShown||f!=drawnEyes||line!=drawnKey){if(screen.face(f,message.c_str(),address.c_str())){drawnEyes=f;drawnKey=line;faceShown=true;}}
 }else if(!face&&now-lastDraw>=250){lastDraw=now;if(faceShown){faceShown=false;drawnKey="";}
  String url="192.168.4.1";String message=driverReady?String(network.message):String(crab::msg::DRIVER);String key=url+message;
  if(displayOk&&key!=drawnKey){String payload=crab::wifiQr(ap.c_str()).c_str();if(screen.show(payload.c_str(),message.c_str(),url.c_str(),ap.c_str()))drawnKey=key;}
 }
 delay(1); // RTOS yield; motion and its 500-ms watchdog run independently
}

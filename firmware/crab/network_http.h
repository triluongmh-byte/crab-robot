// SPDX-License-Identifier: GPL-3.0-or-later
// Actual HTTP handlers and station servicing, also exercised by host tests.
#pragma once
String jsonString(const String& s){String out="\"";for(size_t i=0;i<s.length();i++){unsigned char c=s[i];if(c=='"'||c=='\\'){out+='\\';out+=char(c);}else if(c<32){char b[7];snprintf(b,sizeof(b),"\\u%04x",c);out+=b;}else out+=char(c);}return out+"\"";}
void json(int code,const String& s){server.sendHeader("Cache-Control","no-store");server.sendHeader("X-Content-Type-Options","nosniff");server.send(code,"application/json; charset=utf-8",s);}
void ok(){json(200,"{\"ok\":true}");}
void error(int code=400){json(code,"{\"error\":\"Lệnh chưa hợp lệ hoặc chưa sẵn sàng\"}");}
bool uintArg(const char* name,uint32_t& value){String s=server.arg(name);if(s.length()==0||s.length()>10)return false;uint64_t v=0;for(char c:s){if(c<'0'||c>'9')return false;v=v*10+c-'0';if(v>0xffffffffULL)return false;}value=(uint32_t)v;return true;}
bool owns(){uint32_t t;if(!uintArg("token",t))return false;Guard g;return t&&t==motion.session;}
void stopMotion(){Guard g;motion.stop();}
void connectStation(const String& ssid,const String& pass){WiFi.disconnect(false,false);stationHasIp=false;WiFi.begin(ssid.c_str(),pass.c_str());}
void pauseSavedRetry(){
 network.pauseRetry(millis());
 if(network.pauseRequested){WiFi.disconnect(false,false);stationHasIp=false;network.pauseRequested=false;}
}
void actuatorError(){json(409,"{\"error\":\"Servo 360° hoặc chưa rõ loại: không đi bộ, không đưa về giữa. Chỉ thử từng servo không tải.\"}");}
void configureHttp(){
 server.on("/api/status",HTTP_GET,[]{crab::Motion state;{Guard g;state=motion;}String url=network.state==crab::NetState::Online?String("http://")+WiFi.localIP().toString()+"/":"http://192.168.4.1/";
  json(200,String("{\"message\":")+jsonString(network.message)+",\"url\":"+jsonString(url)+",\"online\":"+(network.state==crab::NetState::Online?"true":"false")+",\"driver\":"+(driverReady?"true":"false")+",\"assembly\":"+(state.assembly?"true":"false")+",\"positional\":"+(state.positional()?"true":"false")+",\"testOpen\":"+(state.test.opened?"true":"false")+",\"testActive\":"+(state.test.active?"true":"false")+",\"testChannel\":"+String(state.test.channel)+",\"neutralCounts\":"+String(state.test.neutral)+",\"pulseCounts\":"+String(state.test.emittedCounts)+",\"emittedChannel\":"+String(state.test.emittedChannel)+",\"requestedCounts\":"+String(state.test.counts)+"}");});
 server.on("/api/session",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;{Guard g;motion.newSession(token);}json(200,"{\"token\":\""+String(token)+"\"}");});
 server.on("/api/move",HTTP_POST,[]{uint32_t token,seq,dir,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("dir",dir)||!uintArg("fresh",fresh)||fresh>1||dir>8){error();return;}bool accepted;{Guard g;if(dir&&!motion.positional()){actuatorError();return;}accepted=motion.command(token,seq,int(dir),millis(),fresh==1);}if(accepted)ok();else error(409);});
 server.on("/api/scan",HTTP_POST,[]{
  pauseSavedRetry();
  if(network.state==crab::NetState::Connecting){json(200,"{\"busy\":true}");return;}
  int n=WiFi.scanComplete();if(n==WIFI_SCAN_FAILED){WiFi.scanNetworks(true);json(200,"{\"busy\":true}");return;}
  if(n==WIFI_SCAN_RUNNING){json(200,"{\"busy\":true}");return;}
  String s="{\"busy\":false,\"networks\":[";int count=0;
  for(int i=0;i<n&&count<30;i++){String name=WiFi.SSID(i);if(name.length()==0)continue;bool dup=false;for(int j=0;j<i;j++)if(WiFi.SSID(j)==name)dup=true;if(dup)continue;if(count++)s+=',';s+=jsonString(name);}s+="]}";WiFi.scanDelete();json(200,s);
 });
 server.on("/api/wifi",HTTP_POST,[]{
  String ssid=server.arg("ssid"),pass=server.arg("password");
  if(ssid.length()<1||ssid.length()>32||pass.length()>63||(pass.length()>0&&pass.length()<8)){error();return;}
  WiFi.scanDelete();stopMotion();candidateSsid=ssid;candidatePass=pass;network.connect(true,millis());connectStation(ssid,pass);ok();
 });
 server.on("/api/light",HTTP_POST,[]{if(!owns()){error(409);return;}lightOn=!lightOn;light.set(lightOn);ok();});
 server.on("/api/speed",HTTP_POST,[]{if(!owns()){error(409);return;}String s=server.arg("value");if(s!="0.4"&&s!="0.65"&&s!="1"){error();return;}{Guard g;motion.speed=s.toFloat();}ok();});
 server.on("/api/assembly",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t a;if(!uintArg("active",a)||a>1){error();return;}{Guard g;if(!motion.setAssembly(a)){error(409);return;}}ok();});
 server.on("/api/centre",HTTP_POST,[]{if(!owns()){error(409);return;}{Guard g;if(!motion.centre()){actuatorError();return;}}ok();});
 server.on("/api/stand",HTTP_POST,[]{if(!owns()){error(409);return;}{Guard g;if(!motion.positional()){actuatorError();return;}motion.setAssembly(true);}ok();});
 server.on("/api/trim",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t ch;String s=server.arg("delta");if(!uintArg("ch",ch)||ch>7||(s!="-1"&&s!="1")){error();return;}bool accepted;float offset;{Guard g;accepted=motion.trim(ch,s.toInt());offset=motion.offsets[ch];}if(!accepted){error(409);return;}json(200,"{\"offset\":"+String(offset,0)+"}");});
 server.on("/api/save",HTTP_POST,[]{if(!owns()){error(409);return;}float offsets[8];{Guard g;if(!motion.positional()||!motion.assembly){actuatorError();return;}memcpy(offsets,motion.offsets,sizeof(offsets));}
  if(trimStore.putBytes("offsets",offsets,sizeof(offsets))!=sizeof(offsets)){error(500);return;}ok();});
 // Explicit RAM-only mode selection. No servo type or test result is saved.
 server.on("/api/actuator",HTTP_POST,[]{
  uint32_t seq;if(!owns()||!uintArg("seq",seq)){error(409);return;}
  String value=server.arg("value");if(value!="unknown"&&value!="positional"){error();return;}
  if(value=="positional"&&server.arg("confirm")!="1"){error();return;}
  {Guard g;if(!motion.sequence(motion.session,seq)||!motion.selectActuator(value=="positional",millis())){error(409);return;}}ok();
 });
 server.on("/api/test",HTTP_POST,[]{
  uint32_t active,seq;if(!owns()||!uintArg("seq",seq)||!uintArg("active",active)||active>1){error();return;}
  {Guard g;if(!motion.sequence(motion.session,seq)||!motion.openTest(active)){error(409);return;}}ok();
 });
 server.on("/api/test/config",HTTP_POST,[]{
  uint32_t seq,ch,neutral;if(!owns()||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("neutral",neutral)||neutral<287||neutral>327){error();return;}
  {Guard g;if(!motion.sequence(motion.session,seq)||!motion.test.opened||motion.assembly||motion.actuator!=crab::Actuator::Unknown||!motion.test.config(ch,neutral)){error(409);return;}}ok();
 });
 server.on("/api/test/hold",HTTP_POST,[]{
  uint32_t token,seq,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("fresh",fresh)||fresh>1){error();return;}
  String step=server.arg("step");if(step!="-20"&&step!="-4"&&step!="-1"&&step!="0"&&step!="1"&&step!="4"&&step!="20"){error();return;}
  {Guard g;if(!motion.testCommand(token,seq,step.toInt(),millis(),fresh==1)){error(409);return;}}
  ok();
 });
 // Captive portal probes (Android/iOS/Windows) all land on our embedded page.
 server.onNotFound([]{if(server.uri().startsWith("/api/")){error(404);return;}server.sendHeader("Cache-Control","no-store");server.send_P(200,"text/html; charset=utf-8",WEB_UI);});
 server.begin();
}
void serviceNetwork(uint32_t now){
 bool connected=stationHasIp.load()&&WiFi.status()==WL_CONNECTED&&WiFi.SSID()==(network.pending?candidateSsid:storedSsid);
 bool candidateWas=network.pending;
 network.tick(now,connected,crab::elapsed(now,network.since)>500&&(WiFi.status()==WL_CONNECT_FAILED||WiFi.status()==WL_NO_SSID_AVAIL),WiFi.softAPgetStationNum()>0);
 if(network.pauseRequested){WiFi.disconnect(false,false);stationHasIp=false;network.pauseRequested=false;}
 if(network.saveRequested){
  storedSsid=candidateSsid;storedPass=candidatePass;wifiStore.putString("ssid",storedSsid);wifiStore.putString("pass",storedPass);
  candidatePass="";candidateSsid="";network.saveRequested=false;
 }
 if(candidateWas&&!network.pending&&!connected){candidateSsid="";candidatePass="";WiFi.disconnect(false,false);}
 if(network.retryRequested){connectStation(storedSsid,storedPass);network.retryRequested=false;}
}

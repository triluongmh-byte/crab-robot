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
// "a" holds eight comma-separated joint angles in degrees, each within +/-90.
bool poseArg(float out[8]){
 String s=server.arg("a");if(s.length()<15||s.length()>120)return false;
 const char* p=s.c_str();
 for(int ch=0;ch<8;ch++){
  char* end=nullptr;float v=strtof(p,&end);if(end==p||!std::isfinite(v)||v<-90||v>90)return false;
  out[ch]=v;p=end;if(ch<7){if(*p!=',')return false;p++;}
 }
 return *p==0;
}
// Speed slider: plain decimal fraction ("0.9"), SPEED_MIN..SPEED_MAX.
bool speedArg(float& out){
 String s=server.arg("value");if(s.length()<1||s.length()>5)return false;
 int dots=0;for(char c:s){if(c=='.'){if(++dots>1)return false;}else if(c<'0'||c>'9')return false;}
 const float v=s.toFloat();if(!(v>=cfg::SPEED_MIN-1e-4f&&v<=cfg::SPEED_MAX+1e-4f))return false;
 out=crab::clamp(v,cfg::SPEED_MIN,cfg::SPEED_MAX);return true;
}
// Saved emotions are opaque JSON for the page; bound size and reject control bytes.
bool emotionListValid(const String& s){
 if(s.length()<2||s.length()>3800||s[0]!='['||s[s.length()-1]!=']')return false;
 for(size_t i=0;i<s.length();i++)if((unsigned char)s[i]<32)return false;
 return true;
}
// Caller owns motionLock; only hard-off writes occur here. Never send HTTP under it.
void offForChangeLocked(){
 motion.stop();motion.outputEpoch++;motion.test.generation++;motion.continuous.generation++;
 if(driverReady.load()&&!servos.disableOutputs()){driverReady=false;motion.inhibit=true;}
}
void connectStation(const String& ssid,const String& pass){WiFi.disconnect(false,false);stationHasIp=false;WiFi.begin(ssid.c_str(),pass.c_str());}
void pauseSavedRetry(){
 network.pauseRetry(millis());
 if(network.pauseRequested){WiFi.disconnect(false,false);stationHasIp=false;network.pauseRequested=false;}
}
void actuatorError(){json(409,"{\"error\":\"Bản180°: bấm Bật servo180° trước, chờ bật đủ8 kênh và thoát Ráp để lái.\"}");}
void configureHttp(){
 server.on("/api/status",HTTP_GET,[]{crab::Motion state;{Guard g;state=motion;}String url=network.state==crab::NetState::Online?String("http://")+WiFi.localIP().toString()+"/":"http://192.168.4.1/";
  String offsets="[";for(int ch=0;ch<8;ch++){if(ch)offsets+=",";offsets+=String(state.offsets[ch],0);}offsets+="]";
  json(200,String("{\"firmware\":\"positional180-v11\",\"servoType\":\"positional180\",\"drive360\":false,\"lightOn\":")+(lightOn?"true":"false")+",\"message\":"+jsonString(network.message)+",\"url\":"+jsonString(url)+",\"online\":"+(network.state==crab::NetState::Online?"true":"false")+",\"driver\":"+(driverReady?"true":"false")+",\"assembly\":"+(state.assembly?"true":"false")+",\"positional\":"+(state.positional()?"true":"false")+",\"enabled\":"+String(state.enabled)+",\"speed\":"+String(state.speed,2)+",\"gait\":"+jsonString(crab::patternName(state.gaitPattern))+",\"flickHip\":"+String(state.flickHip,0)+",\"offsets\":"+offsets+"}");});
 // Read-only view of last acknowledged output commands. No writes or arming.
 server.on("/api/servos",HTTP_GET,[]{
  crab::ServoTelemetry samples[8];bool driver;uint32_t sampledAt;
  {Guard g;servos.snapshot(samples);driver=driverReady.load();sampledAt=millis();}
  String body="{\"kind\":\"commanded\",\"feedback\":false,\"driver\":"+String(driver?"true":"false")+",\"sampledAtMs\":"+String(sampledAt)+",\"servos\":[";
  for(int ch=0;ch<8;ch++){
   const auto& x=samples[ch];if(ch)body+=",";
   body+="{\"ch\":"+String(ch)+",\"known\":"+String(x.known?"true":"false")+",\"active\":"+String(x.known&&x.active?"true":"false");
   if(x.known&&x.active)body+=",\"angleDeg\":"+String(90.f+(x.pulseUs-cfg::CENTRE_US)/cfg::US_PER_DEG,1)+",\"pulseUs\":"+String(x.pulseUs)+",\"counts\":"+String(x.counts);
   else body+=",\"angleDeg\":null,\"pulseUs\":null,\"counts\":null";
   body+="}";
  }
  body+="]}";json(200,body);
 });
 server.on("/api/session",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;{Guard g;offForChangeLocked();motion.newSession(token);}json(200,"{\"token\":\""+String(token)+"\"}");});
 server.on("/api/move",HTTP_POST,[]{uint32_t token,seq,dir,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("dir",dir)||!uintArg("fresh",fresh)||fresh>1||dir>8){error();return;}bool accepted,blocked;{Guard g;blocked=dir&&(!motion.positional()||motion.enabled<8||motion.assembly);accepted=!blocked&&motion.command(token,seq,int(dir),millis(),fresh==1);}if(blocked){actuatorError();return;}if(accepted)ok();else error(409);});
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
 // Emotion studio: direct poses under the walking lease/deadman, LED colour, saved list.
 server.on("/api/pose",HTTP_POST,[]{
  uint32_t token,seq,ms,fresh;float angles[8];
  if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("ms",ms)||!uintArg("fresh",fresh)||fresh>1||ms>5000||!poseArg(angles)){error();return;}
  bool accepted,blocked;{Guard g;blocked=!motion.positional()||motion.enabled<8||motion.assembly;accepted=!blocked&&motion.poseCommand(token,seq,angles,ms,millis(),fresh==1);}
  if(blocked){actuatorError();return;}if(accepted)ok();else error(409);});
 server.on("/api/led",HTTP_POST,[]{uint32_t r,g,b;if(!owns()){error(409);return;}if(!uintArg("r",r)||!uintArg("g",g)||!uintArg("b",b)||r>255||g>255||b>255){error();return;}lightOn=r||g||b;light.color(r,g,b);ok();});
 server.on("/api/emotions",HTTP_GET,[]{String list=emoteStore.getString("list","[]");json(200,list.length()?list:String("[]"));});
 server.on("/api/emotions/save",HTTP_POST,[]{if(!owns()){error(409);return;}String data=server.arg("data");if(!emotionListValid(data)){error();return;}if(emoteStore.putString("list",data)!=data.length()){error(500);return;}ok();});
 server.on("/emo",HTTP_GET,[]{server.sendHeader("Cache-Control","no-store");server.send_P(200,"text/html; charset=utf-8",EMOTE_UI);});
 server.on("/api/speed",HTTP_POST,[]{if(!owns()){error(409);return;}float v;if(!speedArg(v)){error();return;}{Guard g;offForChangeLocked();motion.speed=v;}ok();});
 // Knee-flick hip stance, whole degrees FLICK_HIP_MIN..FLICK_HIP.
 server.on("/api/flickhip",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t v;if(!uintArg("value",v)||v<cfg::FLICK_HIP_MIN||v>cfg::FLICK_HIP){error();return;}{Guard g;offForChangeLocked();motion.flickHip=float(v);}ok();});
 server.on("/api/gait",HTTP_POST,[]{if(!owns()){error(409);return;}String s=server.arg("value");if(s!="trot"&&s!="pairs"&&s!="flick"){error();return;}{Guard g;offForChangeLocked();motion.gaitPattern=s=="pairs"?crab::Pattern::Pairs:s=="flick"?crab::Pattern::Flick:crab::Pattern::Trot;}ok();});
 server.on("/api/assembly",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t a;if(!uintArg("active",a)||a>1){error();return;}bool accepted;{Guard g;offForChangeLocked();accepted=motion.setAssembly(a);}if(!accepted){error(409);return;}ok();});
 server.on("/api/centre",HTTP_POST,[]{if(!owns()){error(409);return;}bool accepted;{Guard g;offForChangeLocked();accepted=motion.centre();}if(!accepted){actuatorError();return;}ok();});
 server.on("/api/stand",HTTP_POST,[]{if(!owns()){error(409);return;}bool accepted;{Guard g;offForChangeLocked();accepted=motion.positional()&&motion.setAssembly(true);}if(!accepted){actuatorError();return;}ok();});
 server.on("/api/trim",HTTP_POST,[]{if(!owns()){error(409);return;}uint32_t ch;String s=server.arg("delta");if(!uintArg("ch",ch)||ch>7||(s!="-1"&&s!="1")){error();return;}bool accepted;float offset;{Guard g;offForChangeLocked();accepted=motion.trim(ch,s.toInt());offset=motion.offsets[ch];}if(!accepted){error(409);return;}json(200,"{\"offset\":"+String(offset,0)+"}");});
 server.on("/api/save",HTTP_POST,[]{if(!owns()){error(409);return;}float offsets[8];bool accepted;{Guard g;offForChangeLocked();accepted=motion.positional()&&motion.assembly;memcpy(offsets,motion.offsets,sizeof(offsets));}if(!accepted){actuatorError();return;}
  if(trimStore.putBytes("offsets",offsets,sizeof(offsets))!=sizeof(offsets)){error(500);return;}ok();});
 // Explicit RAM-only mode selection. No servo type or test result is saved.
 server.on("/api/actuator",HTTP_POST,[]{
  uint32_t seq;if(!owns()||!uintArg("seq",seq)){error(409);return;}
  String value=server.arg("value");if(value!="unknown"&&value!="positional"){error();return;}
  if(value=="positional"&&server.arg("confirm")!="1"){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(motion.session,seq);if(accepted){offForChangeLocked();accepted=motion.selectActuator(value=="positional",millis());}}if(!accepted){error(409);return;}ok();
 });
 // The former /api/test and /api/360 routes are intentionally not registered.
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

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
void actuatorError(){json(409,"{\"error\":\"Servo 360° hoặc chưa rõ loại: không đi bộ, không đưa về giữa. Chỉ thử từng servo không tải.\"}");}
String continuousState(const crab::Continuous360& c){return String("{\"referenceValid\":")+(c.referenceValid?"true":"false")+",\"cwViewpoint\":"+String(int(c.viewpoint))+",\"estimatedAngle\":"+String(c.estimated[c.channel],2)+",\"clipped\":"+(c.clipped?"true":"false")+",\"moveDuration\":"+String(c.duration)+",\"reason\":"+jsonString(c.reason);}
void continuousReply(bool accepted,const crab::Continuous360& c){json(accepted?200:409,continuousState(c)+",\"ok\":"+(accepted?"true":"false")+",\"error\":"+jsonString(accepted?"":c.reason)+"}");}
void configureHttp(){
 server.on("/api/status",HTTP_GET,[]{crab::Motion state;{Guard g;state=motion;}String url=network.state==crab::NetState::Online?String("http://")+WiFi.localIP().toString()+"/":"http://192.168.4.1/";
  String continuous="[";for(int ch=0;ch<8;ch++){const auto& c=state.continuous.channels[ch];if(ch)continuous+=",";continuous+=String("{\"stop\":")+String(c.stop)+",\"forward\":"+String(c.forward)+",\"reverse\":"+String(c.reverse)+",\"confirmed\":"+(c.confirmed?"true":"false")+",\"cwCalibrated\":"+(c.cw.calibrated?"true":"false")+",\"ccwCalibrated\":"+(c.ccw.calibrated?"true":"false")+",\"cwCounts\":"+String(c.cw.counts)+",\"ccwCounts\":"+String(c.ccw.counts)+",\"cwRate\":"+String(c.cw.degreesPerMs,6)+",\"ccwRate\":"+String(c.ccw.degreesPerMs,6)+",\"estimated\":"+String(state.continuous.estimated[ch],2)+",\"cwBudget\":"+String(crab::Continuous360::budget(ch,1),0)+",\"ccwBudget\":"+String(crab::Continuous360::budget(ch,2),0)+"}";}continuous+="]";
  json(200,continuousState(state.continuous)+",\"drive360\":true,\"hipsOnly\":true,\"hipBalanceMs\":"+String(state.drive.balanceMs)+",\"drive360Active\":"+(state.drive.active?"true":"false")+",\"lightOn\":"+(lightOn?"true":"false")+",\"continuousOpen\":"+(state.continuous.opened?"true":"false")+",\"continuousActive\":"+(state.continuous.active?"true":"false")+",\"continuousChannel\":"+String(state.continuous.channel)+",\"continuousRequested\":"+String(state.continuous.counts)+",\"continuousEmitted\":"+String(state.continuous.emittedCounts)+",\"continuousEmittedChannel\":"+String(state.continuous.emittedChannel)+",\"continuousDuration\":"+String(state.continuous.duration)+",\"continuousCalibration\":"+continuous+",\"message\":"+jsonString(network.message)+",\"url\":"+jsonString(url)+",\"online\":"+(network.state==crab::NetState::Online?"true":"false")+",\"driver\":"+(driverReady?"true":"false")+",\"assembly\":"+(state.assembly?"true":"false")+",\"positional\":"+(state.positional()?"true":"false")+",\"testOpen\":"+(state.test.opened?"true":"false")+",\"testActive\":"+(state.test.active?"true":"false")+",\"testChannel\":"+String(state.test.channel)+",\"neutralCounts\":"+String(state.test.neutral)+",\"pulseCounts\":"+String(state.test.emittedCounts)+",\"emittedChannel\":"+String(state.test.emittedChannel)+",\"requestedCounts\":"+String(state.test.counts)+"}");});
 server.on("/api/session",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;{Guard g;offForChangeLocked();motion.newSession(token);}json(200,"{\"token\":\""+String(token)+"\"}");});
 server.on("/api/move",HTTP_POST,[]{uint32_t token,seq,dir,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("dir",dir)||!uintArg("fresh",fresh)||fresh>1||dir>8){error();return;}bool accepted,blocked;{Guard g;blocked=dir&&(motion.assembly||motion.test.opened||motion.continuous.opened);accepted=!blocked&&motion.command(token,seq,int(dir),millis(),fresh==1);}if(blocked){actuatorError();return;}if(accepted)ok();else error(409);});
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
 server.on("/api/speed",HTTP_POST,[]{if(!owns()){error(409);return;}String s=server.arg("value");if(s!="0.4"&&s!="0.65"&&s!="1"){error();return;}{Guard g;offForChangeLocked();motion.speed=s.toFloat();}ok();});
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
 server.on("/api/test",HTTP_POST,[]{
  uint32_t active,seq;if(!owns()||!uintArg("seq",seq)||!uintArg("active",active)||active>1){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(motion.session,seq);if(accepted){offForChangeLocked();accepted=motion.openTest(active);}}if(!accepted){error(409);return;}ok();
 });
 server.on("/api/test/config",HTTP_POST,[]{
  uint32_t seq,ch,neutral;if(!owns()||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("neutral",neutral)||neutral<287||neutral>327){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(motion.session,seq);if(accepted){offForChangeLocked();accepted=motion.test.opened&&!motion.assembly&&motion.actuator==crab::Actuator::Unknown&&motion.test.config(ch,neutral);}}if(!accepted){error(409);return;}ok();
 });
 server.on("/api/test/hold",HTTP_POST,[]{
  uint32_t token,seq,fresh;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("fresh",fresh)||fresh>1){error();return;}
  String step=server.arg("step");if(step!="-20"&&step!="-4"&&step!="-1"&&step!="0"&&step!="1"&&step!="4"&&step!="20"){error();return;}
  bool accepted;{Guard g;accepted=motion.testCommand(token,seq,step.toInt(),millis(),fresh==1);}if(!accepted){error(409);return;}ok();
 });
 // Separate continuous speed/direction experiment; never invokes angular gait.
 server.on("/api/360",HTTP_POST,[]{
  uint32_t active,seq;if(!owns()||!uintArg("seq",seq)||!uintArg("active",active)||active>1){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(motion.session,seq);if(accepted){offForChangeLocked();accepted=motion.openContinuous(active);}}
  if(!accepted){error(409);return;}ok();
 });
 server.on("/api/360/config",HTTP_POST,[]{
  uint32_t seq,ch,neutral,forward,reverse;
  if(!owns()||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("stop",neutral)||!uintArg("forward",forward)||!uintArg("reverse",reverse)||!crab::Continuous360::validCount(neutral)||!crab::Continuous360::validCount(forward)||!crab::Continuous360::validCount(reverse)){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(motion.session,seq);if(accepted){offForChangeLocked();accepted=motion.continuous.opened&&!motion.inhibit&&!motion.assembly&&motion.actuator==crab::Actuator::Unknown&&!motion.test.opened&&motion.continuous.configure(ch,neutral,forward,reverse);}}
  if(!accepted){error(409);return;}ok();
 });
 server.on("/api/360/hold",HTTP_POST,[]{
  uint32_t token,seq,ch,action,duration,fresh;
  if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("action",action)||action>2||!uintArg("duration",duration)||duration<crab::Continuous360::MIN_MS||duration>crab::Continuous360::MAX_MS||!uintArg("fresh",fresh)||fresh>1){error();return;}
  bool accepted;crab::Continuous360 result;{Guard g;accepted=motion.continuousCommand(token,seq,ch,action,duration,millis(),fresh==1);result=motion.continuous;}
  continuousReply(accepted,result);
 });
 // Manual-reference settings are ordered, stop first and never emit a pulse.
 server.on("/api/360/viewpoint",HTTP_POST,[]{
  uint32_t token,seq,value;if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("value",value)||value>2){error();return;}
  bool accepted;{Guard g;accepted=motion.sequence(token,seq);if(accepted){offForChangeLocked();accepted=motion.continuous.opened&&motion.continuous.setViewpoint(value);}}if(accepted)ok();else error(409);
 });
 server.on("/api/360/calibrate",HTTP_POST,[]{
  uint32_t token,seq,ch,dir,counts,degrees,ms;
  if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("direction",dir)||dir<1||dir>2||!uintArg("counts",counts)||!crab::Continuous360::validCount(counts)||!uintArg("degrees",degrees)||degrees<1||degrees>180||!uintArg("ms",ms)||ms<50||ms>60000){error();return;}
  bool accepted;crab::Continuous360 result;{Guard g;accepted=motion.sequence(token,seq);if(accepted){offForChangeLocked();accepted=motion.continuous.opened&&!motion.inhibit&&motion.continuous.calibrate(ch,dir,counts,degrees,ms);}result=motion.continuous;}continuousReply(accepted,result);
 });
 server.on("/api/360/reference",HTTP_POST,[]{
  uint32_t token,seq;if(!uintArg("token",token)||!uintArg("seq",seq)||server.arg("confirm")!="manual90"){error();return;}
  bool accepted;crab::Continuous360 result;{Guard g;accepted=motion.sequence(token,seq);if(accepted){offForChangeLocked();accepted=motion.continuous.opened&&!motion.inhibit&&motion.continuous.confirmReference();}result=motion.continuous;}continuousReply(accepted,result);
 });
 server.on("/api/360/move",HTTP_POST,[]{
  uint32_t token,seq,ch,dir,degrees,fresh,cap;
  if(!uintArg("token",token)||!uintArg("seq",seq)||!uintArg("ch",ch)||ch>7||!uintArg("direction",dir)||dir<1||dir>2||!uintArg("degrees",degrees)||degrees<1||degrees>60||!uintArg("cap",cap)||cap<50||cap>500||!uintArg("fresh",fresh)||fresh>1){error();return;}
  bool accepted;crab::Continuous360 result;{Guard g;accepted=motion.sequence(token,seq)&&!motion.inhibit&&!motion.assembly&&motion.actuator==crab::Actuator::Unknown&&!motion.test.opened&&motion.continuous.move(ch,dir,degrees,millis(),fresh==1,cap);result=motion.continuous;}continuousReply(accepted,result);
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

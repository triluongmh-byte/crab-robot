// SPDX-License-Identifier: GPL-3.0-or-later
// Kame32 oscillator gait adapted 2026-11-06: PCA9685 channels, crawl staggering,
// vector projection, bounded velocity/acceleration, no blocking execute()/delay().
#include "Robot.h"
#include <cmath>
#include <algorithm>
#include <cstdlib>
namespace crab {
namespace {
constexpr float pi=3.14159265358979323846f;
float clamp(float v,float a,float b){return std::max(a,std::min(v,b));}
Str arg(const Request& r,const Str& key){auto i=r.args.find(key);return i==r.args.end()?"":i->second;}
Response result(int status,const Str& text){return {status,"application/json; charset=utf-8","{\"message\":"+jsonString(text)+"}"};}
}
Str jsonString(const Str& s){
 Str o="\"";const char* hex="0123456789abcdef";
 for(unsigned char c:s){if(c=='"'||c=='\\'){o+='\\';o+=char(c);}else if(c<32){o+="\\u00";o+=hex[c>>4];o+=hex[c&15];}else o+=char(c);}return o+"\"";
}
bool unsignedNumber(const Str& s,uint32_t& n){
 if(s.empty()||s.size()>10)return false;
 uint64_t v=0;for(char c:s){if(c<'0'||c>'9')return false;v=v*10+c-'0';if(v>UINT32_MAX)return false;}n=uint32_t(v);return true;
}
void Wifi::portal(const Str& error){
 radio.disconnect();radio.accessPoint(apName);state=WifiState::Portal;
 pendingPassword.clear();pendingSsid.clear();candidate=false;
 url="http://192.168.4.1/";message=error;
}
void Wifi::begin(uint32_t now){
 auto record=store.get("wifi");auto split=record.find(':');uint32_t length=0;
 bool valid=split!=Str::npos&&unsignedNumber(record.substr(0,split),length)&&length>0&&length<=32&&record.size()>=split+1+length&&record.size()<=split+1+length+63;
 Str ssid=valid?record.substr(split+1,length):"",pass=valid?record.substr(split+1+length):"";
 if(ssid.empty()){portal("Quét QR để nối Wi-Fi");return;}
 radio.accessPoint(apName);radio.join(ssid,pass);started=now;
 state=WifiState::Connecting;message="Đang nối Wi-Fi đã lưu";
}
bool Wifi::submit(const Str& ssid,const Str& password,uint32_t now){
 if(ssid.empty()||ssid.size()>32||password.size()>63||ssid.find('\0')!=Str::npos||password.find('\0')!=Str::npos)return false;
 if(state==WifiState::Connecting)return false;
 radio.accessPoint(apName);radio.join(ssid,password);started=now;
 pendingSsid=ssid;pendingPassword=password;candidate=true;
 state=WifiState::Connecting;message="Đang nối Wi-Fi, chờ một chút";return true;
}
void Wifi::tick(uint32_t now){
 if(state==WifiState::Connecting){
  if(radio.connected()){
   if(candidate){
    // One atomic NVS value avoids mixed SSID/password records after power loss.
    if(!store.put("wifi",std::to_string(pendingSsid.size())+":"+pendingSsid+pendingPassword)){
     portal("Chưa lưu được Wi-Fi, thử lại nhé");return;
    }
   }
   pendingPassword.clear();pendingSsid.clear();candidate=false;
   radio.stopAP();state=WifiState::Online;url="http://"+radio.address()+"/";message="Đã vào Wi-Fi";
  }else if(elapsed(now,started)>=cfg::wifiTimeoutMs){portal("Sai mật khẩu Wi-Fi hoặc ngoài vùng phủ sóng, thử lại nhé");}
 }else if(state==WifiState::Online){
  if(!radio.connected()){portal("Mất Wi-Fi, nối lại từ QR nhé");}
  else url="http://"+radio.address()+"/";
 }
}
bool Wifi::reset(){
 bool a=store.erase("wifi");
 portal(a?"Đã xóa Wi-Fi. Quét QR để nối lại":"Chưa xóa được Wi-Fi, giữ BOOT thử lại");return a;
}
Str Wifi::qr()const{return state==WifiState::Online?url:"WIFI:T:nopass;S:"+apName+";;";}
Vector directionVector(Direction d){
 switch(d){case Direction::Forward:return {1,0};case Direction::Back:return {-1,0};
 case Direction::Left:return {0,1};case Direction::Right:return {0,-1};
 case Direction::ForwardLeft:return {.70710678f,.70710678f};case Direction::ForwardRight:return {.70710678f,-.70710678f};
 case Direction::BackLeft:return {-.70710678f,.70710678f};case Direction::BackRight:return {-.70710678f,-.70710678f};default:return {0,0};}
}
bool parseDirection(const Str& s,Direction& d){
 const char* names[]={"stop","forward","back","left","right","fl","fr","bl","br"};
 for(int i=0;i<9;i++)if(s==names[i]){d=Direction(i);return true;}return false;
}
std::array<float,8> gait(Direction d,float phase){
 // One swing leg at a time (FL, RR, FR, RL). Sine lift, smooth half-cosine
 // hip return; slow stance sweep. Kame32's independent hip/knee oscillators
 // become a common phase accumulator instead of its blocking timed loop.
 std::array<float,8> out{};auto v=directionVector(d);if(d==Direction::Stop)return out;
 constexpr float offsets[4]={0,.5f,.75f,.25f};
 constexpr float sx[4]={1,1,-1,-1},sy[4]={1,-1,1,-1};
 for(int leg=0;leg<4;leg++){
  float p=phase-offsets[leg];p-=std::floor(p);
  float sweep=p<.25f?std::cos(pi*p*4):-std::cos(pi*(p-.25f)/.75f);
  // +angle CCW at a vertical shaft. Stance opposes body travel.
  float projection=(sy[leg]*v.x-sx[leg]*v.y)*.70710678f;
  out[leg*2]=cfg::hipAmplitude*projection*sweep;
  out[leg*2+1]=p<.25f?cfg::kneeAmplitude*std::sin(pi*p*4):0;
 }
 return out;
}
void Robot::begin(uint32_t now){
 bootTime=lastTick=now;enabled=0;ready=false;fault=false;direction=Direction::Stop;
 for(int i=0;i<8;i++){
  auto s=store.get("t"+std::to_string(i));char* end=nullptr;long value=std::strtol(s.c_str(),&end,10);
  trim[i]=!s.empty()&&end&&*end==0&&value>=-15&&value<=15?int(value):0;
  angle[i]=90+trim[i];velocity[i]=0;
 }
}
void Robot::network(bool up){linked=up;if(!up)direction=Direction::Stop;}
void Robot::hardwareFault(){fault=true;ready=false;direction=Direction::Stop;light=false;}
bool Robot::move(const Str& client,uint32_t seq,Direction d,uint32_t now){
 if(d==Direction::Stop)return stop(client,seq);
 if(!ready||fault||!linked||assembly||client.empty()||client.size()>48)return false;
 if(owner!=client){if(moving()&&elapsed(now,lastCommand)<cfg::heartbeatMs)return false;owner=client;hasSequence=false;}
 if(hasSequence&&seq<=lastSeq)return false;
 hasSequence=true;lastSeq=seq;lastCommand=now;direction=d;return true;
}
bool Robot::stop(const Str& client,uint32_t seq){
 // Every stop succeeds. Preserve a sequence barrier against delayed heartbeats.
 direction=Direction::Stop;
 if(owner==client&&(!hasSequence||seq>lastSeq)){hasSequence=true;lastSeq=seq;}
 return true;
}
void Robot::enterAssembly(){direction=Direction::Stop;assembly=true;rawCenter=false;}
void Robot::leaveAssembly(){direction=Direction::Stop;assembly=false;rawCenter=false;}
void Robot::center(){enterAssembly();rawCenter=true;}
bool Robot::adjust(int ch,int delta){
 if(!assembly||ch<0||ch>7||(delta!=1&&delta!=-1))return false;
 rawCenter=false;trim[ch]=std::max(-15,std::min(15,trim[ch]+delta));return true;
}
bool Robot::saveTrim(){
 if(!assembly)return false;
 for(int i=0;i<8;i++)if(!store.put("t"+std::to_string(i),std::to_string(trim[i])))return false;return true;
}
void Robot::resetTrim(){if(assembly){trim.fill(0);rawCenter=false;}}
void Robot::tick(uint32_t now){
 if(moving()&&(!linked||elapsed(now,lastCommand)>=cfg::heartbeatMs))direction=Direction::Stop;
 if(!fault&&enabled<8&&elapsed(now,bootTime)>=uint32_t(enabled)*cfg::servoEnableMs){enabled++;ready=enabled==8;}
 auto delta=elapsed(now,lastTick);if(delta<cfg::motionTickMs)return;lastTick=now;
 float dt=std::min(delta,50u)*.001f;
 if(moving())phaseMs=(phaseMs+std::min(delta,50u))%cfg::gaitPeriodMs;
 auto target=gait(direction,float(phaseMs)/cfg::gaitPeriodMs);
 for(int i=0;i<8;i++){
  float p=float(phaseMs)/cfg::gaitPeriodMs;constexpr float offsets[4]={0,.5f,.75f,.25f};
  p-=offsets[i/2];p-=std::floor(p);
  float cap=moving()&&p<.25f?cfg::swingRate:cfg::slowRate;
  float wanted=90+(rawCenter?0:trim[i])+(assembly?0:cfg::signs[i]*target[i]);
  wanted=clamp(wanted,90-cfg::maxJointDelta,90+cfg::maxJointDelta);
  float error=wanted-angle[i];
  // Proportional velocity with acceleration limit; no angle/velocity snap on stop.
  float desired=clamp(error*4,-cap,cap);
  velocity[i]+=clamp(desired-velocity[i],-cfg::acceleration*dt,cfg::acceleration*dt);
  float step=velocity[i]*dt;
  angle[i]=clamp(angle[i]+step,65,115);
  if(std::fabs(error)<.0001f&&std::fabs(velocity[i])<.01f){angle[i]=wanted;velocity[i]=0;}
 }
}
bool BootHold::update(bool down,uint32_t now){
 if(!down){held=fired=false;return false;}
 if(!held){since=now;held=true;}
 if(!fired&&elapsed(now,since)>=cfg::bootHoldMs){fired=true;return true;}return false;
}
int BootHold::remaining(uint32_t now)const{return held?std::max(0,8-int(elapsed(now,since)/1000)):8;}
Response Api::handle(const Request& r,uint32_t now){
 if(r.path=="/api/status"&&r.method=="GET"){
  Str body="{\"wifi\":"+jsonString(wifi.message)+",\"online\":"+(wifi.state==WifiState::Online?"true":"false")+",\"url\":"+jsonString(wifi.url)+",\"moving\":"+(robot.moving()?"true":"false")+",\"assembly\":"+(robot.assembly?"true":"false")+",\"ready\":"+(robot.isReady()?"true":"false")+",\"fault\":"+(robot.isFault()?"true":"false")+",\"light\":"+(robot.light?"true":"false")+",\"trim\":[";
  for(int i=0;i<8;i++){if(i)body+=",";body+=std::to_string(robot.trim[i]);}return {200,"application/json; charset=utf-8",body+"]}"};
 }
 if(r.method!="POST")return result(405,"Dùng POST cho lệnh này");
 if(r.path=="/api/wifi"){
  bool ok=wifi.submit(arg(r,"ssid"),arg(r,"password"),now);
  return result(ok?202:400,ok?"Đang nối Wi-Fi, xem QR trên màn hình":"Tên Wi-Fi hoặc mật khẩu chưa hợp lệ / đang kết nối");
 }
 if(r.path=="/api/move"||r.path=="/api/stop"){
  uint32_t seq=0;if(!unsignedNumber(arg(r,"seq"),seq))return result(400,"Lệnh không hợp lệ");
  auto client=arg(r,"client");if(client.empty()||client.size()>48)return result(400,"Lệnh không hợp lệ");
  if(r.path=="/api/stop"){robot.stop(client,seq);return result(200,"Đã dừng");}
  Direction d;if(!parseDirection(arg(r,"dir"),d))return result(400,"Hướng không hợp lệ");
  bool ok=robot.move(client,seq,d,now);return result(ok?200:409,ok?"Đã nhận":"Đã dừng / đang Ráp / chưa sẵn sàng");
 }
 if(r.path=="/api/light"){
  auto value=arg(r,"on");if(value!="0"&&value!="1")return result(400,"Lệnh đèn không hợp lệ");
  robot.light=value=="1"&&!robot.isFault();return result(200,robot.light?"Đèn bật":"Đèn tắt");
 }
 if(r.path=="/api/assembly"){
  auto op=arg(r,"op");
  if(op=="enter")robot.enterAssembly();else if(op=="exit")robot.leaveAssembly();
  else if(op=="center")robot.center();else if(op=="reset"&&robot.assembly)robot.resetTrim();
  else if(op=="save"){if(!robot.saveTrim())return result(409,"Chưa lưu được tâm");}
  else return result(400,"Lệnh Ráp không hợp lệ");return result(200,"Đã nhận lệnh Ráp");
 }
 if(r.path=="/api/trim"){
  uint32_t ch=0;auto delta=arg(r,"delta");
  if(!unsignedNumber(arg(r,"ch"),ch)||ch>7||(delta!="1"&&delta!="-1")||!robot.adjust(ch,delta=="1"?1:-1))return result(400,"Mở trang Ráp để chỉnh tâm");
  return result(200,"Đã chỉnh tâm");
 }
 return result(404,"Không có trang này");
}
}

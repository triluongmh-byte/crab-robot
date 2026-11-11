#pragma once
#include <stdint.h>
#include <cmath>
#include <algorithm>
// Open-loop estimates only: no encoder, homing, holding or positional gait.
namespace crab {
struct Continuous360 {
 static constexpr int MIN_COUNT=205,MAX_COUNT=409;
 static constexpr uint32_t MIN_MS=50,MAX_MS=500;
 static constexpr float MARGIN_DEG=5;
 enum class Viewpoint {Pending,HornFace,BodyTop};
 struct Rate {int counts=0;float degreesPerMs=0;bool calibrated=false;};
 struct Calibration {int stop=307,forward=267,reverse=347;bool confirmed=false;Rate cw,ccw;};
 Calibration channels[8];
 Viewpoint viewpoint=Viewpoint::Pending;
 bool opened=false,active=false,referenceValid=false,clipped=false;
 int channel=0,counts=0,emittedCounts=0,emittedChannel=-1,direction=0;
 float estimated[8]={},rate=0,requestedDegrees=0;
 uint32_t since=0,last=0,duration=200,requestedDuration=0,generation=0,accounted=0,requestedCap=MAX_MS;
 const char* reason="Chưa xác nhận đã đặt 90°.";
 static bool validCount(int c){return c>=MIN_COUNT&&c<=MAX_COUNT;}
 static float budget(int ch,int dir){
  if(ch<0||ch>7||(dir!=1&&dir!=2))return 0;
  if(ch%2)return 40-MARGIN_DEG;
  return ((ch<4)==(dir==1)?30:60)-MARGIN_DEG;
 }
 void stop(){active=false;referenceValid=false;reason="Đã tắt PWM; cần đặt lại và xác nhận 90°.";}
 void tick(uint32_t now){
  if(!active)return;
  uint32_t dt=std::min(uint32_t(now-since),duration);
  estimated[channel]+=(direction==1?1:-1)*rate*(dt-accounted);accounted=dt;
  if(uint32_t(now-since)>=duration||uint32_t(now-last)>=500){stop();reason="Hết thời gian / mất giữ lệnh; mốc 90° không còn hợp lệ.";}
 }
 bool configure(int ch,int neutral,int forward,int reverse){
  stop();if(ch<0||ch>7||!validCount(neutral)||!validCount(forward)||!validCount(reverse))return false;
  channel=ch;channels[ch]=Calibration{};channels[ch].stop=neutral;channels[ch].forward=forward;channels[ch].reverse=reverse;channels[ch].confirmed=true;return true;
 }
 bool setViewpoint(int value){
  stop();if(value<0||value>2)return false;
  viewpoint=static_cast<Viewpoint>(value);
  // A changed viewpoint cannot reuse direction observations.
  for(auto& c:channels){c.cw=Rate{};c.ccw=Rate{};}
  return true;
 }
 // Enter observations from a real unloaded test; recording calibration emits nothing.
 bool calibrate(int ch,int dir,int value,float degrees,uint32_t ms){
  stop();if(ch<0||ch>7||(dir!=1&&dir!=2)||!validCount(value)||!std::isfinite(degrees)||degrees<=0||degrees>180||ms<50||ms>60000||degrees/ms>1)return false;
  auto& c=channels[ch];if(!c.confirmed||(value!=c.forward&&value!=c.reverse)||value==c.stop){reason="Áp dụng count trước; hướng phải khác count dừng.";return false;}
  auto& r=dir==1?c.cw:c.ccw;const auto& other=dir==1?c.ccw:c.cw;
  if(other.calibrated&&other.counts==value){reason="Hai hướng không được dùng cùng count.";return false;}
  r.counts=value;r.degreesPerMs=degrees/ms;r.calibrated=true;return true;
 }
 bool confirmReference(){
  stop();if(!opened)return false;
  for(float& a:estimated)a=0;
  referenceValid=true;reason="Đã xác nhận đặt 90° bằng tay; góc chỉ là ước tính, có trôi.";return true;
 }
 bool refuse(const char* why){reason=why;return false;}
 bool start(int ch,int dir,uint32_t ms,uint32_t now){
  if(!opened||ch<0||ch>7||(dir!=1&&dir!=2)||ms<MIN_MS||ms>MAX_MS)return refuse("Lệnh hoặc thời gian ngoài giới hạn 50–500 ms.");
  if(!referenceValid)return refuse("Chưa xác nhận đã đặt 90°; đặt lại bằng tay rồi xác nhận.");
  if(!(ch%2)&&viewpoint==Viewpoint::Pending)return refuse("Góc nhìn CW của hông đang chờ xác nhận; không tự đảo chiều.");
  const Rate& r=dir==1?channels[ch].cw:channels[ch].ccw;
  if(!channels[ch].confirmed||!r.calibrated||!std::isfinite(r.degreesPerMs)||r.degreesPerMs<=0)return refuse("Chưa hiệu chỉnh kênh / hướng này.");
  if(active)return refuse("Đang có một kênh hoạt động; tắt trước khi đổi lệnh.");
  float remaining=budget(ch,dir)-(dir==1?estimated[ch]:-estimated[ch]);
  uint32_t available=remaining>0?uint32_t(std::floor(remaining/r.degreesPerMs)):0;
  if(available<MIN_MS)return refuse("Hết ngân sách hành trình (đã trừ biên 5°).");
  duration=std::min(ms,available);clipped=duration<ms;requestedDuration=ms;
  channel=ch;direction=dir;counts=r.counts;rate=r.degreesPerMs;since=last=now;accounted=0;generation++;active=true;
  reason=clipped?"Đã cắt thời gian theo ngân sách, biên 5°; góc chỉ là ước tính.":"Nhích thử có giới hạn; góc chỉ là ước tính, có trôi.";
  return true;
 }
 // Compatibility route also enforces reference/calibration/budget. Raw neutral
 // pulses are refused: a candidate stop count may still turn a continuous servo.
 bool hold(int ch,int action,uint32_t ms,uint32_t now,bool fresh){
  tick(now);
  if(ch<0||ch>7||action<1||action>2)return refuse("Dùng TẮT TẤT CẢ; count dừng không phải phanh.");
  int value=action==1?channels[ch].forward:channels[ch].reverse;
  int dir=channels[ch].cw.calibrated&&value==channels[ch].cw.counts?1:2;
  const Rate& r=dir==1?channels[ch].cw:channels[ch].ccw;
  if(!r.calibrated||r.counts!=value)return refuse("Chưa hiệu chỉnh kênh / hướng này.");
  if(fresh){requestedDegrees=0;return start(ch,dir,ms,now);}
  if(!validOutput()||ch!=channel||value!=counts||ms!=requestedDuration)return false;
  last=now;return true;
 }
 bool move(int ch,int dir,float degrees,uint32_t now,bool fresh,uint32_t cap=MAX_MS){
  tick(now);
  if(ch<0||ch>7||(dir!=1&&dir!=2)||!std::isfinite(degrees)||degrees<=0||degrees>60||cap<MIN_MS||cap>MAX_MS)return refuse("Chọn góc nhích thử 1–60° (ước tính).");
  if(!fresh){if(!validOutput()||ch!=channel||dir!=direction||degrees!=requestedDegrees||cap!=requestedCap)return false;last=now;return true;}
  const Rate& r=dir==1?channels[ch].cw:channels[ch].ccw;
  if(!r.calibrated||!std::isfinite(r.degreesPerMs)||r.degreesPerMs<=0)return refuse("Chưa hiệu chỉnh kênh / hướng này.");
  float planned=std::floor(degrees/r.degreesPerMs);
  if(planned<MIN_MS)return refuse("Góc yêu cầu nhỏ hơn xung thử tối thiểu 50 ms.");
  bool capped=planned>cap;
  if(!start(ch,dir,uint32_t(std::min(planned,float(cap))),now))return false;
  requestedDegrees=degrees;requestedCap=cap;clipped=clipped||capped;
  if(capped)reason="Đã cắt theo trần 500 ms / ngân sách; góc chỉ là ước tính.";
  return true;
 }
 bool validOutput()const{
  if(!opened||!active||!referenceValid||channel<0||channel>7||!validCount(counts)||duration<MIN_MS||duration>MAX_MS||(direction!=1&&direction!=2)||(!(channel%2)&&viewpoint==Viewpoint::Pending))return false;
  const auto& r=direction==1?channels[channel].cw:channels[channel].ccw;
  if(!r.calibrated||!channels[channel].confirmed||r.counts!=counts||!std::isfinite(rate)||rate<=0||rate!=r.degreesPerMs||accounted>duration||!std::isfinite(estimated[channel]))return false;
  float projected=estimated[channel]+(direction==1?1:-1)*rate*(duration-accounted);
  return estimated[channel]<=budget(channel,1)+.001f&&estimated[channel]>=-budget(channel,2)-.001f&&projected<=budget(channel,1)+.001f&&projected>=-budget(channel,2)-.001f;
 }
};
}

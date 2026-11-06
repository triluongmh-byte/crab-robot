// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "Config.h"
#include <array>
#include <map>
#include <string>
namespace crab {
using Str=std::string;
inline uint32_t elapsed(uint32_t now,uint32_t then){return now-then;}
struct Storage {
 virtual ~Storage()=default;
 virtual Str get(const Str& key)=0;
 virtual bool put(const Str& key,const Str& value)=0;
 virtual bool erase(const Str& key)=0;
};
struct Radio {
 virtual ~Radio()=default;
 virtual void accessPoint(const Str& ssid)=0;
 virtual void join(const Str& ssid,const Str& password)=0;
 virtual void stopAP()=0;
 virtual void disconnect()=0;
 virtual bool connected()=0;
 virtual Str address()=0;
};
enum class WifiState { Portal, Connecting, Online };
class Wifi {
 Storage& store; Radio& radio;
 uint32_t started=0; bool candidate=false;
 Str pendingSsid,pendingPassword;
 void portal(const Str& message);
 public:
 WifiState state=WifiState::Portal;
 Str apName, message, url="http://192.168.4.1/";
 Wifi(Storage& s,Radio& r,Str name):store(s),radio(r),apName(name){}
 void begin(uint32_t now);
 bool submit(const Str& ssid,const Str& password,uint32_t now);
 void tick(uint32_t now);
 bool reset();
 Str qr() const;
};
enum class Direction { Stop, Forward, Back, Left, Right, ForwardLeft, ForwardRight, BackLeft, BackRight };
struct Vector {float x,y;};
Vector directionVector(Direction d);
bool parseDirection(const Str& s,Direction& d);
std::array<float,8> gait(Direction d,float phase);
class Robot {
 Storage& store;
 std::array<float,8> velocity{};
 uint32_t bootTime=0,lastTick=0,lastCommand=0,phaseMs=0;
 uint32_t lastSeq=0; Str owner; bool hasSequence=false;
 uint8_t enabled=0;
 bool ready=false, linked=false, fault=false;
 Direction direction=Direction::Stop;
 public:
 bool assembly=false,rawCenter=false,light=false;
 std::array<int,8> trim{};
 std::array<float,8> angle{{90,90,90,90,90,90,90,90}};
 explicit Robot(Storage& s):store(s){}
 void begin(uint32_t now);
 void tick(uint32_t now);
 void network(bool up);
 void hardwareFault();
 bool move(const Str& client,uint32_t seq,Direction d,uint32_t now);
 bool stop(const Str& client,uint32_t seq);
 void enterAssembly();
 void leaveAssembly();
 void center();
 bool adjust(int channel,int delta);
 bool saveTrim();
 void resetTrim();
 bool moving()const{return direction!=Direction::Stop;}
 uint8_t enabledCount()const{return enabled;}
 bool isReady()const{return ready&&!fault;}
 bool isFault()const{return fault;}
 Direction currentDirection()const{return direction;}
};
class BootHold {
 uint32_t since=0; bool held=false,fired=false;
 public:
 bool update(bool down,uint32_t now);
 int remaining(uint32_t now)const;
};
struct Request {Str method,path; std::map<Str,Str> args;};
struct Response {int status;Str type,body;};
class Api {
 Robot& robot; Wifi& wifi;
 public:
 Api(Robot& r,Wifi& w):robot(r),wifi(w){}
 Response handle(const Request& req,uint32_t now);
};
Str jsonString(const Str& value);
bool unsignedNumber(const Str& value,uint32_t& out);
}

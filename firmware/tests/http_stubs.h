// Minimal host HTTP/radio/storage adapters. The handlers under test are shipped code.
#pragma once
#include <string>
#include <map>
#include <vector>
#include <functional>
#include <atomic>
#include <cstring>
#include <cassert>
#include <type_traits>
#include <sstream>
#include <iomanip>
class String:public std::string{
public:
 using std::string::string;
 String(const std::string& s):std::string(s){}
 template<typename T,typename std::enable_if<std::is_arithmetic<T>::value,int>::type=0>
 String(T n):std::string(std::to_string(n)){}
 String(float n,int places){std::ostringstream out;out<<std::fixed<<std::setprecision(places)<<n;assign(out.str());}
 bool startsWith(const char* p)const{return find(p)==0;}
 float toFloat()const{return std::stof(*this);}
 int toInt()const{return std::stoi(*this);}
};
constexpr int HTTP_GET=0,HTTP_POST=1,WL_CONNECTED=3,WL_CONNECT_FAILED=4,WL_NO_SSID_AVAIL=1;
constexpr int WIFI_SCAN_FAILED=-2,WIFI_SCAN_RUNNING=-1;
uint32_t clockMs=0;
uint32_t millis(){return clockMs;}
uint32_t esp_random(){return 42;}
int lockDepth=0;
struct Guard{Guard(){lockDepth++;}~Guard(){lockDepth--;}};
struct Servos{int offCalls=0;crab::ServoTelemetry samples[8];void snapshot(crab::ServoTelemetry (&out)[8])const{assert(lockDepth>0);for(int ch=0;ch<8;ch++)out[ch]=samples[ch];}bool disableOutputs(){assert(lockDepth>0);offCalls++;for(auto& s:samples){s.known=true;s.active=false;}return true;}} servos;
struct Server{
 std::map<std::string,std::function<void()>> handlers;
 std::map<std::string,String> args;
 std::function<void()> fallback;
 String currentUri,body;int code=0;
 void on(const char* path,int,std::function<void()> fn){handlers[path]=fn;}
 void onNotFound(std::function<void()> fn){fallback=fn;}
 void begin(){}
 String arg(const char* name){return args[name];}
 String uri(){return currentUri;}
 void sendHeader(const char*,const char*){}
 void send(int c,const char*,const String& s){assert(lockDepth==0);code=c;body=s;}
 void send_P(int c,const char* mime,const char* s){send(c,mime,s);}
 void request(const char* path,std::map<std::string,String> a={}){
  args=a;currentUri=path;body="";code=0;
  auto it=handlers.find(path);if(it==handlers.end())fallback();else it->second();
  assert(code!=0);
 }
} server;
struct Wifi{
 int state=0,apClients=1,beginCalls=0,disconnectCalls=0,scanCalls=0,scanState=WIFI_SCAN_FAILED;
 String ssid;std::vector<String> networks={"Nhà tôi","Nhà tôi","", "Other"};
 struct IP{String toString(){return "192.168.1.2";}};
 IP localIP(){return {};}
 int status(){return state;}
 int softAPgetStationNum(){return apClients;}
 void disconnect(bool off,bool erase){assert(!off&&!erase);disconnectCalls++;state=0;}
 void begin(const char* s,const char*){ssid=s;beginCalls++;state=0;}
 String SSID(){return ssid;}
 String SSID(int i){return networks.at(i);}
 int scanComplete(){return scanState;}
 void scanNetworks(bool async){assert(async);scanCalls++;scanState=WIFI_SCAN_RUNNING;}
 void scanDelete(){scanState=WIFI_SCAN_FAILED;}
} WiFi;
struct Store{
 std::map<std::string,String> data;
 size_t putString(const char* key,const String& s){data[key]=s;return s.length();}
 String getString(const char* key,const String& fallback){auto it=data.find(key);return it==data.end()?fallback:it->second;}
 size_t putBytes(const char*,const void*,size_t n){return n;}
 std::map<std::string,int32_t> ints;
 size_t putInt(const char* key,int32_t v){ints[key]=v;return 4;}
 int32_t getInt(const char* key,int32_t fallback){auto it=ints.find(key);return it==ints.end()?fallback:it->second;}
} wifiStore,trimStore,emoteStore;
struct Light{bool on=false;int r=-1,g=-1,b=-1;void set(bool v){on=v;}void color(int r_,int g_,int b_){r=r_;g=g_;b=b_;}} light;
crab::Motion motion;crab::Network network;
std::atomic<bool> driverReady(true),stationHasIp(false);
String candidateSsid,candidatePass,storedSsid,storedPass;
bool lightOn=false;uint32_t lightRgb=0xffffff;
std::atomic<uint8_t> staFail(0);uint32_t shownRgb=0xffffff;bool ledOverride=false;uint32_t ledAt=0;
crab::Mood emoteMood=crab::Mood::Normal;uint32_t moodAt=0;

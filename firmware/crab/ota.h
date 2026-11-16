#pragma once
#include <stdint.h>
#include <stddef.h>
#include "hardware.h"
// Firmware update over Wi-Fi (owner, 2026-11-16: run the crab on battery
// without the USB cable). The crab's own Wi-Fi is open and any page can take
// control, so an upload also needs a one-time PIN that only shows on the
// crab's screen: whoever flashes must be able to see the robot.
namespace crab {
// Every firmware image carries this text. An upload without it (another
// board's build, a random .bin) is refused before it can become bootable.
constexpr char OTA_MARKER[]="crab-ota-target=" CRAB_TARGET_NAME ";";
constexpr uint32_t OTA_PIN_MS=120000;   // PIN shown on the screen this long
constexpr uint32_t OTA_CONFIRM_MS=20000; // new firmware marks itself good after this uptime
namespace otamsg {
constexpr const char* OWNER="Mở lại trang để lấy quyền điều khiển rồi thử lại.";
constexpr const char* PIN="Mã sai hoặc hết hạn. Bấm Hiện mã để lấy mã mới.";
constexpr const char* TARGET="File này không phải firmware cua bản " CRAB_TARGET_NAME ". Bản cũ vẫn chạy.";
constexpr const char* WRITE="Ghi firmware lỗi. Bản cũ vẫn chạy.";
constexpr const char* EMPTY="Chưa nhận được file. Bản cũ vẫn chạy.";
}
// One PIN at a time, valid for OTA_PIN_MS, burnt by the first attempt.
struct OtaPin {
 uint32_t pin=0,at=0;bool armed=false;
 uint32_t issue(uint32_t now,uint32_t random){pin=100000+random%900000;at=now;armed=true;return pin;}
 bool shown(uint32_t now)const{return armed&&now-at<OTA_PIN_MS;}
 bool take(uint32_t guess,uint32_t now){const bool ok=shown(now)&&guess==pin;armed=false;return ok;}
};
// Streaming search for OTA_MARKER across upload chunks. Its first character
// occurs only once in it, so restarting a partial match at 0 or 1 is exact.
struct MarkerScan {
 size_t matched=0;bool found=false;
 void feed(const uint8_t* data,size_t n){
  constexpr size_t len=sizeof(OTA_MARKER)-1;
  for(size_t i=0;i<n&&!found;i++){
   const char c=char(data[i]);
   if(c==OTA_MARKER[matched]){if(++matched==len)found=true;}
   else matched=c==OTA_MARKER[0]?1:0;
  }
 }
};
// What happened to one upload, from the first chunk to the reply.
struct OtaUpload {
 bool accepted=false,ok=false;const char* why=nullptr;MarkerScan scan;
 bool writing()const{return accepted&&!ok&&!why;}
};
}

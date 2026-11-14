#pragma once
#include <Arduino.h>
#include "config.h"
#include "font_vi.h"
#include "qrcodegen.h"
#include "eyes.h"
#include <algorithm>
#include <cstdio>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_vendor.h>
#include <esp_heap_caps.h>
#if CRAB_INTEGRATED_BOARD
#include <driver/spi_master.h>
#include "waveshare_panel.h"
#endif
class Screen {
 esp_lcd_panel_handle_t panel=nullptr;
 esp_lcd_panel_io_handle_t io=nullptr;
 uint16_t* pixels=nullptr;
 SemaphoreHandle_t done=nullptr;
 static bool IRAM_ATTR transferred(esp_lcd_panel_io_handle_t,esp_lcd_panel_io_event_data_t*,void* arg){
  BaseType_t wake=pdFALSE;xSemaphoreGiveFromISR(static_cast<Screen*>(arg)->done,&wake);return wake==pdTRUE;
 }
 void pixel(int x,int y,bool black){put(x,y,black?0:0xffff);}
 void put(int x,int y,uint16_t c){if(x>=0&&x<320&&y>=0&&y<170)pixels[y*320+x]=c;}
 // Face colours are 0x0000/0xffff only: byte-order independent on both panels.
 static constexpr uint16_t INK=0xffff,PAPER=0x0000;
 void roundRect(int cx,int cy,int w,int h,int r){
  r=std::min(r,std::min(w,h)/2);const int hw=w/2-r,hh=h/2-r;
  for(int y=cy-h/2;y<cy+(h+1)/2;y++)for(int x=cx-w/2;x<cx+(w+1)/2;x++){
   const int dx=std::max(0,std::abs(x-cx)-hw),dy=std::max(0,std::abs(y-cy)-hh);if(dx*dx+dy*dy<=r*r)put(x,y,INK);}
 }
 void arch(int cx,int cy,int ro,int ri){for(int y=cy-ro;y<=cy;y++)for(int x=cx-ro;x<=cx+ro;x++){const int d=(x-cx)*(x-cx)+(y-cy)*(y-cy);if(d<=ro*ro&&d>=ri*ri)put(x,y,INK);}}
 int width(const char* s){int w=0;while(*s){uint32_t cp=utf8(s);if(const Glyph* g=glyph(cp))w+=g->advance;}return w;}
 const Glyph* glyph(uint32_t cp){for(const auto& g:GLYPHS)if(g.cp==cp)return &g;return nullptr;}
 uint32_t utf8(const char*& s){uint32_t c=(uint8_t)*s++;if(c<128)return c;int n=c<224?1:c<240?2:3;c&=(1<<(6-n))-1;while(n--&&*s)c=(c<<6)|((uint8_t)*s++&63);return c;}
 void text(const char* s,int x,int y,int right=319,uint16_t ink=0){const int left=x;while(*s){uint32_t cp=utf8(s);if(cp=='\n'){x=left;y+=19;continue;}const Glyph* g=glyph(cp);if(!g)continue;if(x+g->advance>right){x=left;y+=19;}if(y+20>170)break;for(int yy=0;yy<20;yy++)for(int xx=0;xx<16;xx++)if(g->rows[yy]&(1<<(15-xx)))put(x+xx,y+yy,ink);x+=g->advance;}}
 public:
 bool begin(){
  if(cfg::POWER_PIN>=0){digitalWrite(cfg::POWER_PIN,HIGH);pinMode(cfg::POWER_PIN,OUTPUT);}
#if !CRAB_INTEGRATED_BOARD
  pinMode(cfg::LCD_RD,OUTPUT);digitalWrite(cfg::LCD_RD,HIGH);
#endif
  pinMode(cfg::LCD_BL,OUTPUT);digitalWrite(cfg::LCD_BL,LOW);
  done=xSemaphoreCreateBinary();pixels=(uint16_t*)heap_caps_malloc(320*170*2,MALLOC_CAP_DMA|MALLOC_CAP_INTERNAL);
  if(!done||!pixels)return false;
#if CRAB_INTEGRATED_BOARD
  spi_bus_config_t b={};b.sclk_io_num=cfg::LCD_SCLK;b.mosi_io_num=cfg::LCD_MOSI;
  b.miso_io_num=-1;b.quadwp_io_num=-1;b.quadhd_io_num=-1;b.max_transfer_sz=320*170*2;
  if(spi_bus_initialize(SPI2_HOST,&b,SPI_DMA_CH_AUTO)!=ESP_OK)return false;
  esp_lcd_panel_io_spi_config_t c={};c.dc_gpio_num=cfg::LCD_DC;c.cs_gpio_num=cfg::LCD_CS;
  c.pclk_hz=cfg::LCD_SPI_HZ;c.spi_mode=0;c.trans_queue_depth=1;
  c.on_color_trans_done=transferred;c.user_ctx=this;c.lcd_cmd_bits=8;c.lcd_param_bits=8;
  if(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)SPI2_HOST,&c,&io)!=ESP_OK)return false;
#else
  esp_lcd_i80_bus_handle_t bus=nullptr;esp_lcd_i80_bus_config_t b={};
  b.dc_gpio_num=cfg::LCD_DC;b.wr_gpio_num=cfg::LCD_WR;b.clk_src=LCD_CLK_SRC_PLL160M;
  for(int i=0;i<8;i++)b.data_gpio_nums[i]=cfg::LCD_DATA[i];b.bus_width=8;b.max_transfer_bytes=320*170*2;
  if(esp_lcd_new_i80_bus(&b,&bus)!=ESP_OK)return false;
  esp_lcd_panel_io_i80_config_t c={};c.cs_gpio_num=cfg::LCD_CS;c.pclk_hz=16000000;c.trans_queue_depth=1;c.on_color_trans_done=transferred;c.user_ctx=this;c.lcd_cmd_bits=8;c.lcd_param_bits=8;c.dc_levels.dc_data_level=1;
  if(esp_lcd_new_panel_io_i80(bus,&c,&io)!=ESP_OK)return false;
#endif
  esp_lcd_panel_dev_config_t p={};p.reset_gpio_num=cfg::LCD_RST;p.color_space=ESP_LCD_COLOR_SPACE_RGB;p.bits_per_pixel=16;
  if(esp_lcd_new_panel_st7789(io,&p,&panel)!=ESP_OK)return false;
#if CRAB_INTEGRATED_BOARD
  // Match vendor reset timing. Keep BL low until the complete init succeeds.
  digitalWrite(cfg::LCD_RST,HIGH);pinMode(cfg::LCD_RST,OUTPUT);delay(100);
  digitalWrite(cfg::LCD_RST,LOW);delay(100);digitalWrite(cfg::LCD_RST,HIGH);delay(100);
  for(const auto& cmd:waveshare::INIT){
   if(esp_lcd_panel_io_tx_param(io,cmd.command,cmd.data,cmd.length)!=ESP_OK)return false;
   if(cmd.delayMs)delay(cmd.delayMs);
  }
  // Vendor landscape MADCTL 0x70, flipped 180 degrees per case D15 (xor 0xc0).
  const uint8_t rotation=waveshare::MADCTL;
  if(esp_lcd_panel_io_tx_param(io,0x36,&rotation,1)!=ESP_OK)return false;
  if(esp_lcd_panel_set_gap(panel,waveshare::GAP_X,waveshare::GAP_Y)!=ESP_OK)return false;
#else
  esp_lcd_panel_reset(panel);esp_lcd_panel_init(panel);esp_lcd_panel_invert_color(panel,true);
  esp_lcd_panel_swap_xy(panel,true);esp_lcd_panel_mirror(panel,false,true);esp_lcd_panel_set_gap(panel,0,35);
  esp_lcd_panel_disp_on_off(panel,true);
  // Official LILYGO factory's newer-panel sequence, selectable for older stock.
  if(cfg::LCD_NEW_PANEL){
   struct Cmd{uint8_t command,data[14],length;};
   const Cmd init[]={
    {0x11,{0},0x80},{0x3a,{0x05},1},{0xb2,{0x0b,0x0b,0,0x33,0x33},5},
    {0xb7,{0x75},1},{0xbb,{0x28},1},{0xc0,{0x2c},1},{0xc2,{1},1},
    {0xc3,{0x1f},1},{0xc6,{0x13},1},{0xd0,{0xa7},1},{0xd0,{0xa4,0xa1},2},
    {0xd6,{0xa1},1},
    {0xe0,{0xf0,5,0x0a,6,6,3,0x2b,0x32,0x43,0x36,0x11,0x10,0x2b,0x32},14},
    {0xe1,{0xf0,8,0x0c,0x0b,9,0x24,0x2b,0x22,0x43,0x38,0x15,0x16,0x2f,0x37},14}
   };
   for(const auto& cmd:init){
    if(esp_lcd_panel_io_tx_param(io,cmd.command,cmd.data,cmd.length&0x7f)!=ESP_OK)return false;
    if(cmd.length&0x80)delay(120); // setup only, before any servo starts
   }
  }
#endif
  digitalWrite(cfg::LCD_BL,HIGH);return true;
 }
 // Face: two pet eyes on black, one small status line at the bottom.
 static constexpr int EYE_W=58,EYE_H=86,EYE_GAP=52,EYE_Y=70,LOOK_PX=24,LINE_Y=150;
 // The bottom line must fit on one row (the font wraps, and the wrapped row
 // falls off the 170 px panel). Keep "message  address" when it fits, else the
 // address alone (the part needed to reach the crab), else the message alone.
 static constexpr int STATUS_MAX_PX=316;
 const char* statusLine(const char* message,const char* address,char* out,size_t n){
  snprintf(out,n,"%s%s%s",message,(*message&&*address)?"  ":"",address);
  if(width(out)<=STATUS_MAX_PX)return out;
  return *address?address:message;
 }
 bool face(const crab::EyeFrame& f,const char* message,const char* address){
  char both[192];return face(f,statusLine(message,address,both,sizeof both));
 }
 bool face(const crab::EyeFrame& f,const char* line){
  if(!panel)return false;
  for(int i=0;i<320*170;i++)pixels[i]=PAPER;
  for(int side:{-1,1}){
   const int cx=160+side*EYE_GAP+f.look*LOOK_PX;
   if(f.happy)arch(cx,EYE_Y+16,32,21);
   else roundRect(cx,EYE_Y,EYE_W,std::max(6,EYE_H*f.open/100),20);
  }
  const int w=width(line);text(line,std::max(2,(320-w)/2),LINE_Y,317,INK);
  if(esp_lcd_panel_draw_bitmap(panel,0,0,320,170,pixels)!=ESP_OK)return false;
  return xSemaphoreTake(done,pdMS_TO_TICKS(1000))==pdTRUE;
 }
 uint16_t at(int x,int y)const{return pixels[y*320+x];}
 bool show(const char* payload,const char* message,const char* address,const char* ap){
  if(!panel)return false;
  memset(pixels,255,320*170*2);
  uint8_t temp[qrcodegen_BUFFER_LEN_FOR_VERSION(5)],qr[qrcodegen_BUFFER_LEN_FOR_VERSION(5)];
  bool encoded=qrcodegen_encodeText(payload,temp,qr,qrcodegen_Ecc_MEDIUM,1,5,qrcodegen_Mask_AUTO,true);
  if(encoded){int n=qrcodegen_getSize(qr),scale=std::min(4,160/(n+8)),side=(n+8)*scale;
   int x0=(160-side)/2,y0=(170-side)/2;
   for(int y=0;y<n;y++)for(int x=0;x<n;x++)if(qrcodegen_getModule(qr,x,y))for(int j=0;j<scale;j++)for(int i=0;i<scale;i++)pixel(x0+(x+4)*scale+i,y0+(y+4)*scale+j,true);
  }
  text(message,164,2);text(address,164,64);text(ap,164,110);text("Giữ BOOT 8 giây\nđể xóa Wi-Fi",164,130);
  if(esp_lcd_panel_draw_bitmap(panel,0,0,320,170,pixels)!=ESP_OK)return false;
  return xSemaphoreTake(done,pdMS_TO_TICKS(1000))==pdTRUE;
 }
};

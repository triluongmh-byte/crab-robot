#pragma once
#include <algorithm>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <cassert>
#define IRAM_ATTR
#define pdFALSE 0
#define pdTRUE 1
#define ESP_OK 0
#define pdMS_TO_TICKS(x) (x)
#define LCD_CLK_SRC_PLL160M 0
#define ESP_LCD_COLOR_SPACE_RGB 0
using BaseType_t=int;
using SemaphoreHandle_t=int*;
using esp_lcd_panel_handle_t=void*;
using esp_lcd_panel_io_handle_t=void*;
using esp_lcd_i80_bus_handle_t=void*;
using esp_lcd_spi_bus_handle_t=void*;
struct esp_lcd_panel_io_event_data_t{};
using Callback=bool(*)(esp_lcd_panel_io_handle_t,esp_lcd_panel_io_event_data_t*,void*);
struct esp_lcd_i80_bus_config_t{int dc_gpio_num,wr_gpio_num,clk_src,data_gpio_nums[8],bus_width,max_transfer_bytes;};
struct esp_lcd_panel_io_i80_config_t{int cs_gpio_num,pclk_hz,trans_queue_depth;Callback on_color_trans_done;void* user_ctx;int lcd_cmd_bits,lcd_param_bits;struct{int dc_data_level;}dc_levels;};
struct esp_lcd_panel_io_spi_config_t{int dc_gpio_num,cs_gpio_num,pclk_hz,spi_mode,trans_queue_depth;Callback on_color_trans_done;void* user_ctx;int lcd_cmd_bits,lcd_param_bits;};
struct esp_lcd_panel_dev_config_t{int reset_gpio_num,color_space,bits_per_pixel;};
struct PanelCommand{int cmd;std::vector<uint8_t> bytes;};
static std::vector<PanelCommand> commands;
static esp_lcd_panel_io_spi_config_t spiConfig;
static esp_lcd_i80_bus_config_t parallelConfig;
static int spiCalls=0,i80Calls=0,gapX=-1,gapY=-1,draws=0,failCommand=-1;
static int semaphore=0;
static Callback colorDone=nullptr;static void* colorCtx=nullptr;
inline SemaphoreHandle_t xSemaphoreCreateBinary(){return &semaphore;}
inline void xSemaphoreGiveFromISR(SemaphoreHandle_t s,BaseType_t*){*s=1;}
inline int xSemaphoreTake(SemaphoreHandle_t s,int){int v=*s;*s=0;return v;}
inline void delay(unsigned){}
inline int esp_lcd_new_i80_bus(const esp_lcd_i80_bus_config_t* b,esp_lcd_i80_bus_handle_t* h){i80Calls++;parallelConfig=*b;*h=(void*)1;return 0;}
inline int esp_lcd_new_panel_io_i80(void*,const esp_lcd_panel_io_i80_config_t* c,void** h){colorDone=c->on_color_trans_done;colorCtx=c->user_ctx;*h=(void*)1;return 0;}
inline int esp_lcd_new_panel_io_spi(void*,const esp_lcd_panel_io_spi_config_t* c,void** h){spiCalls++;spiConfig=*c;colorDone=c->on_color_trans_done;colorCtx=c->user_ctx;*h=(void*)1;return 0;}
inline int esp_lcd_new_panel_st7789(void*,const esp_lcd_panel_dev_config_t*,void** h){*h=(void*)1;return 0;}
inline int esp_lcd_panel_reset(void*){return 0;}
inline int esp_lcd_panel_init(void*){return 0;}
inline int esp_lcd_panel_invert_color(void*,bool){return 0;}
inline int esp_lcd_panel_swap_xy(void*,bool){return 0;}
inline int esp_lcd_panel_mirror(void*,bool,bool){return 0;}
inline int esp_lcd_panel_set_gap(void*,int x,int y){gapX=x;gapY=y;return 0;}
inline int esp_lcd_panel_disp_on_off(void*,bool){return 0;}
inline int esp_lcd_panel_io_tx_param(void*,int cmd,const void* d,size_t n){const auto* bytes=(const uint8_t*)d;commands.push_back({cmd,std::vector<uint8_t>(bytes,bytes+n)});return cmd==failCommand?-1:0;}
inline int esp_lcd_panel_draw_bitmap(void*,int x,int y,int xe,int ye,const void*){assert(x==0&&y==0&&xe==320&&ye==170);draws++;colorDone(nullptr,nullptr,colorCtx);return 0;}

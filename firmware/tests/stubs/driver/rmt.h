#pragma once
#include <stdint.h>
#include <vector>
using gpio_num_t=int;
constexpr int RMT_MODE_TX=0,RMT_CHANNEL_0=0,RMT_IDLE_LEVEL_LOW=0,ESP_OK=0;
struct rmt_item32_t{int level0=0,duration0=0,level1=0,duration1=0;};
struct rmt_config_t{int rmt_mode,channel,gpio_num,clk_div,mem_block_num;struct{bool idle_output_en;int idle_level;}tx_config;};
extern rmt_config_t rmtCapture;extern std::vector<rmt_item32_t> rmtBits;
inline int rmt_config(rmt_config_t* c){rmtCapture=*c;return 0;}
inline int rmt_driver_install(int,int,int){return 0;}
inline int rmt_write_items(int,const rmt_item32_t* bits,int n,bool){rmtBits.assign(bits,bits+n);return 0;}

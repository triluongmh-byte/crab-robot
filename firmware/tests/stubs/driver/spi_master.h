#pragma once
#define SPI2_HOST 1
#define SPI_DMA_CH_AUTO 3
struct spi_bus_config_t{int sclk_io_num,mosi_io_num,miso_io_num,quadwp_io_num,quadhd_io_num,max_transfer_sz;};
static spi_bus_config_t spiBus;
inline int spi_bus_initialize(int host,const spi_bus_config_t* b,int dma){assert(host==SPI2_HOST&&dma==SPI_DMA_CH_AUTO);spiBus=*b;return 0;}

#pragma once
// Select at compile time; never detect/remap hardware from a running device.
#ifndef CRAB_INTEGRATED_BOARD
#define CRAB_INTEGRATED_BOARD 0
#endif
#if CRAB_INTEGRATED_BOARD != 0 && CRAB_INTEGRATED_BOARD != 1
#error "CRAB_INTEGRATED_BOARD must be 0 (LILYGO) or 1 (integrated)"
#endif
namespace cfg {
constexpr bool INTEGRATED_BOARD=CRAB_INTEGRATED_BOARD;
constexpr int SDA_PIN=18, SCL_PIN=17, LED_PIN=1, BOOT_PIN=0;
constexpr int USB_DM=19, USB_DP=20;
constexpr int LCD_BL=38, LCD_RST=5, LCD_CS=6, LCD_DC=7;
#if CRAB_INTEGRATED_BOARD
// Final U1.23 -> U3.23, R9 10k to 3V3. GPIO15 is physically NC.
constexpr int POWER_PIN=-1, PCA_OE_PIN=21;
constexpr bool LCD_SPI=true;
constexpr int LCD_SCLK=8, LCD_MOSI=39, LCD_SPI_HZ=10000000;
constexpr int LCD_WR=-1, LCD_RD=-1, LCD_DATA[8]={-1,-1,-1,-1,-1,-1,-1,-1};
constexpr int LCD_ROTATION_DEG=270; // vendor landscape 90 + case D15 180
constexpr const char* HARDWARE_TARGET="integrated";
#else
constexpr int POWER_PIN=15, PCA_OE_PIN=-1;
constexpr bool LCD_SPI=false;
constexpr int LCD_SCLK=-1, LCD_MOSI=-1, LCD_SPI_HZ=0;
constexpr int LCD_WR=8, LCD_RD=9, LCD_DATA[8]={39,40,41,42,45,46,47,48};
constexpr int LCD_ROTATION_DEG=90;
constexpr const char* HARDWARE_TARGET="lilygo";
#endif
constexpr bool LCD_NEW_PANEL=true; // LILYGO factory only; integrated uses Waveshare init
}

#pragma once
#include <stdint.h>
#include <stddef.h>
#define OUTPUT 1
#define HIGH 1
#define LOW 0
void digitalWrite(int pin,int value);
void pinMode(int pin,int mode);
inline void delayMicroseconds(unsigned){}

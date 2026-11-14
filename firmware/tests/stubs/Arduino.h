#pragma once
#include <stdint.h>
#include <stddef.h>
#define OUTPUT 1
#define HIGH 1
#define LOW 0
#define INPUT_PULLDOWN 9
#define CHANGE 3
#define ARDUINO_ISR_ATTR
void digitalWrite(int pin,int value);
void pinMode(int pin,int mode);
inline void delayMicroseconds(unsigned){}
int digitalRead(int pin);
uint32_t micros();
void attachInterruptArg(int pin,void (*fn)(void*),void* arg,int mode);
inline void noInterrupts(){}
inline void interrupts(){}

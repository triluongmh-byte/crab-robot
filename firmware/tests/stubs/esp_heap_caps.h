#pragma once
#define MALLOC_CAP_DMA 1
#define MALLOC_CAP_INTERNAL 2
inline void* heap_caps_malloc(size_t n,int){return malloc(n);}

#include <cstdint>

#include "robo.h"

uint8_t *vram;

// frame_buffer_base = 0x80000000
// Size = 1921024

extern "C" void KernelMain(uint64_t frame_buffer_base,
                           uint64_t frame_buffer_size) {
  vram = reinterpret_cast<uint8_t *>(frame_buffer_base);
  // 1dot 表示
  __asm__ volatile(
    "movl	vram(%eip), %edx\n\t"
    "movl	$0, 0(%edx)\n\t"
	 );
  __asm__ volatile(
    "movl	vram(%eip), %edx\n\t"
    "xorl %ecx, %ecx\n\t"
    "LOOP:\n\t"
    "movl	$0, (%edx,%ecx)\n\t"
    "addl $4, %ecx\n\t"
    "cmpl $1921024, %ecx\n\t"
    "jl LOOP\n\t"
	 );
  while (1)
    __asm__("hlt");
}

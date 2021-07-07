all: kernel.elf

CPPFLAGS=-I/home/watanabe/osbook/devenv/x86_64-elf/include/c++/v1 -I/home/watanabe/osbook/devenv/x86_64-elf/include -I/home/watanabe/osbook/devenv/x86_64-elf/include/freetype2 -I/home/watanabe/edk2/MdePkg/Include -I/home/watanabe/edk2/MdePkg/Include/X64 -nostdlibinc -D__ELF__ -D_LDBL_EQ_DBL -D_GNU_SOURCE -D_POSIX_TIMERS -DEFIAPI='__attribute__((ms_abi))'

LDFLAGS=-L/home/watanabe/osbook/devenv/x86_64-elf/lib

kernel.elf: main.cpp
	clang++ -O2 $(CPPFLAGS) -Wall -g --target=x86_64-elf -ffreestanding -mno-red-zone -fno-exceptions -fno-rtti -std=c++17 -c main.cpp
	ld.lld $(LDFLAGS)  --entry KernelMain -z norelro --image-base 0x100000 --static -o kernel.elf main.o


clean:
	rm -f main.o kernel.elf disk.img
	rm -rf mnt

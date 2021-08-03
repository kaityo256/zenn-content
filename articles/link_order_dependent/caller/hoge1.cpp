#include "caller.h"
#include <cstdio>

struct Hoge1 : public Callee {
  void func() {
    puts("Hello from Hoge1!");
  }
};

Hoge1 hoge1;

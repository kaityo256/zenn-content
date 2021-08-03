#include "caller.h"
#include <cstdio>

struct Hoge2 : public Callee {
  void func() {
    puts("Hello from Hoge2!");
  }
};

Hoge2 hoge2;

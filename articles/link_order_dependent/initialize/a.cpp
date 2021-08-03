#include "a.h"
#include <cstdio>

A &A::get_instance() {
  static A a;
  return a;
}

struct A_initializer {
  A_initializer() {
    A::get_instance().init();
  }
};

A_initializer ai;

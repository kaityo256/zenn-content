#include "a.h"

struct B {
  B() {
    puts("Hello from B!");
    A a = A::get_instance();
    a.buf[3] = 12345;
  }
};

B b;

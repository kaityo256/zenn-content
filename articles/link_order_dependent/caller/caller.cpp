#include "caller.h"

Caller &Caller::get_instance() {
  static Caller c;
  return c;
}

void Caller::call_all() {
  for (auto c : v) {
    c->func();
  }
}

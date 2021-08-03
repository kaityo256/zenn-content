#include <cstdio>
class A {
public:
  static A &get_instance();
  void init() {
    buf = new int(10);
    puts("A is initialized");
  }
  int *buf;

private:
  A(){};
};

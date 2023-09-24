#include <stdio.h>

int a = 0;
int f() {
  a += 1;
  return a;
}
int g() {
  a *= 2;
  return a;
}
int h(int a1, int a2) {
  return a1 * a2;
}

int main() {
  a = h(f(), g());
  for (int i = 0; i < 16; i++) {
    if (i % (a + 3) == 0) {
      printf("%s\n", a ? "buzz" : "fizz");
    } else {
      printf("%d\n", i);
    }
  }
}
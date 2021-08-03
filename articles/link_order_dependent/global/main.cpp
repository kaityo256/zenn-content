#include <cstdio>

extern int a, b, _ZL1c;
void printc();

int main() {
  printf("a: %p\n", &a);
  printf("b: %p\n", &b);
  printc();
}

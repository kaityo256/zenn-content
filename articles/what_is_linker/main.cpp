#include <cstdio>

int a = 1;
int b = 2;

int add(int, int);

int main() {
  int c = add(a, b);
  printf("%d\n", c);
  printf("add :%p\n", add);
  printf("main:%p\n", main);
}

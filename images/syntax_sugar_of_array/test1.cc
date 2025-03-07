#include <cstdio>
#include <typeinfo>

void func1(int a[2][3]) {
  printf("func1: %s\n", typeid(a).name());
}

void func2(int (&a)[2][3]) {
  printf("func2: %s\n", typeid(a).name());
}

void func3(int a[][3]) {
  printf("func3: %s\n", typeid(a).name());
}

int main() {
  int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
  printf("main:  %s\n", typeid(a).name());
  func1(a);
  func2(a);
  func3(a);
}

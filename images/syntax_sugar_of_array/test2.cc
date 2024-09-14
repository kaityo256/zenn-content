#include <cstdio>
#include <typeinfo>

const int N = 4;

void func1(int a[N]) {
  printf("%s\n", typeid(a).name());
  a[N] = 1;
}

void func2(int a[]) {
  printf("%s\n", typeid(a).name());
  a[N] = 1;
}

void func3(int *a) {
  printf("%s\n", typeid(a).name());
  a[N] = 1;
}

void func4(int (&a)[N]) {
  printf("%s\n", typeid(a).name());
  a[N] = 1;
}

int main() {
  int a[N] = {1, 2, 3, 4};
  func1(a);
  func2(a);
  func3(a);
  func4(a);
}
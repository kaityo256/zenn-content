#include <cstdio>
#include <typeinfo>

int main() {
  int a[2][3][4];
  printf("%s\n", typeid(a).name());
}
#include <cstdio>
#include <typeinfo>

void func1(int a[2][3]) {
  printf("%s\n", typeid(a).name());
}

void func2(int (&a)[2][3]) {
  printf("%s\n", typeid(a).name());
}

void func3(int a[][3]) {
  printf("%s\n", typeid(a).name());
}

void show(int (&a)[2][3]) {
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 3; j++) {
      //printf("%d ", a[i][j]);
      //printf("%d ", *(a[i] + j));
      printf("%d ", *(*(a + i) + j));
    }
    printf("\n");
  }
}

int main() {
  int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
  func1(a);
  func2(a);
  func3(a);
  show(a);
}

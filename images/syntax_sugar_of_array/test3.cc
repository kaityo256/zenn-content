#include <cstdio>

int main() {
  int a[] = {1, 2, 3};
  printf("%d\n", *a);       // => 1
  printf("%d\n", *(a + 1)); // => 2
  printf("%d\n", *(a + 2)); // => 3

  printf("%p\n", a);
  printf("%p\n", a + 1);

  for (int i = 0; i < 3; i++) {
    printf("%d\n", i[a]); // => 1, 2, 3
  }
}
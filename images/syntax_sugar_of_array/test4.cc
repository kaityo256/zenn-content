#include <cstdio>

int main() {
  int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
  printf("%p\n", a);     // => 0x7fff70ae4a40
  printf("%p\n", a + 1); // => 0x7fff70ae4a4c
  printf("%p\n", a[0]);  // => 0x7fff70ae4a40
  printf("%p\n", a[1]);  // => 0x7fff70ae4a4c

  printf("%d\n", a[1][2]);
  printf("%d\n", (*(a + 1))[2]);
  printf("%d\n", *(*(a + 1) + 2));
}

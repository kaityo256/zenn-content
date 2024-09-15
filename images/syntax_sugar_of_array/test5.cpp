#include <cstdio>

template <size_t M, size_t N>
void show(int (&a)[M][N]) {
  for (int i = 0; i < M; i++) {
    for (int j = 0; j < N; j++) {
      printf("%d ", a[i][j]);
    }
    printf("\n");
  }
}

int main() {
  int a[2][3] = {{1, 2, 3}, {4, 5, 6}};
  int b[2][2] = {{1, 2}, {3, 4}};
  printf("a = \n");
  show(a);
  printf("b = \n");
  show(b);
}

---
title: "続：未定義動作でFizzBuzz"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp","gcc","clang"]
published: true
---

## はじめに

たまにFizzBuzzが話題になりますね。いろんな解法があると思いますが、ここではC/C++言語の未定義動作を使ってFizzBuzzしてみましょうか。[未定義動作でFizzBuzz](https://zenn.dev/kaityo256/articles/fizzbuzz_undefined)ではclang++にfizzを、g++にbuzzを表示してもらいましたが、今回はどちらもコンパイルはgccに任せつつ、環境で結果が変わるコードを書いてみます。とりあえずx86ならfizzを、ARMならbuzzを表示してもらうことにしましょう。

## コード

以下がコードです。

```c
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
```

実行結果はこんな感じになります。

### x86

普通にx86のgccを使うと3の倍数の時だけfizzが表示されます。

```sh
$ gcc test.cc

fizz
1
2
fizz
4
5
fizz
7
8
fizz
10
11
fizz
13
14
fizz
```

### AARCH64

ARMでコンパイル、実行すると5の倍数の時だけbuzzと言います。手元にARMのマシンがなかったのでクロスコンパイルしてQEMUで実行します。

```sh
$ aarch64-linux-gnu-gcc -static test.cc
$ ./a.out
buzz
1
2
3
4
buzz
6
7
8
9
buzz
11
12
13
14
buzz
```

ちなみにQEMUが入っていると、クロスコンパイルされた実行バイナリを検出して自動でエミュレートしてくれるので、そのまま`./a.out`で実行できます。

## 原理

何か環境依存するコードがあって、整数`a`が、ある環境なら`0`に、別の環境になら`2`にするようにできれば、あとは

```c
  for (int i = 0; i < 16; i++) {
    if (i % (a + 3) == 0) {
      printf("%s\n", a ? "buzz" : "fizz");
    } else {
      printf("%d\n", i);
    }
  }
```

でいいわけですね。なので環境依存で0と2を作ればいいだけです。

さて、C言語では副作用を持つ処理を関数の複数の引数として渡すと、その実行順序は保証されません。したがって、

```c
a = h(f(), g());
```

みたいなコードを書いたとき、先に`f()`が実行されるか、`g()`が実行されるかは処理系依存になります。それを利用します。

グローバルな変数`a`を0に初期化しておき、`f()`が`a`に1を足す処理を、`g()`が`a`を2倍する処理をします。

すると、x86のgccは、引数に渡された関数を後ろから処理するので、

```c
int h(int a1, int a2) {
  // a1 = 0, a2 = 1
  return a1 * a2; // 0
}
```

と0を返します。逆に、ARMのgccは前から処理するので、

```c
int h(int a1, int a2) {
  // a1 = 1, a2 = 2
  return a1 * a2; // 2
}
```

となり、2を返します。これで環境により変数が0になったり2になったりするコードが作れました。

ちなみに、副作用を持つ関数の引数をどちらから処理するかはgccとclangでも意見がわかれます。なので、

```c
$ gcc test.cc
$ ./a.out
fizz
1
2
fizz
4
5
fizz
7
8
fizz
10
11
fizz
13
14
fizz

$ clang test.cc
$ ./a.out
buzz
1
2
3
4
buzz
6
7
8
9
buzz
11
12
13
14
buzz
```

と、gccとclangでも異なる結果になります。

いや、それだけの話しなんですけど。

## 参考

* [未定義動作でFizzBuzz](https://zenn.dev/kaityo256/articles/fizzbuzz_undefined)
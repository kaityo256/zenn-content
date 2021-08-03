---
title: "実行結果がリンクの順番に依存するコード"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp"]
published: false
---

## はじめに

以前[リンカのお仕事](https://zenn.dev/kaityo256/articles/what_is_linker)という記事を書きました。関数やグローバル変数のアドレスは、コンパイル時にはとりあえずラベルとして定義され、そのアドレスはリンク時にリンカが決めます。その際、リンクの順番によりアドレスが変わります。その結果、リンクの順番により実行結果が変わるようなコードが書けます。それについてちょっとだけ説明しようと思います。

## グローバル変数

関数の外で宣言された変数はグローバル変数となります。何も指定しなければ、それはグローバルシンボルとなり、別のファイルからもアクセスできます。コンパイラに「実体が別のオブジェクトファイルにあるよ」と教えるには`extern`宣言を使います。


`main.cpp`

```cpp
#include <cstdio>

extern int a, b;

int main() {
  printf("a: %p\n", &a);
  printf("b: %p\n", &b);
}
```

`a`、`b`の実体をそれぞれ`a.cpp`、`b.cpp`に書いてやりましょう。

```cpp
int a = 1;
```

```cpp
int b = 1;
```

コンパイル、実行します。

```sh
$ g++ main.cpp a.cpp b.cpp
$ ./a.out
a: 0x55b27b601010
b: 0x55b27b601014
```

`a`と`b`のアドレスの下3桁が`010`と`014`になっていることに注意しましょう。`readelf`で`a.out`を見てみます。

```sh
$ readelf -s a.out | grep OBJECT
(snip)
    51: 0000000000004014     4 OBJECT  GLOBAL DEFAULT   25 b
(snip)
    63: 0000000000004010     4 OBJECT  GLOBAL DEFAULT   25 a
```

`a`と`b`のアドレスが4010、4014と、下3桁がさっきの結果と一致していますね。

さて、これらのグローバル変数のアドレスを決めるのはリンカで、リンカは原則として渡されたオブジェクトファイルの順番通りにくっつけるので、順序を入れ替えるとアドレスも入れ替わります。

```sh
$ g++ main.cpp b.cpp a.cpp
$ ./a.out
a: 0x564c18c36014
b: 0x564c18c36010
```

`a`と`b`のアドレスの順序が入れ替わりました。

なお、グローバル変数をそのファイルの中でのみ使い、他のオブジェクトファイルから参照されたくない場合は`static`をつけます。こんな`c.cpp`ファイルを作ってみましょう。

```cpp
#include <cstdio>
static int c = 1;

void printc() {
  printf("c: %p\n", &c);
}
```

`static`宣言をしたので、このグローバル変数`c`は外から参照できないはずです。確かめてみましょう。`main.cpp`をこのように書き換えます。

```cpp
#include <cstdio>

extern int a, b, c;

int main() {
  printf("a: %p\n", &a);
  printf("b: %p\n", &b);
  printf("c: %p\n", &c);
}
```

コンパイルは問題なくできますが、リンク時に怒られます。

```cpp
$ g++ -c main.cpp a.cpp b.cpp c.cpp
$ g++ main.o a.o b.o c.o
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x3b): undefined reference to `c'
collect2: error: ld returned 1 exit status
```

しかし、`c`はグローバル変数なので、どこかのアドレスにはあります。それを表示させてみましょう。そのために`c.cpp`に`printc`という関数を用意しておきました。`main.cpp`を以下のように書き換えます。

```cpp
#include <cstdio>

extern int a, b;
void printc();

int main() {
  printf("a: %p\n", &a);
  printf("b: %p\n", &b);
  printc();
}
```

コンパイル、実行してみましょう。

```cpp
$ g++ -c main.cpp a.cpp b.cpp c.cpp
$ g++ main.o a.o b.o c.o
$ ./a.out
a: 0x5561e1a7d010
b: 0x5561e1a7d014
c: 0x5561e1a7d018
```

4バイトずつ順番に配置されていますね。readelfで見てみましょう。

```sh
$ readelf -s a.out | grep OBJECT
    40: 0000000000004018     4 OBJECT  LOCAL  DEFAULT   25 _ZL1c
(snip)
    53: 0000000000004014     4 OBJECT  GLOBAL DEFAULT   25 b
(snip)
    65: 0000000000004010     4 OBJECT  GLOBAL DEFAULT   25 a
```

`a`や`b`にGLOBALという指定があるのに対して、`c`は名前がマングリングされ、さらにLOCAL指定がついています。これにより、他のグローバル変数と同じ領域に配置されつつ、他のオブジェクトファイルから参照できないようになっています。当然、リンク順序を入れ替えれば場所も変わります。

```cpp
$ g++ main.o c.o a.o b.o 
$ ./a.out
a: 0x561f4bfce014
b: 0x561f4bfce018
c: 0x561f4bfce010
```

c,a,bの順番でリンクしたので、アドレスもc,a,bの順番に配置されています。

## リンクの順序に依存して実行結果が変わるコード

グローバル変数のアドレスがリンクの順序に依存することを見ました。その結果、グローバル変数として定義されたクラスのインスタンスの初期化の順番もリンクの順序に依存することになります。それを見てみましょう。


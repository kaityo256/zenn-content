---
title: "実行結果がリンクの順番に依存するコード"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp"]
published: true
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

関数を登録して、後でその関数をまとめて実行するためのクラス`Caller`と、そのクラスに関数を登録するためのクラス`Callee`を定義してみましょう。

まずは`caller.h`はこんな感じです。

```cpp
#include <vector>

struct Callee;

class Caller {
public:
  void add(Callee *c) {
    v.push_back(c);
  }
  void call_all();
  static Caller &get_instance();

private:
  std::vector<Callee *> v;
  Caller(){};
};

struct Callee {
  virtual void func() = 0;
  Callee() {
    Caller::get_instance().add(this);
  }
};
```

Callerクラスは、Calleeクラスのインスタンスの配列を持っていて、`call_all`で登録された関数を全て呼び出します。また、シングルトンパターンにより、`Caller`クラスのインスタンスを一つに限定し、`Caller::get_instance()`で取得できるようにしておきます。Calleeクラスは、コンストラクタで`Caller::get_instance()`を使って`Caller`のインスタンスを取得し、自分を登録します。

Callerクラスのインスタンスは`caller.cpp`に定義された`get_instance`関数のstaticなローカル変数として定義しておきます。`call_all`もここで定義しておきましょう。

`caller.cpp`

```cpp
#include "caller.h"

Caller &Caller::get_instance() {
  static Caller c;
  return c;
}

void Caller::call_all() {
  for (auto c : v) {
    c->func();
  }
}
```

main関数では、`Caller::get_instance().call_all()`を呼び出すだけです。

`main.cpp`

```cpp
#include "caller.h"

int main() {
  Caller::get_instance().call_all();
}
```

コンパイル、実行してみましょう。

```cpp
$ g++ -c main.cpp caller.cpp
$ g++ main.o caller.o
$ ./a.out
```

何も登録していないので、何もおきません。

さて、関数を登録するためのファイルを作りましょう。こんな`hoge1.cpp`を作ります。

```cpp
#include "caller.h"
#include <cstdio>

struct Hoge1 : public Callee {
  void func() {
    puts("Hello from Hoge1!");
  }
};

Hoge1 hoge1;
```

Calleeクラスを継承したHoge1クラスを作って、そのインスタンスをグローバル変数として定義しています。この`Hoge1 hoge1`が初期化された際、Callerクラスにこの関数が登録されます。コンパイル、リンクしてみましょう。コンパイルするのは`hoge1.cpp`だけです。

```cpp
$ g++ -c hoge1.cpp
$ g++ main.o caller.o hoge1.o
$ ./a.out
Hello from Hoge1!
```

`main`関数を再コンパイルすることなく、新たにオブジェクトファイルをリンクするだけで、その実行結果を変えることができました。

関数は後からいくつでも追加できます。

`hoge2.cpp`

```cpp
#include "caller.h"
#include <cstdio>

struct Hoge2 : public Callee {
  void func() {
    puts("Hello from Hoge2!");
  }
};

Hoge2 hoge2;
```

```sh
$ g++ -c hoge2.cpp
$ g++ main.o caller.o hoge1.o hoge2.o
$ ./a.out
Hello from Hoge1!
Hello from Hoge2!
```

このように、グローバル変数の初期化をうまく使うことで、既存のコードを修正、再コンパイルすることなく、機能を追加することができます。

ただし、グローバル変数の初期化を利用しているため、実行結果は初期化の順番に依存します。

```sh
$ g++ main.o caller.o hoge2.o hoge1.o
$ ./a.out
Hello from Hoge2!
Hello from Hoge1!
```

## 初期化順序が守られないと困るコード

グローバル変数のアドレスはリンカが決めるため、リンクの順番に依存します。また、グローバル変数として定義されたインスタンスの初期化順序もリンクの順番に依存することになります。すると、例えば`A`というインスタンスが初期化されてから`B`というインスタンスが初期化されなければならないのに、リンクの順序が変わってバグる、なんてことがおきます。それを見てみましょう。ちょっとわざとらしいコードになっていますが、例ということで気にしないでください。

シングルトンパターンを実装したクラスAを用意します。こいつにはpublicな配列として`int *buf`があり、`A::init`で初期化されることとしましょう。

`a.h`

```cpp
#include <cstdio>
class A {
public:
  static A &get_instance();
  void init() {
    buf = new int(10);
    puts("A is initialized");
  }
  int *buf;

private:
  A(){};
};
```

このシングルトンを初期化するため、`A_initializer`というクラスを作り、そのコンストラクタで`A::init`を呼び出すことにします。

`a.cpp`

```cpp
#include "a.h"
#include <cstdio>

A &A::get_instance() {
  static A a;
  return a;
}

struct A_initializer {
  A_initializer() {
    A::get_instance().init();
  }
};

A_initializer ai;
```

これにより、グローバル変数`A_initializer`が初期化されたタイミングで、`A`が初期化されることになります。

何もしないmain関数を作ります。

`main.cpp`

```cpp
#include "a.h"

int main(){
}
```

コンパイル、実行してみましょう。

```sh
$ g++ main.cpp a.cpp
$ ./a.out
A is initialized
```

main関数は何にもしませんが、`A_initiazlier`が初期化されたタイミングで`A::init`が呼ばれています。

さて、この`A::buf`を使うクラスを作って追加してみましょう。

`b.cpp`

```cpp
#include "a.h"

struct B {
  B() {
    puts("Hello from B!");
    A a = A::get_instance();
    a.buf[3] = 12345;
  }
};

B b;
```

コンストラクタで`A`のインスタンスを手に入れ、`A::buf`をさわるだけのコードです。コンパイル、実行します。

```sh
$ g++ main.cpp a.cpp b.cpp
$ ./a.out
A is initialized
Hello from B!
```

`A`が初期化された後に`B`が触りにいっているので問題はおきません。しかし、リンクの順番を変えると当然バグります。

```sh
$ g++ main.cpp b.cpp a.cpp
Hello from B!
zsh: segmentation fault  ./a.out
```

`A`が初期化される前に`B`のインスタンスが作られ、それが`A`を触りにいってしまったためです。

## まとめ

分割コンパイル時のグローバル変数のアドレスはリンクの順番に依存し、それに伴ってグローバル変数として定義されたインスタンスの初期化順序もリンクの順序に依存します。リンクの順序に依存して振る舞いが変わるコードは、当然のことながら思わぬバグを引き起こします。例えばGNU MakefileをCMakeに置き換えたらバグった、ファイル名を変えただけでバグった、なんてイヤなバグり方をします。上記で挙げた例はあまり良くない例であり、現在はこういう書き方をする人は少ないと思いますが、たまに外部デバイスを触るコードなどでこういう書き方をするコードを見かけたりします。「リンクの順番を変えたら動作がおかしくなった」なんて現象に出会ったら、「グローバル変数の初期化順序の問題かも」と思えると、沼にハマる時間が短くなるかもしれません。本稿が、将来「沼」にハマった人の脱出に役立つことを願っています。

## 参考文献

* [リンカのお仕事](https://zenn.dev/kaityo256/articles/what_is_linker)
* [実践的低レイヤプログラミング](https://tanakamura.github.io/pllp/docs/)の[リンカの章](https://tanakamura.github.io/pllp/docs/linker.html) リンカが何をしているか詳しく書いてあるのでざっと読んでおくと良いことがあるかも。
---
title: "インクリメント演算子のコンパイラの気持ち"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["C","GCC","clang","LLVM"]
published: false
---

## はじめに

突然ですがクイズです。以下のコードの実行結果はどうなるでしょうか？

```c
#include <stdio.h>

int main(){
  int a = 1;
  int b = ++a + ++a + ++a;
  printf("%d\n",b);
}
```

結果は処理系に依存し、gccなら10に、clangなら9になります。これが未定義動作なのか処理系定義なのか、それとも他の何かは仕様警察に任せるとして、gccやclangはこれをどう解釈したの、その気持ちを探ってみようと思います。

なお、以下は中間コードその他から僕が勝手にコンパイラの気持ちを推し量ったものであり、正確性については保証しません。

## インクリメント演算子

`++`というインクリメント演算子は、変数に1を加算するものです。`++a`や`a++`のように、前に付ける場合と後ろにつける場合で、代入にたいする振る舞いが変わります。

前につける場合、インクリメントは代入の前に行われます。例えば、

```c
int a = 1;
int b = ++a;
```

と書いた時には、

```c
int a = 1;
a = a + 1
int b = a;
```

と等価です。したがって`b=2`になります。

後ろにつけた場合は、インクリメントは代入の後に行われます。したがって、

```c
int a = 1;
int b = a++;
```

は

```c
int a = 1;
int b = a;
a = a + 1
```

と等価であり、`b=1`になります。

さて、このインクリメント演算子は、しばしば問題を引き起こします。例えば加算の両側に現れた場合、その解釈に曖昧さが現れるからです。

以下の例を考えましょう。

```c
int a = 1;
int b = ++a + ++a;
```

このとき、`b`の値はいくつになるべきでしょうか？この時既に、gccとclangで意見が食い違います。gccは6、clangは5と解釈します。これがどういうことなのかを見てみましょう、というのがこの記事の目的です。

## clangの気持ち

clangの気持ちを見るには、LLVM中間コードを見るのが手っ取り早いです。

例えばこんなコードを書いてみます。

```c
int func(int a){
  return ++a;
}
```

このLLVM中間コードを見てやりましょう。

```sh
clang -emit-llvm -S test.c
```

すると、`test.ll`ができるので中身を見てやります。

```txt
; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @func(i32 %0) #0 {
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  %3 = load i32, i32* %2, align 4
  %4 = add nsw i32 %3, 1
  store i32 %4, i32* %2, align 4
  ret i32 %4
}
```

ごちゃごちゃしていますが、ゆっくり眺めると、インクリメント演算子を一時変数に受けて、代入はその一時変数の値を使うことがわかります。つまり、

```c
int b = ++a;
```

は、

```c
int tmp = a + 1;
a = tmp;
int b = tmp;
```

という解釈をします。これがわかるのが、LLVMの最後の`store`です。先程のLLVMをCっぽく書くと、

```c
int func(int a){
  int tmp = a + 1;
  a = tmp;
  return tmp;
}
```

となります。`a`は使われないのに、`a=tmp`という代入文があります。それに対応しているのが`store i32 %4, i32* %2, align 4`です。

さて、`++a`が`int tmp=a+1;a=tmp`に変換されるとわかると、clangの「気持ち」が理解できます。

以下のコードを考えましょう。

```c
int a = 1;
int b = ++a + ++a;
```

`++a`は、一時変数`tmp = a + 1;`に変換され、`++a`の値として`tmp`を使う、というルールから、まず左側の`++a`はこのように変換されます。

```c
int a = 1;
int tmp1 = a + 1;
a = tmp1;
int b = tmp1 + ++a;
```

右側の`++a`も同様に変換されます。

```c
int a = 1;
int tmp1 = a + 1;
a = tmp1;
int tmp2 = a + 1;
a = tmp2;
int b = tmp1 + tmp2;
```

この動作を追うと、`tmp1=2`、`tmp2=3`になるため、結果は`2 + 3 = 5`になります。

全く同様にして、

```c
int a = 1;
int b = ++a + ++a + ++a;
```

は、

```c
int a = 1;
int tmp1 = a + 1; // tmp1 = 2
a = tmp1;
int tmp2 = a + 1; // tmp2 = 3
a = tmp2;
int tmp3 = a + 1; // tmp3 = 4
a = tmp3;
int b = tmp1 + tmp2 + tmp3;
```

に変換され、答えは`2 + 3 + 4 = 9`になります。これが、冒頭のコードの実行結果が、clangでは9になる理由です。

## GCCの気持ち

次に、GCCの気持ちを探ってみましょう。こんなコードを書きます。

```c
int func(int a){
  return ++a + ++a;
}
```

gccに`-fdump-tree-all`オプションをつけてコンパイルすると、コンパイルがこのコードをどのように解釈したかがわかります。

```sh
gcc- c -fdump-tree-all test.c
```

ファイルがごちゃごちゃできますが、見るのは`test.c.005t.gimple`です。

```c
func (int a)
{
  int D.1914;

  a = a + 1;
  a = a + 1;
  D.1914 = a * 2;
  return D.1914;
}
```

わかりやすく書き直すとこうでしょうか。

```c
int func(int a){
  a = a + 1;
  a = a + 1;
  int tmp = a + a;
  return tmp;
}
```

つまり、GCCは、`+`の両側に現れたインクリメント演算子をまず処理していまい、その後に加算を実行していることがわかります。これにより、

```c
int a = 1;
int b = ++a + ++a;
```

は、

```c
int a = 1;
a = a + 1;
a = a + 1;
tmp = a + a
int b = tmp;
```

と書き直されるため、`b=6`になります。

では、三段ではどうでしょうか。こんなコードを書きましょう。

```c
int func(int a){
  return ++a + ++a + ++a;
}
```

これを`-fdump-tree-all`をつけてコンパイルします。

```sh
gcc -c -fdump-tree-all test.c
```

またたくさんファイルができますが、まずは`test.c.004t.original`を見てみましょう。

```c
{
  return ( ++a +  ++a) +  ++a;
}
```

先に左側の`+`を処理することにしたようです。次に`test.c.005t.gimple`を見てみましょう。

```c
func (int a)
{
  int D.1914;

  a = a + 1;
  a = a + 1;
  _1 = a * 2;
  a = a + 1;
  D.1914 = a + _1;
  return D.1914;
}
```

少し整理するとこうなります。

```c
int func(int a){
  a = a + 1;
  a = a + 1;
  int tmp1 = a + a;
  a = a + 1;
  int tmp2 = tmp1 + a;
  return tmp2;
}
```

どうやってこうなったか、気持ちを推し量ってみましょう。オリジナルのコードはこうです。

```c
int func(int a){
  return ++a + ++a + ++a;
}
```

まず、コンパイラは先に左側の加算を実行することにしました。

```c
int func(int a){
  return (++a + ++a) + ++a;
}
```

左側を一時変数`tmp1`に受けます。

```c
int func(int a){
  int tmp1 = ++a + ++a;
  return tmp1 + ++a;
}
```

`++a + ++a`は、両方のインクリメント演算子を加算の前に解決してしまいます。

```c
int func(int a){
  a = a + 1;
  a = a + 1;
  int tmp1 = a + a;
  return tmp1 + ++a;
}
```

次に、`tmp1 + ++a`ですが、まず一時変数`tmp2`にうけましょう。

```c
int func(int a){
  a = a + 1;
  a = a + 1;
  int tmp1 = a + a;
  int tmp2 = tmp1 + ++a;
  return tmp2;
}
```

`tmp1 + ++a`のインクリメント演算子を解決します。

```c
int func(int a){
  a = a + 1;
  a = a + 1;
  int tmp1 = a + a;
  a = a + 1;
  int tmp2 = tmp1 + a;
  return tmp2;
}
```

以上から、GCCは

```c
int a = 1;
int b = ++a + ++a + ++a;
```

を

```c
int a = 1;
a = a + 1;
a = a + 1;          // a = 3
int tmp = a + a;    // tmp = 3 + 3
a = a + 1;          // a = 4
int tmp2 = tmp + a; // 3 + 3 + 4
int b = tmp2;
```

と解釈し、`b = 3 + 3 + 4 = 10`となります。これが、冒頭のコードの実行結果がgccでは10になる理由です。

## まとめ

前置インクリメント演算子が加算の両側に現れたとき、その結果(というか解釈)が処理系に依存すること、さらにgccとclangがそれぞれどのように解釈したか、その気持ちを推し量ってみました。

他にインクリメント演算子のある言語において`a=1`のときに`++a + ++a + ++a`の値がどうなるか調べたところ、clang派が多いようですが、PerlはGCCと同じ10を返しました。

* clang派(結果が9)
    * [PHP](https://wandbox.org/permlink/c6OsSNXGlrHlFC5I)
    * [D言語](https://wandbox.org/permlink/KMzM8e8wLBcvbvlO)
    * [JavaScript](https://wandbox.org/permlink/cqrziGOj8U3rP99k)
* GCC派(結果が10)
    * [Perl](https://wandbox.org/permlink/H7nkIyfX8k1LK2wl)

インクリメント演算子はトラブルのもとだからか、採用しないことにした言語も結構あります(RubyやPythonなど)。

また、Goのように前置インクリメントはなく、後置インクリメントだけにして、さらに「文」として値を返さないことにした言語もあります。これにより、

```go
a++
```

はできますが、

```go
b = a++
```

といった代入はできません。また、インクリメント演算子は関数の引数に入れた場合も問題を起こします。例えばこんなコードを考えましょう。

```c
#include <stdio.h>

void func(int a, int b, int c){
  printf("%d %d %d\n",a ,b ,c);
}

int main(){
  int i = 1;
  func(i++, i++, i++);
}
```

これは、gccでコンパイルしても、x86では「3 2 1」に、ARMでは「1 2 3」になります。

Goのように、「文」にしてしまうと、関数の引数に突っ込むこともできないため、この問題は発生しません。

というわけで、インクリメント演算子はいろいろ面倒なので注意しましょう。個人的には「採用はするけど文にする」というGoの方針が一番しっくりくるかな、という気がしました。


---
title: "関数の定義位置により結果が変わるコード"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["C","GCC"]
published: false
---

## はじめに

少し前、こんなポストをしました。

@[tweet](https://twitter.com/kaityo256/status/1729865255495581824)

これは、C言語において、関数の宣言よりも前に関数呼び出しがあり、かつ引数の型が異なる場合、結果が想定の逆になってしまう、というものです。

この現象の本質は、暗黙のプロトタイプ宣言とABIにあり、以下の記事で説明は尽きています。

[Cの可変長引数とABIの奇妙な関係](https://qiita.com/qnighy/items/be04cfe57f8874121e76)

ですが、先のポストへの反応を見ていると、いまいち何が起きているかが伝わっていないようだったので、簡単に説明しようと思います。

## 現象

まず、この現象は`printf`関数が本質ではありません。それを見るため、以下のようなコードを書いてみましょう。

```c:test1.c
int func(int a, double b){
    return a;
}

int main(){
    return func(1.0,2);
}
```

実行して、終了ステータスを見てみます。

```sh
$ gcc test1.c; ./a.out; echo $?
1
```

`func`からは1が返ってきます。

では、コードはそのままで、`main`と`func`の順序を入れ替えてみましょう。

```c:test2.c
int main(){
    return func(1.0,2);
}

int func(int a, double b){
    return a;
}
```

先程と同様に実行し、終了ステータスを見てみます。

```sh
$ gcc test2.c; ./a.out; echo $?
2
```

2になりましたね。`printf`とか関係なく、単にファイルの中の関数の順序を入れ替えるだけで結果が変わります。これがなぜかを理解するには、ABIと暗黙の関数のプロトタイプ宣言について知る必要があります。

## 関数の引数について

まず、以下の2つの関数を考えます。

```c
void func1(int a, double b);
void func2(double b, int a);
```

引数の順序が違いますが、どちらも`int a`はレジスタ`rdi`に、`double b`は`xmm0`に入ってきます。見てみましょう。こんなコードを書きます。

```c:func.c
void func1(int a, double b){}

void func2(double b, int a){}

int main(){
    func1(1, 2.3);
    func2(2.3, 1);
}
```

コンパイルしてgdbで`func1`、`func2`に入ったところで止め、`rdi`と`xmm0`の値を確認します。

```sh
$ gcc -g func.c; gdb -q ./a.out
Reading symbols from ./a.out...
(gdb) b func1
Breakpoint 1 at 0x1129: file func.c, line 1.
(gdb) b func2
Breakpoint 2 at 0x113c: file func.c, line 3.
(gdb) r
Starting program: ./a.out

Breakpoint 1, func1 (a=21845, b=0) at func.c:1
1       void func1(int a, double b){}
```

いま、`func1`のところで止まったところです。`rdi`と`xmm0`の値を見てみます。

```sh
(gdb) p/d $rdi
$1 = 1
(gdb) p/f $xmm0.v2_int64
$2 = {2.2999999999999998, 0}
```

`rdi`に1が、`xmm0`に`2.3`が入っていますね。

続けて、`func2`でも同じことをしてみます。

```sh
(gdb) c
Continuing.

Breakpoint 2, func2 (b=2.829327078342936e-314, a=1073899110) at func.c:3
3       void func2(double b, int a){}
(gdb) p/d $rdi
$3 = 1
(gdb) p/f $xmm0.v2_int64
$4 = {2.2999999999999998, 0}
```

`func1`と引数の順序が異なるにも関わらず、`rdi`に1が、`xmm0`に`2.3`が入っています。

要するに、x86_64のABIでは、引数の順序に関係なく、最初の整数の引数は`rdi`を、最初の浮動小数の引数は`xmm0`を使う、と決まっています。

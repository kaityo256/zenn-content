---
title: "関数の定義位置により結果が変わるコード"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["C","GCC"]
published: true
---

## はじめに

少し前、こんなポストをしました。

@[tweet](https://twitter.com/kaityo256/status/1729865255495581824)

これは、C言語において、関数の宣言よりも前に関数呼び出しがあり、かつ引数の型が異なる場合、結果が想定の逆になってしまう、というものです。

この現象の本質は、暗黙のプロトタイプ宣言とABIにあり、以下の記事で説明は尽きています。

[Cの可変長引数とABIの奇妙な関係](https://qiita.com/qnighy/items/be04cfe57f8874121e76)

ですが、先のポストへの反応を見ていると、いまいち何が起きているかが伝わっていないようだったので、簡単に説明しようと思います。

以下、使用コンパイラはGCC 9.3.0、環境はWSL上のUbuntu 20.04です。

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

引数の順序が違いますが、どちらも`int a`はレジスタ`edi`に、`double b`は`xmm0`に入ってきます。見てみましょう。こんなコードを書きます。

```c:func.c
void func1(int a, double b){}

void func2(double b, int a){}

int main(){
    func1(1, 2.3);
    func2(2.3, 1);
}
```

コンパイルしてgdbで`func1`、`func2`に入ったところで止め、`edi`と`xmm0`の値を確認します。

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

いま、`func1`のところで止まったところです。`edi`と`xmm0`の値を見てみます。

```sh
(gdb) p/d $edi
$1 = 1
(gdb) p/f $xmm0.v2_int64
$2 = {2.2999999999999998, 0}
```

`edi`に1が、`xmm0`に`2.3`が入っていますね。

続けて、`func2`でも同じことをしてみます。

```sh
(gdb) c
Continuing.

Breakpoint 2, func2 (b=2.829327078342936e-314, a=1073899110) at func.c:3
3       void func2(double b, int a){}
(gdb) p/d $edi
$3 = 1
(gdb) p/f $xmm0.v2_int64
$4 = {2.2999999999999998, 0}
```

`func1`と引数の順序が異なるにも関わらず、`edi`に1が、`xmm0`に`2.3`が入っています。

要するに、x86_64のABIでは、引数の順序に関係なく、最初の整数の引数は`edi`を、最初の浮動小数の引数は`xmm0`を使う、と決まっています。

## 暗黙のプロトタイプ宣言

次に、暗黙の型宣言についてです。C言語では、関数がプロトタイプ宣言無しに呼ばれた場合、返り値はintを返す関数であると仮定し、かつ引数については何も情報がないとします(チェックが行われない)。

すると、プロトタイプ宣言無しで

```c
func1(1, 2.3);
```

と呼ばれた場合、この関数のプロトタイプは

```c
int func1(int a, double b);
```

かもしれませんし

```c
int func1(int a, ...);
```

かもしれませんし、

```c
int func1(...);
```

かもしれません。この全ての可能性に対応するため、決められた個数の引数についてはレジスタを使い、かつ使った浮動小数点レジスタの数を`rax`(の下位8bit)に入れてから関数を呼ぶことになります。見てみましょう。

```c:proto.c
void func2(void){
    func1(1, 2.3)
}
```

アセンブリを見てみましょう。

```sh
$ gcc -S proto.c
```

```as
func2:
.LFB0:
  endbr64
  pushq %rbp
  movq  %rsp, %rbp
  movq  .LC0(%rip), %rax
  movq  %rax, %xmm0
  movl  $1, %edi
  movl  $1, %eax
  call  func1@PLT
  popq  %rbp
  ret
.LC0:
  .long 1717986918
```

不要な情報を一部削除していますが、

* `edi`に1を
* `xmm0`に2.3を
* `eax`に1を

代入しているのがわかると思います。`edi`が整数引数、`xmm0`が浮動小数点です。そして、`eax`に使った浮動小数点の数である1が入っています。

`func1`のプロトタイプ宣言がある場合、可変長引数の可能性が消えるため、`eax`への代入は不要になります。

```c:proto2.c
int func1(int, double);

void func2(void){
    func1(1, 2.3);
}
```

```sh
$ gcc -S proto2.c
```

```asm
func2:
.LFB0:
	endbr64
	pushq	%rbp
	movq	%rsp, %rbp
	movq	.LC0(%rip), %rax
	movq	%rax, %xmm0
	movl	$1, %edi
	call	func1@PLT
	popq	%rbp
	ret
	.cfi_endproc
```

`call`の前の`movl  $1, %eax`が消えたのがわかりますね。どちらにせよ、整数引数は`edi`に、浮動小数点引数は`xmm0`に入れて渡されます。

## 何がおきたか

以上を踏まえて、最初のコードで何が起きたか見てみましょう。

最初に`func2`の情報がないまま呼ばれています。

```c
void func1(){
    func2(1.0, 2);
}
```

仕方ないのでコンパイラは`func2(double, int)`もしくは`func2(...)`のどちらでもいけるように、

* `edi`に2を
* `xmm0`に1.0を
* `eax`に1を

代入して`call func2`するコードを吐きます。

しかし、実際には`func2`は`func2(int, double)`でした。


```c
void func2(int a, double b){
    printf("%d %f\n", a, b);
}
```

`func2`では、`edi`に`a`の値が、`xmm0`に`b`の値が代入されてくると思っています。なので、

```c
func2(1.0, 2);
```

と呼び出したにもかかわらず、

```c
func2(2, 1.0);
```

として呼び出されたとして処理されてしまいます。これが値がひっくり返る理由です。

## まとめ

暗黙のプロトタイプ宣言と、関数の引数に関するABIがからんだ、少し直感に反するC言語の処理について紹介しました。

ここで紹介したようなコードに対しては、最近のコンパイラは警告を出しますし、処理系によってはエラーで落とすこともあるようです。ただ、「警告を無視するな」で終わらせるにはちょっともったいないかな、と思って少し丁寧に説明してみました。

冗談で怖さを煽るようなポストをしてしまいましたが、こういう直感に反するC言語の処理の理解は、ABIなど低レイヤを学ぶ絶好の機会だと思います。

この記事で、少しでもC言語が面白いと思ってもらえたら幸いです。


---
title: "リンカのお仕事"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["C","C++"]
published: true
---

## はじめに

突然ですが、こんなC++プログラムをコンパイルしてみましょう.

```cpp
#include <cstdio>

void func();

int main() {
  func();
}
```

`func`という関数のプロトタイプ宣言があり、それを`main`関数内で呼び出していますが、実体が定義されていません。これをコンパイルしようとすると、例えばこんなエラーがでます。

```sh
$ g++ test.cpp
/usr/bin/ld: /tmp/ccFEAPJn.o: in function `main':
test.cpp:(.text+0x9): undefined reference to `func()'
collect2: error: ld returned 1 exit status
```

エラーメッセージは「`func`なんて知らないよ」というものですが、エラーを出しているのは`/usr/bin/ld`というプログラムです。これは、リンカ(linker)と呼ばれるソフトウェアです。

リンカというと、「分割コンパイルされて作られたオブジェクトファイルをくっつけて実行バイナリを作るもの」というイメージがあるかもしれませんが、他にもいろいろな仕事をしています。それをちょっとだけ見てみましょう。以下、Linux(っていうかELF)の話に限定します。GCCとUbuntuを使います。

## 分割コンパイル

まずは適当に分割コンパイルしてみましょう。まず、`main.cpp`はこんな感じです。

```cpp
#include <cstdio>

int a = 1;
int b = 2;

int add(int, int);

int main() {
  int c = add(a, b);
  printf("%d\n", c);
}
```

`add`という関数を宣言して呼び出しています。その実体を`add.cpp`に書いてやりましょう。

```cpp
int add(int x, int y) {
  return x + y;
}
```

単に二つの引数を足して返すだけの関数ですね。これを分割コンパイルしましょう。`g++`に`-c`オプションをつけると、コンパイルのみおこなって、オブジェクトファイルを作ってくれます。

```sh
$ g++ -c main.cpp
$ g++ -c add.cpp
```

これで`main.o`、`add.o`ができました。これをリンクします。`g++`に`.o`ファイルを食わせるとリンクして、実行バイナリを作ってくれます。

```cpp
$ g++ main.o add.o
$ ./a.out
3
```

実行バイナリができて実行できました。これが分割コンパイルです。

## 関数のアドレス

さて、プログラムを実行する際、コードがメモリ上にロードされています。そして「最初の場所」から順番に実行されていきます。関数とは、メモリ上のラベルであり、どこかのアドレスを指しています。関数呼び出しとは、

* 現在実行中のプログラムのアドレスを記憶して
* 呼びたい関数のアドレスへジャンプして
* その関数の処理が終わったら記憶していたアドレスへ戻ってくる

という一連の処理のことです。

それを見るために、関数のアドレスを表示させてみましょう。さっきの`main.cpp`を以下のように書き換えてみます。

```cpp
#include <cstdio>

int a = 1;
int b = 2;

int add(int, int);

int main() {
  int c = add(a, b);
  printf("%d\n", c);
  printf("add :%p\n", add);
  printf("main:%p\n", main);
}
```

先ほど書いたように、関数とはメモリのどこかのアドレスを指すラベルです。そのラベルがどのアドレスを指しているか表示しています。

コンパイル、実行してみましょう。

```sh
$ g++ -c main.cpp
$ g++ main.o add.o
$ ./a.out
3
add :0x55e63ead21bd
main:0x55e63ead2149
```

関数の実行結果`3`の後に、関数のアドレスが表示されました。Ubuntuではデフォルトで[address space layout randomization, ASLR](https://ja.wikipedia.org/wiki/%E3%82%A2%E3%83%89%E3%83%AC%E3%82%B9%E7%A9%BA%E9%96%93%E9%85%8D%E7%BD%AE%E3%81%AE%E3%83%A9%E3%83%B3%E3%83%80%E3%83%A0%E5%8C%96)というセキュリティが有効になっているため、実行するたびにアドレスが変わりますが、とりあえず下3桁だけ見ておけばよいです。

これを見ると、`add`のアドレスの下3桁が1bdに、`main`のアドレスの下3桁が149になっていますね。この、関数をどのアドレスに配置すべきかは、実行バイナリである`a.out`に書いてあります。`readelf`というコマンドで見てみましょう。

```sh
$ readelf -s ./a.out | grep FUNC | c++filt
     2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@GLIBC_2.2.5 (2)
     3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.2.5 (2)
     6: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@GLIBC_2.2.5 (2)
    29: 0000000000001090     0 FUNC    LOCAL  DEFAULT   16 deregister_tm_clones
    30: 00000000000010c0     0 FUNC    LOCAL  DEFAULT   16 register_tm_clones
    31: 0000000000001100     0 FUNC    LOCAL  DEFAULT   16 __do_global_dtors_aux
    34: 0000000000001140     0 FUNC    LOCAL  DEFAULT   16 frame_dummy
    46: 0000000000001000     0 FUNC    LOCAL  DEFAULT   12 _init
    47: 0000000000001250     5 FUNC    GLOBAL DEFAULT   16 __libc_csu_fini
    50: 00000000000011bd    24 FUNC    GLOBAL DEFAULT   16 add(int, int)
    53: 0000000000001258     0 FUNC    GLOBAL HIDDEN    17 _fini
    54: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@@GLIBC_2.2.5
    55: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@@GLIBC_
    60: 00000000000011e0   101 FUNC    GLOBAL DEFAULT   16 __libc_csu_init
    62: 0000000000001060    47 FUNC    GLOBAL DEFAULT   16 _start
    65: 0000000000001149   116 FUNC    GLOBAL DEFAULT   16 main
    68: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@@GLIBC_2.2
```

なんかごちゃごちゃ出てきましたが、とりあえず`main`の場所は1149に、`add(int, int)`の場所は11bdと指定されており、確かに下3桁がそれぞれ149、1bdになっています。`c++filt`はC++の関数名のデマングリングをするコマンドですが、ここでは詳細には触れません。

アセンブリも見てみましょう。`objdump -S`で逆アセンブルしてみます。

```sh
$ objdump -S ./a.out
(snip)
0000000000001149 <main>:
(snip)
    1165:       e8 53 00 00 00          callq  11bd <add(int, int)>
(snip)
    11bc:       c3                      retq
(snip)
00000000000011bd <add(int, int)>:
(snip)
```

`main`と`add`のアドレスがそれぞれ`1149`、`11bd`であること、また、`main`関数から`add`を呼び出す時、`callq  11bd`と、`add`の指すアドレスが指定されていることがわかります。これを見ると、関数とはメモリ上のアドレスを指すラベルであり、関数呼び出しとはラベルの指すアドレスへのジャンプであることが実感できるかと思います。

## シンボルの解決

さて、先ほどは`main.o`、`add.o`の順番でリンクしました。順番を逆にしてみましょう。

```sh
$ g++ add.o main.o
$ ./a.out
add :0x560fd7d1c149
main:0x560fd7d1c161
```

`add`と`main`のメモリの位置が入れ替わり、`add`の方が先になりました。`readelf`で見てみましょう。

```sh
$ readelf -s ./a.out | grep FUNC | c++filt
(snip)
    50: 0000000000001149    24 FUNC    GLOBAL DEFAULT   16 add(int, int)
(snip)
    65: 0000000000001161   116 FUNC    GLOBAL DEFAULT   16 main
(snip)
```

`add`のアドレスが1149に、`main`のアドレスが1161になっています。つまり、関数のアドレスはリンクする順番に依存します。したがって、関数のアドレスはリンク時に決まることがわかります。

逆に言えば、リンクするまでは関数のアドレスは決まっていません。`readelf`でオブジェクトファイルを見てみましょうか。

```sh
$ readelf -s main.o  | c++filt
(snip)
    12: 0000000000000000   116 FUNC    GLOBAL DEFAULT    1 main
(snip)
    14: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND add(int, int)
    15: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND printf
```

`main`は関数(FUNC)であることが書いてありますが、アドレスは決まっておらず、さらに`add`や`printf`はUND、つまり未定義(undefined)となっています。`add.o`も見てみましょう。

```sh
$ readelf -s add.o  | c++filt
(snip)
     9: 0000000000000000    24 FUNC    GLOBAL DEFAULT    1 add(int, int)
(snip)
```

`add`は関数(FUNC)であることが書いてありますが、やはりアドレスはまだ決まっていません。この状態で`main.o`のアセンブリを見てみましょう。

```sh
$ objdump -S main.o | c++filt
0000000000000000 <main>:
(snip)
  1c:   e8 00 00 00 00          callq  21 <main+0x21>
  21:   89 45 fc                mov    %eax,-0x4(%rbp)
```

`add`を呼び出しているところには、仮のアドレス(callqの次の命令のアドレス)が入っています。

関数や変数はメモリ上のアドレスのどこかを指すラベルですが、こういうラベルを「シンボル」と言います。リンカは、プログラムのサイズを計算して、シンボルと実際のアドレスを紐づけます。この、ラベルへの参照を解決するのがリンカの仕事です。

## スタートアップルーチン

`readelf`で`a.out`にある関数のシンボルをもう一度見てみましょう。

```sh
$ readelf -s a.out  | grep FUNC |c++filt
     2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@GLIBC_2.2.5 (2)
     3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.2.5 (2)
     6: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@GLIBC_2.2.5 (2)
    29: 0000000000001090     0 FUNC    LOCAL  DEFAULT   16 deregister_tm_clones
    30: 00000000000010c0     0 FUNC    LOCAL  DEFAULT   16 register_tm_clones
    31: 0000000000001100     0 FUNC    LOCAL  DEFAULT   16 __do_global_dtors_aux
    34: 0000000000001140     0 FUNC    LOCAL  DEFAULT   16 frame_dummy
    46: 0000000000001000     0 FUNC    LOCAL  DEFAULT   12 _init
    47: 0000000000001250     5 FUNC    GLOBAL DEFAULT   16 __libc_csu_fini
    50: 0000000000001149    24 FUNC    GLOBAL DEFAULT   16 add(int, int)
    53: 0000000000001258     0 FUNC    GLOBAL HIDDEN    17 _fini
    54: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@@GLIBC_2.2.5
    55: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@@GLIBC_
    60: 00000000000011e0   101 FUNC    GLOBAL DEFAULT   16 __libc_csu_init
    62: 0000000000001060    47 FUNC    GLOBAL DEFAULT   16 _start
    65: 0000000000001161   116 FUNC    GLOBAL DEFAULT   16 main
    68: 0000000000000000     0 FUNC    WEAK   DEFAULT  UND __cxa_finalize@@GLIBC_2.2
```

もともとのプログラムには`main`と`add`しか定義がなく、それ以外の関数呼び出しは`printf`だけだったのに、他にもいろいろ増えていることがわかりますね。こいつらをリンクするのもリンカの仕事です。このうち、`_start`だけ見てみましょう。

`_start`とは、スタートアップルーチンと呼ばれるもので、`main`関数を呼び出すのが主な仕事です。gdbで見てみましょう。

```sh
$ gdb ./a.out
```

まずは`_start`にブレークポイントを置きます。

```sh
(gdb) b _start
Breakpoint 1 at 0x1060
```

`0x1060`にブレークポイントが置かれました。さっき`readelf`で見た`_start`のアドレスと同じですね。

```txt
    62: 0000000000001060    47 FUNC    GLOBAL DEFAULT   16 _start
```

実行すると、`_start`のところで止まります。

```sh
(gdb) r
Breakpoint 1, 0x0000555555555060 in _start ()
```

アセンブリを見てみましょう。

```sh
(gdb) disas
Dump of assembler code for function _start:
=> 0x0000555555555060 <+0>:     endbr64
   0x0000555555555064 <+4>:     xor    %ebp,%ebp
   0x0000555555555066 <+6>:     mov    %rdx,%r9
   0x0000555555555069 <+9>:     pop    %rsi
   0x000055555555506a <+10>:    mov    %rsp,%rdx
   0x000055555555506d <+13>:    and    $0xfffffffffffffff0,%rsp
   0x0000555555555071 <+17>:    push   %rax
   0x0000555555555072 <+18>:    push   %rsp
   0x0000555555555073 <+19>:    lea    0x1d6(%rip),%r8        # 0x555555555250 <__libc_csu_fini>
   0x000055555555507a <+26>:    lea    0x15f(%rip),%rcx        # 0x5555555551e0 <__libc_csu_init>
   0x0000555555555081 <+33>:    lea    0xd9(%rip),%rdi        # 0x555555555161 <main>
   0x0000555555555088 <+40>:    callq  *0x2f52(%rip)        # 0x555555557fe0
   0x000055555555508e <+46>:    hlt
End of assembler dump.
```

`main`関数が呼ばれて**いない**ことがわかります。実は、スタートアップルーチンは`__libc_start_main`を呼んでおり、`main`関数はその関数から呼ばれます。そのためにスタートアップルーチンに`main`関数場所を教えているのがここです。

```sh
   0x0000555555555081 <+33>:    lea    0xd9(%rip),%rdi        # 0x555555555161 <main>
```

プログラムを実行する際、この`_start`が最初に実行されます。したがって、こいつがリンクされていないと実行バイナリが作れません。オブジェクトファイルを`g++`ではなく、`ld`でリンクしてみましょう。

```txt
$ ld main.o add.o
ld: warning: cannot find entry symbol _start; defaulting to 0000000000401000
ld: main.o: in function `main':
main.cpp:(.text+0x36): undefined reference to `printf'
ld: main.cpp:(.text+0x51): undefined reference to `printf'
ld: main.cpp:(.text+0x69): undefined reference to `printf'
```

最初に実行される場所(entry symbol)であるところの`_start`が無いよと言われたり、`printf`が見つからないよと言われたりしています。実はこいつらの場所をリンカに教えているのが`g++`です。`g++`はコンパイラではなくコンパイラドライバと呼ばれるもので、裏でプリプロセッサを呼んだり、コンパイラを呼んだり、リンカを呼んだりいろいろやってくれるものです。`glibc`の場所などを`ld`ちゃんと教えることで、正しくリンクされ、実行バイナリができます。

## まとめ

リンカのお仕事を見てみました。リンカは分割コンパイルされたオブジェクトファイルをくっつけるのも仕事ですが、その際にシンボル名を解決し、実際のアドレスと紐づけています。また、スタートアップルーチンや`printf`といった関数を含むライブラリをくっつけたりするのもリンカの仕事ですが、それらのライブラリの場所をリンカに教えるのはコンパイルドライバである`g++`です。

リンカはいろいろ奥が深いですが、その詳細を説明するのは私の能力を超えます。気になる人は参考文献を参照してください。

## 参考文献

* [実践的低レイヤプログラミング](https://tanakamura.github.io/pllp/docs/)の[リンカの章](https://tanakamura.github.io/pllp/docs/linker.html) リンカが何をしているか詳しく書いてあるのでざっと読んでおくと「へぇ」と思うことがいっぱいある
* [github.com/rui314/mold](https://github.com/rui314/mold) Rui Ueyamaさんによるリンカの実装。高速な動作をするためにいろいろ工夫されており、ソースを読んでも理解は難しいが、とりあえず「リンカの中身」を見てみるのに良いかもしれない。
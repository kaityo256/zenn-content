---
title: "GCCに27957段ネストした関数を食わせると死ぬ"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["C++","GCC","C"]
published: false
---

## TL;DR

`f(f(f(f(1))))`のように関数をネストして呼び出す時、27957段以上ネストするとGCCが死ぬので気を付けましょう。

## はじめに

最近のコンパイラは、関数のインライン展開をやってくれます。例えば

```cpp
int f(int i) {
  return i;
}
```

という、単に引数をそのまま返す関数がある時、これを何度も呼び出す

```cpp
int hoge(){
  return f(f(f(1)));
}
```

のような関数があると、中身をなるべく展開してくれます。コンパイルすると`hoge`はこうなります。

```txt
hoge:
.LFB1:
  .cfi_startproc
  endbr64
  movl  $1, %eax
  ret
  .cfi_endproc
```

問答無用で1を返す関数に最適化してしまっていますね。

これを見ると、多分10人中10人が「ネストを何段まで展開できるんだろう？」と思うと思います。なので調べてみましょう。こんなスクリプトを書きます。

```rb
def make_src(n)
  str = <<"EOS"
int f(int i) { return i; }
int hoge() { return #{'f('*n}f(1)#{')'*n}; }
EOS
  File.open("test.c","w") do |f|
  f.puts(str)
  end
end

make_src(ARGV[0].to_i)
```

これで、例えば

```sh
ruby test.rb 10
```

とかすると、

```cpp
int f(int i) { return i; }
int hoge() { return f(f(f(f(f(f(f(f(f(f(f(1))))))))))); }
```

という`test.c`が出てきます。コンパイルしてみましょう。

```sh
gcc -O3 -S test.c
```

```txt
hoge:
.LFB1:
  .cfi_startproc
  endbr64
  movl  $1, %eax
  ret
  .cfi_endproc
```

まだ楽勝ですね。では10万では？

```sh
$ ruby test.rb 100000;gcc -O3 -S test.c
gcc: internal compiler error: Segmentation fault signal terminated program cc1
Please submit a full bug report,
with preprocessed source if appropriate.
See <file:///usr/share/doc/gcc-9/README.Bugs> for instructions.
```

**GCCが internal compiler errorで死にました**。

関数のネストを10段展開しても死なず、100000段展開すると、死ぬ、ということはそのどこかに死ぬ境目があることになりますね。

## GCCにXX段ネストした関数を食わせると死ぬ

「GCCは何段まで関数のネストを展開できるんでしょうか？これってトリビアになりませんか？」

このトリビアの種、つまりこういうことになります。

「GCCが死ぬのは関数をXX段ネストした時」

実際に、調べてみた。

環境はWSL2上のUbuntu 20.04、GCCのバージョンは

```sh
$ gcc --version
gcc (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0
Copyright (C) 2019 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

手抜き二分探索コードを書いてみましょう。

```rb
def make_src(n)
  str = <<"EOS"
  int f(int i) { return i; }
  int hoge() { return #{'f('*n}f(1)#{')'*n}; }
EOS
    File.open("test.c","w") do |f|
    f.puts(str)
    end
end

def check(n)
  make_src(n)
  return !system("gcc -O3 -S test.c 2> /dev/null")
end

n = (10..100000).bsearch {|n| check(n)}
puts "GCC dies by #{n} times nested functions."
```

実行してみます。

```sh
$ ruby binsearch.rb
GCC dies by 27957 times nested functions.
```

27957段で死ぬようです。試してみましょう。

```sh
$ ruby test.rb 27956;gcc -O3 -S test.c;echo $?
0

$ ruby test.rb 27957;gcc -O3 -S test.c;echo $?
gcc: internal compiler error: Segmentation fault signal terminated program cc1
Please submit a full bug report,
with preprocessed source if appropriate.
See <file:///usr/share/doc/gcc-9/README.Bugs> for instructions.
4
```

確かに27956段までは大丈夫(たまに死にますが)で、27967段では確実に死にますね。

## まとめ

こうしてこの世界にまた一つ

新たなトリビアが生まれた。

「GCCに27957段ネストした関数を食わせると死ぬ」

というわけで、皆さんも関数を多段ネストしたくなった時は27000段くらいで止めておくのが良いと思います。

## これまでのコンパイラいじめの記録

* [printfに4285個アスタリスクをつけるとclang++が死ぬ](https://qiita.com/kaityo256/items/84d8ba352009e3a0fe42)
* [定数配列がからんだ定数畳み込み最適化](https://qiita.com/kaityo256/items/bf9712559c9cd2ce4e2c)
* [C++でアスタリスクをつけすぎると端末が落ちる](https://qiita.com/kaityo256/items/d54439246edc1cc58121)
* [整数を419378回インクリメントするとMacのg++が死ぬ](https://qiita.com/kaityo256/items/6b5715b213e955d44f55)
* [コンパイラは関数のインライン展開を☓☓段で力尽きる](https://qiita.com/kaityo256/items/b4dc66c92338c0b92552)
* [関数ポインタと関数オブジェクトのインライン展開](https://qiita.com/kaityo256/items/5911d50c274465e19cf6)
* [インテルコンパイラのアセンブル時最適化](https://qiita.com/kaityo256/items/e7b05eb9c2bfbbd434a7)
* [GCCの最適化がインテルコンパイラより賢くて驚いた話](https://qiita.com/kaityo256/items/72c1bf93a210e450308c)
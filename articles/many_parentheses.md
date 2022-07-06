---
title: "括弧で34087重に囲んだ関数を食わせるとg++が死ぬ"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp","gcc","llvm",`intel`]
published: false
---

## TL;DR

`((((printf("Hello World\n")))))`みたいに関数をたくさんの括弧で囲むとコンパイラが死ぬので気をつけましょう。

## はじめに

以前、[printfに4285個アスタリスクをつけるとclang++が死ぬ](https://qiita.com/kaityo256/items/84d8ba352009e3a0fe42)という記事や、[GCCに27958段ネストした関数を食わせると死ぬ](https://zenn.dev/kaityo256/articles/nesting_functions)という記事を書きました。

特に、`printf`にアスタリスクをたくさんつける記事では、`clang++`がわりとすぐ死んだのに対して、`g++`は5万個とかつけても大丈夫でした。一般に、コンパイラが死ぬ系のコンパイラいじめは、再帰でスタックを使い切るタイプのものが多く、LLVMよりもGCCの方が頑健という印象です。

さて、C++では、括弧を無駄につけることができます。例えば、

```cpp
printf("Hello World\n");
```

と書いても、

```cpp
(((printf("Hello World\n"))));
```

と書いても同じ結果になります。これ、いくつまで囲めるか、気になりますね。スクリプトを書いてみましょう(`test.rb`)。

```rb
def check(n)
  s1 = "("*n
  s2 = ")"*n
  open("test.cpp","w") do |f|
  f.puts <<EOS
#include <cstdio>
int main(){
(#{s1}printf)("Hello World\\n")#{s2};
}
EOS
  end
  return system("g++ test.cpp")
end

check(ARGV[0].to_i)
```

例えば、

```sh
ruby test.rb 10
```

とすると、こんなコードが出力され、`g++`に渡されます。

```cpp
#include <cstdio>
int main(){
(((((((((((printf)("Hello World\n")))))))))));
}
```

とりあえず1000くらいから行ってみましょうか。

```sh
ruby test.rb 1000
```

まだ余裕そうです。10000は？

```sh
ruby test.rb 10000
```

問題ありません。50000ではどうでしょうか？

```sh
$ ruby test.rb 50000
g++: internal compiler error: Segmentation fault signal terminated program cc1plus
Please submit a full bug report,
with preprocessed source if appropriate.
See <http://bugzilla.redhat.com/bugzilla> for instructions.
```

**`g++`がICE(internal compiler error)で死にましたね**。

関数を10000重に囲んでも大丈夫ですが、50000重に囲むと死ぬ、ということはそのどこかに死ぬ境目があることになりますね。

## 括弧でXX重に囲んだ関数を食わせるとg++が死ぬ

「g++は何重まで関数を括弧で囲めるんでしょうか？これってトリビアになりませんか？」

このトリビアの種、つまりこういうことになります。

「g++が死ぬのは関数を括弧でXX重に囲んだ時」

実際に、調べてみた。

環境やコンパイラのバージョンは以下の通り。

* OS: Red Hat Enterprise Linux release 8.2
* g++ 8.5.0
* clang++: 12.0.0
* icpc (ICC) 19.1.3.304 20200925

## g++の場合

こんなコードを書いてみましょう(`search.rb`)。

```rb
def check(n)
  s1 = "("*n
  s2 = ")"*n
  open("test.cpp","w") do |f|
  f.puts <<EOS
#include <cstdio>
int main(){
#{s1}printf("Hello World\\n")#{s2};
}
EOS
  end
  if system("g++ test.cpp 2> /dev/null")
    puts "#{n} OK"
    false
  else
    puts "#{n} NG"
    true
  end
end

(10000..50000).bsearch do |n|
  check(n)
end
```

実行してみます。

```sh
$ ruby check.rb
30000 OK
40000 NG
35000 NG
32500 OK
33750 OK
34375 NG
34063 OK
34219 NG
34141 NG
34102 NG
34083 OK
34093 NG
34088 NG
34086 OK
34087 NG
```

34086重は大丈夫ですが、34087重はダメですね。

## 括弧でXX重に囲んだ関数を食わせるとclang++が死ぬ

clang++でも試してみましょう。先程の`test.rb`の`g++`を`clang++`にするだけです。まずは1000あたりから行きましょうか。

```sh
$ ruby test.rb 1000
test.cpp:3:257: fatal error: bracket nesting level exceeded maximum of 256
(snip)
test.cpp:3:257: note: use -fbracket-depth=N to increase maximum nesting level
1 error generated.
```

括弧の深さはデフォルトで256までであり、それ以上に増やしたければ`-fbracket-depth=N`で指定しろ、とありますね。とりあえず10000に増やしてもう一度やってみましょう。

```sh
$ ruby test.rb 1000
test.cpp:3:1002: warning: stack nearly exhausted; compilation time may suffer, and crashes due to stack overflow are likely [-Wstack-exhausted]
(snip)
1 warning generated.
```

**スタックを使い切りそうだという警告** が出ました。こんなの前からあったっけ？では10000では？

```sh
$ ruby test.rb 10000
PLEASE submit a bug report to https://bugs.llvm.org/ and include the crash backtrace, preprocessed source, and associated run script.
(snip)
clang-12: error: unable to execute command: Segmentation fault (core dumped)
clang-12: error: clang frontend command failed due to signal (use -v to see invocation)
(snip)
```

**無事に死にました。**

また二分探索してみましょうか。

```sh
$ ruby check.rb
5500 NG
3250 NG
2125 NG
1562 NG
1281 NG
1140 NG
1070 NG
1035 NG
1017 NG
1008 OK
1013 OK
1015 NG
1014 OK
```

1014重は大丈夫でしたが、1015重はダメでした。1000でギリギリだったようですね。

## 括弧でXX重に囲んだ関数を食わせるとicpcが死ぬ

せっかくなのでIntel Compilerも殺してみましょうか。

```sh
$ ruby test.rb 1000
$ ruby test.rb 10000
test.cpp(3): internal error: bad pointer
(snip)
compilation aborted for test.cpp (code 4)
```

1000はOK、10000は死ぬので、ギリギリはその間ですね。

```sh
$ ruby check.rb
5500 NG
3250 NG
2125 OK
2688 NG
2407 NG
2266 NG
2196 NG
2161 NG
2143 NG
2134 NG
2130 OK
2132 NG
2131 OK
```

2131重は大丈夫ですが、2132重はダメでした。

## まとめ

こうしてこの世界にまた一つ

新たなトリビアが生まれた。

* 括弧で34087重に囲んだ関数を食わせると`g++`が死ぬ
* 括弧で1015重に囲んだ関数を食わせると`clang++`が死ぬ
* 括弧で2132重に囲んだ関数を食わせると`icpc`が死ぬ

というわけで、不意に「あー、関数を括弧で死ぬほど囲みたい。最低でも1万くらいは囲みたい」とおもったら、`g++`を使うと良いと思います。

## 補足のトリビア

* たくさん括弧で囲むと`g++`も`clang++`もコンパイルにすごく時間がかかるが、`icpc`はあっという間に死んでくれるので検証が楽。
* [アスタリスクをたくさん付けた場合](https://qiita.com/kaityo256/items/84d8ba352009e3a0fe42)、`clang++`は`Parser::ParseCastExpression`という関数の再帰呼び出しのし過ぎでスタック枯渇で死んでいたが、括弧で囲みすぎた場合は`Parser::ParseParenExpression`という関数の再帰のし過ぎで死ぬ。
* 死ぬ括弧の深さはメモリに依存する(スタック枯渇だから)ので、環境によって異なる。

## これまでのコンパイラいじめの記録

* [GCCに27958段ネストした関数を食わせると死ぬ](https://zenn.dev/kaityo256/articles/nesting_functions)
* [printfに4285個アスタリスクをつけるとclang++が死ぬ](https://qiita.com/kaityo256/items/84d8ba352009e3a0fe42)
* [定数配列がからんだ定数畳み込み最適化](https://qiita.com/kaityo256/items/bf9712559c9cd2ce4e2c)
* [C++でアスタリスクをつけすぎると端末が落ちる](https://qiita.com/kaityo256/items/d54439246edc1cc58121)
* [整数を419378回インクリメントするとMacのg++が死ぬ](https://qiita.com/kaityo256/items/6b5715b213e955d44f55)
* [コンパイラは関数のインライン展開を☓☓段で力尽きる](https://qiita.com/kaityo256/items/b4dc66c92338c0b92552)
* [関数ポインタと関数オブジェクトのインライン展開](https://qiita.com/kaityo256/items/5911d50c274465e19cf6)
* [インテルコンパイラのアセンブル時最適化](https://qiita.com/kaityo256/items/e7b05eb9c2bfbbd434a7)
* [GCCの最適化がインテルコンパイラより賢くて驚いた話](https://qiita.com/kaityo256/items/72c1bf93a210e450308c)

動画もあります。

* [コンパイラのいじめ方(YouTube)](https://www.youtube.com/watch?v=rC-YSvtRrHw) CPP MIXで話したもの

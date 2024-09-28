---
title: "clang++に30740次元の配列を食わせると死ぬ"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp","clang","gcc"]
published: false
---

## はじめに

以前、[C/C++の配列と糖衣構文](https://zenn.dev/kaityo256/articles/syntax_sugar_of_array)という記事を書きました。C/C++では、多次元配列は、その次元やサイズに応じた型が作られます。

例えば

```cpp
#include <cstdio>
#include <typeinfo>

int main() {
  int a[2][3];
  printf("%s\n", typeid(a).name());
}
```

を実行すると、

```txt
A2_A3_i
```

という結果になります。`a`は`int`型の2次元配列であり、サイズは2 x 3である、という意味です。

```cpp
  int a[2][3][4];
```

こんな配列だと、

```txt
A2_A3_A4_i
```

こんな感じになります。

さて、これ、いくらでも次元を増やせそうですね。100次元とかどうでしょう？

```cpp
#include <cstdio>
#include <typeinfo>

int a[1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1][1];

int main() {
  printf("%s\n", typeid(a).name());
}
```

実行するとこんな感じです。

```txt
A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_i
```

全く問題ないですね。それじゃ1万次元とかではどうでしょう？任意の次元の配列を作るコードを吐くRubyスクリプトを作って実行してみましょう。

```rb: check.rb
# frozen_string_literal: true

def check(cpp, n_dim)
  astr = '[1]' * n_dim
  s = <<"CPPSRC"
  #include <cstdio>
  #include <typeinfo>
  int a#{astr};
  int main(){
    printf("%s\\n",typeid(a).name());
  }
CPPSRC
  File.open('test.cc', 'w') do |f|
    f.puts s
  end
  system("#{cpp} test.cc")
end

check('clang++', 10000)
```

```sh
$ ruby check.rb
$ ./a.out
A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1
(snip)
A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_A1_i
```

大丈夫そうです。では5万次元では？

```sh
$ ruby check.rb
PLEASE submit a bug report to https://github.com/llvm/llvm-project/issues/ and include the crash backtrace, preprocessed source, and associated run script.
Stack dump:
0.      Program arguments: /usr/local/bin/clang-16 -cc1 -triple x86_64-unknown-linux-gnu -emit-obj -mrelax-all --mrelax-relocations -disable-free -clear-ast-before-backend -disable-llvm-verifier -discard-value-names -main-file-name test.cc -mrelocation-model pic -pic-level 2 -pic-is-pie -mframe-pointer=all -fmath-errno -ffp-contract=on -fno-rounding-math -mconstructor-aliases -funwind-tables=2 -target-cpu x86-64 -tune-cpu generic -mllvm -treat-scalable-fixed-error-as-warning -debugger-tuning=gdb -fcoverage-compilation-dir=/home/watanabe/temp -resource-dir /usr/local/lib/clang/16 -I/opt/intel/compilers_and_libraries_2020.0.166/linux/mkl/include -internal-isystem /opt/rh/devtoolset-8/root/usr/lib/gcc/x86_64-redhat-linux/8/../../../../include/c++/8 -internal-isystem /opt/rh/devtoolset-8/root/usr/lib/gcc/x86_64-redhat-linux/8/../../../../include/c++/8/x86_64-redhat-linux -internal-isystem /opt/rh/devtoolset-8/root/usr/lib/gcc/x86_64-redhat-linux/8/../../../../include/c++/8/backward -internal-isystem /usr/local/lib/clang/16/include -internal-isystem /usr/local/include -internal-isystem /opt/rh/devtoolset-8/root/usr/lib/gcc/x86_64-redhat-linux/8/../../../../x86_64-redhat-linux/include -internal-externc-isystem /include -internal-externc-isystem /usr/include -fdeprecated-macro -fdebug-compilation-dir=/home/watanabe/temp -ferror-limit 19 -fgnuc-version=4.2.1 -fcxx-exceptions -fexceptions -fcolor-diagnostics -faddrsig -D__GCC_HAVE_DWARF2_CFI_ASM=1 -o /tmp/test-18592a.o -x c++ test.cc
1.      test.cc:4:3: current parser token 'int'
2.      test.cc:3:7: LLVM IR generation of declaration 'a'
3.      test.cc:3:7: Generating code for declaration 'a'
  #0 0x0000000002fc6907 llvm::sys::PrintStackTrace(llvm::raw_ostream&, int) (/usr/local/bin/clang-16+0x2fc6907)
  #1 0x0000000002fc46bc SignalHandler(int) Signals.cpp:0:0
  #2 0x00007fe75ab61630 __restore_rt sigaction.c:0:0
  #3 0x0000000003482b22 clang::CodeGen::CodeGenTypes::ConvertTypeForMem(clang::QualType, bool) (/usr/local/bin/clang-16+0x3482b22)
  #4 0x0000000003481852 clang::CodeGen::CodeGenTypes::ConvertType(clang::QualType) (/usr/local/bin/clang-16+0x3481852)
(snip)
#254 0x0000000003481852 clang::CodeGen::CodeGenTypes::ConvertType(clang::QualType) (/usr/local/bin/clang-16+0x3481852)
#255 0x0000000003482b54 clang::CodeGen::CodeGenTypes::ConvertTypeForMem(clang::QualType, bool) (/usr/local/bin/clang-16+0x3482b54)
clang-16: error: unable to execute command: Segmentation fault (core dumped)
clang-16: error: clang frontend command failed due to signal (use -v to see invocation)
clang version 16.0.0 (https://github.com/llvm/llvm-project.git ba5edfd386fcbb6bd06fe7fe499ca4d5949f1d6b)
Target: x86_64-unknown-linux-gnu
Thread model: posix
InstalledDir: /usr/local/bin
clang-16: note: diagnostic msg:
********************

PLEASE ATTACH THE FOLLOWING FILES TO THE BUG REPORT:
Preprocessed source(s) and associated run script(s) are located at:
clang-16: note: diagnostic msg: /tmp/test-92c55e.cpp
clang-16: note: diagnostic msg: /tmp/test-92c55e.sh
clang-16: note: diagnostic msg:

********************
```

**clang++が死にましたね**。 なんか、「PLEASE submit a bug report」とか言ってますが、「5万次元の配列食わせたらclang++死んだんすけど」というレポート出したら怒られそうな気がするのでやめておきましょう。

というわけで、clang++に1万次元の配列を食わせても大丈夫ですが、5万次元の配列では死ぬようです。そのどこかに「ギリギリ死ぬ次元」がありそうですね。

## clang++にXX次元の配列を食わせると死ぬ

「clang++は何次元の配列までいけるんでしょうか？これってトリビアになりませんか？」

このトリビアの種、つまりこういうことになります。

「clang++にXX次元の配列を食わせると死ぬ」

実際に、調べてみた。

環境やコンパイラのバージョンは以下の通り。

* g++ 4.8.5
* clang++: 16.0.0

GCCのバージョンが古いのは気にしないでください。

こんなコードを書いてみましょう。コンパイラと次元を指定して、コンパイルに成功するか調べるコードです。

```rb: check2.rb
# frozen_string_literal: true

def check(cpp, n_dim)
  astr = '[1]' * n_dim
  s = <<"CPPSRC"
  #include <cstdio>
  #include <typeinfo>
  int a#{astr};
  int main(){
    printf("%s\\n",typeid(a).name());
  }
CPPSRC
  File.open('test.cc', 'w') do |f|
    f.puts s
  end
  if system("#{cpp} test.cc 2> /dev/null")
    puts "#{n_dim} OK"
    false
  else
    puts "#{n_dim} NG"
    true
  end
end

def check_clang
  (10_000..50_000).bsearch do |n|
    check('clang++',n)
  end
end

check_clang
```

2分探索で境目を調べるコードです。実行するとこんな感じになります。

```sh
$ ruby check2.rb
30000 OK
40000 NG
35000 NG
32500 NG
31250 NG
30625 OK
30938 NG
30782 NG
30704 OK
30743 NG
30724 OK
30734 OK
30739 OK
30741 NG
30740 NG
```

30739次元の配列は大丈夫でしたが、30740次元は死にました。

## GCCの場合

GCCは10万次元とか食わせても大丈夫でした。どのくらいまでいけるのか、あとコンパイルにどれくらい時間がかかるのか計測してみましょう。

```rb
def keisoku
  n = 1000
  for i in 1..10 do
    start_time = Time.now
    check("g++", n)
    end_time = Time.now
    puts "#{n} #{end_time - start_time}"
    n *= 2
  end
end
```

結果はこんな感じです。

```txt
1000 0.10042027
2000 0.145120232
4000 0.205267295
8000 0.517492657
16000 1.980355796
32000 7.271903114
64000 38.030796235
128000 258.708976165
256000 1267.16950182
512000 5749.26919743
```

次元に対してコンパイル時間を両対数プロットするとこんな感じです。

![gcc.png](/images/extremely_high_dimensional_array/gcc.png)

実線は$n^2$です。概ね次元の自乗でコンパイル時間が伸びることがわかります。512000次元でコンパイルに1時間半ほどかかっているので、100万次元だと5時間半くらいかかるでしょうか。

## まとめ

こうしてこの世界にまた一つ

新たなトリビアが生まれた。

「clang++に30740次元の配列を食わせると死ぬ」

まぁ、clang++はコンパイルに再帰を使ってるみたいなので、おそらくスタックサイズか何かで上限が決まっており、死ぬサイズは環境依存するようです。別の環境ではもっと小さい次元で死にました。

というわけで、皆さんも超多次元配列を作りたくなった場合は2万次元くらいでとめておくか、100万次元配列をコンパイルしたい場合はGCCを使うと良いと思います。

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
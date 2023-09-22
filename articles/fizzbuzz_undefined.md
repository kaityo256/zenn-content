---
title: "未定義動作でFizzBuzz"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["cpp","gcc","clang"]
published: true
---

## はじめに

たまにFizzBuzzが話題になりますね。いろんな解法があると思いますが、ここではC/C++言語の未定義動作を使ってFizzBuzzしてみましょうか。clang++にfizzを、g++にbuzzを表示してもらいます。

## コード

以下がコードです(9/22少し修正)。

```cpp
#include <cstdio>

int main(){
  const char *str[] = {"fizz", "buzz"};
  int a = 0, b = 0, c = 0;
  a = ++a + --a;
  b = --b + ++b + ++b;
  c = ++c + ++c + b;
  for (int i=1;i<16;i++){
    if (i%c==0){
      printf("%s\n",str[b]);
    }else{
      printf("%d\n",i);
    }
  }
}
```

実行結果はこんな感じになります。

### clang++

```sh
$ clang++ test.cc
test.cc:6:7: warning: multiple unsequenced modifications to 'a' [-Wunsequenced]
  a = ++a + --a;
      ^     ~~
test.cc:7:7: warning: multiple unsequenced modifications to 'b' [-Wunsequenced]
  b = --b + ++b + ++b;
      ^     ~~
test.cc:8:7: warning: multiple unsequenced modifications to 'c' [-Wunsequenced]
  c = ++c + ++c + b;
      ^     ~~
3 warnings generated.

$ ./a.out
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

clang++でコンパイルしたら、3の倍数の時だけfizzと言います。

### g++

```sh
$ g++ test.cc
$ ./a.out
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

g++でコンパイルすると、5の倍数の時だけbuzzと言います。

## 原理

複数の前置インクリメント/デクリメントが式の中に現れると、それは未定義動作を引き起こします。何が起きても文句は言えませんが、とりあえずclang++とg++で解釈が異なります。

```cpp
  int a = 0;
  a = ++a + --a;
```

は、clang++では1に、g++では0になります。

逆に、

```cpp
  int b = 0;
  b = --b + ++b + ++b;
```

は、clang++では0に、g++では1になります。これにより、`a`と`b`をそれぞれclang++であるかg++であるかのフラグに使えます。

```cpp
  int c = 0;
  c = ++c + ++c;
```

は、clang++では3に、g++では4になります。なのでさらに`b`を足して、

```cpp
  int c = 0;
  c = ++c + ++c + b;
```

とすると、clang++では3に、g++では5になります。

いや、それだけの話しなんですけど。

## 参考

何が起きているかは、以下の記事を参照してください。

* [インクリメント演算子とコンパイラの気持ち](https://zenn.dev/kaityo256/articles/increment_operators)
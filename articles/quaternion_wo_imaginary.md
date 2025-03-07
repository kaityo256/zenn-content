---
title: "絶対虚数単位を使いたくない人のための四元数表現"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["数学", "python"]
published: true
---

## はじめに

数学では、自乗すると-1になる数$i$が出てきます。これは存在しない数という意味で、虚数(imaginary number)と呼ばれます。一方、我々が普段使う数は、実際に存在する数という意味で実数(real number)と呼ばれます。そして、実数と虚数が混ざった数を複素数(complex number)といいます。複素数は高次方程式の解を表現するために導入されますが、存在しない数を使うなんて気持ち悪いですよね。そこで、虚数を使わずに、実数だけで話を作ってみましょう。

## 一次方程式

変数$x$の関数、$f(x)$を考えます。これは、$x$を決めたら$f(x)$の値が決まるので、$x$が入力、$f(x)$が出力です。一方、$f(x)$の形と値(出力)が既知である時、その値を与える$x$の値(入力)を知りたいことがよくあります。

例えば、「1冊200円のノートを何冊か買って、1000円だしたらお釣りが200円でした。ノートは何冊買ったでしょう？」といった問題では、$x$を買った冊数、$f(x)$は$x$冊買った場合の価格とすると、

$$
f(x) = 200 x
$$

なので、先程の文章を式に落とすと

$$
1000 - f(x) = 200
$$

となります。これを変形すると

$$
f(x) = 200 x = 800
$$

となります。これは$f(x)$の形と値から$x$を求める、一種の逆問題になっています。

さて、先程の式ですが、$f(x)$の定義を修正して、

$$
f(x) = 200 x - 800
$$

としましょう。すると、我々は

$$
f(x) = 0
$$

を与えるような$x$を求めなさい、という問題に帰着させることができます。これを方程式といいます。以後、適当に定義を修正して、$f(x) = 0$の形の問題のみを考えます。

一般に、実係数$a, b$を使って(ただし$a \neq 0$とする)

$$
f(x) = a x + b = 0
$$

とかけるような方程式を、一次方程式と呼びます。一次方程式の場合、解は

$$
x = -\frac{b}{a}
$$

として求まります。$a$も$b$も実数なので、解$x$も実数です。

## 二次方程式

二次方程式は、実係数$a, b, c$を用いて以下のように表される方程式です(ただし$a \neq 0$)。

$$
f(x) = a x^2 + bx + c = 0
$$

この解を求めるには、以下のように因数分解します。

$$
f(x) = a(x - \alpha)(x - \beta) = 0
$$

3つの項の積が$0$であり、$a \neq 0$ですから、$x - \alpha$もしくは$x - \beta$のどちらかが$0$です。ここから$x = \alpha$もしくは$x = \beta$が解だとわかります。

このように、高次方程式を解くとは、関数$f(x)$を因数分解する問題に帰着されます。

さて、一次方程式の場合は、係数が実数である限り、解も必ず実数でした。しかし、二次方程式では、それでは解が求まらない場合がでてきます。$f(x) = x^2 + 1$とすると、

$$
f(x) = x^2 + 1 = 0
$$

となるため、$x^2 = -1$、すなわち「自乗したら$-1$となる数」を考える必要があります。実数の範囲では解が見つからないため、「解無し」となります。

しかし、なんか工夫して、無理やり解をつくりましょう、というのが本稿の目的です。

## 基底の導入と複素数

実数とは、一本の数直線の上に定義された数、すなわち一次元の世界です。一次元の世界では解が見つからないので、二次元の世界を考えることにします。いま、2つの基底$\mathbf{e}_0, \mathbf{e}_1$を考え、これまで$a$と考えていた数は、実は$a \mathbf{e}_0$を省略していたものだ、と考えます。この世界の二次元ベクトル$(a,b)$は、基底を用いて$a \mathbf{e}_0 + b \mathbf{e}_1$と表現できます。


ここで、$(a \mathbf{e}_0 + b \mathbf{e}_1)$というベクトルと$(c \mathbf{e}_0 + d \mathbf{e}_1)$というベクトルの積を考えると、

$$
\begin{aligned}
(a \mathbf{e}_0 + b \mathbf{e}_1)(c \mathbf{e}_0 + d\mathbf{e}_1) &=
ac \mathbf{e}_0 \mathbf{e}_0 +
ad \mathbf{e}_0 \mathbf{e}_1 +
bc \mathbf{e}_1 \mathbf{e}_0 +
bd \mathbf{e}_1 \mathbf{e}_1
\end{aligned}
$$

となります。ここで、基底が満たすべき性質を考えるために、複素数の性質を「カンニング」することにしましょう。$a \mathbf{e}_0 + b \mathbf{e}_1$を、複素数$a+ bi$に対応させることにします。すると、

$$
(a + bi)(c+di) = (ac - bd) + (bc + ad)i
$$

となります。先程、基底で展開した式と比較すると、基底同士の積に以下のようなルールを設ければよいことがわかります。

$$
\begin{aligned}
\mathbf{e}_0 \mathbf{e}_0 &= \mathbf{e}_0\\
\mathbf{e}_0 \mathbf{e}_1 &= \mathbf{e}_1\\
\mathbf{e}_1 \mathbf{e}_0 &= \mathbf{e}_1\\
\mathbf{e}_1 \mathbf{e}_1 &= -\mathbf{e}_0
\end{aligned}
$$

要するに$\mathbf{e}_0$をかけても何も起きず、$\mathbf{e}_1$の自乗は$-\mathbf{e}_0$となるような基底を考えればよいことになります。

これは、行列を用いると

$$
\begin{aligned}
\mathbf{e}_0 &= \begin{pmatrix}
1 & 0 \\ 0 & 1
\end{pmatrix}\\
\mathbf{e}_1 &= \begin{pmatrix}
0 & -1 \\ 1 & 0
\end{pmatrix}
\end{aligned}
$$

と表現できます。$\mathbf{e}_0$は単位行列なのでかけても何もおきず、$\mathbf{e}_1$については

$$
\begin{pmatrix}
0 & -1 \\ 1 & 0
\end{pmatrix}
\begin{pmatrix}
0 & -1 \\ 1 & 0
\end{pmatrix}
=
\begin{pmatrix}
-1 & 0 \\ 0 & -1
\end{pmatrix}
= -\mathbf{e}_0
$$

なので、たしかに先程要請した関係式を満たしていることがわかります。

以上から、$\mathbf{e}_1$が虚数単位であり、その行列表現が

$$
\mathbf{e}_1 =
\begin{pmatrix}
0 & -1 \\ 1 & 0
\end{pmatrix}
$$

であることがわかります。

さて、この基底を使うと、例えば

$$
x^2 = -1
$$

という方程式が以下のように解けます。まず、$1$は$\mathbf{e}_0$の略と考えると、

$$
x^2 = - \mathbf{e}_0
$$

となります。ここから、

$$
x = \pm \mathbf{e}_1
$$

と解くことができます。

同様に、

$$
f(x) = x^2 -2x + 2
$$

という関数も

$$
f(x) = x^2 -2x + 2\mathbf{e}_0
$$

としてから、

$$
f(x) = (x -\mathbf{e}_0 - \mathbf{e}_1)(x - \mathbf{e}_0 + \mathbf{e}_1)
$$

と因数分解することができます(積をバラして、基底の積が満たす式を使って簡略化すると、ちゃんと元に戻ることがわかります)。

以上から、実数$a$は

$$
a \mathbf{e}_0 = \begin{pmatrix}
a & 0 \\ 0 & a
\end{pmatrix}
$$

という対角行列に、純虚数$bi$は

$$
b \mathbf{e}_1 = \begin{pmatrix}
0 & -b \\ b & 0
\end{pmatrix}
$$

という交代行列に対応することがわかります。

これを使うと、たとえば複素数$a + bi$、$c+di$はそれぞれ

$$
a + bi =  \begin{pmatrix}
a & -b \\ b & a
\end{pmatrix}
$$

$$
c + di =  \begin{pmatrix}
c & -d \\ d & c
\end{pmatrix}
$$

となるため、

$$
\begin{aligned}
(a + bi)(c+di) &= 
\begin{pmatrix}
a & -b \\ b & a
\end{pmatrix}
\begin{pmatrix}
c & -d \\ d & c
\end{pmatrix}\\
&= \begin{pmatrix}
ad-bc & -bc-ad \\ bc+ad & ad-bc
\end{pmatrix}\\
&= (ad-bc) \mathbf{e}_0 + (bc+ad) \mathbf{e}_1 \\
&\equiv (ad-bc) + (bc+ad)i
\end{aligned}
$$

と、通常の行列の積の定義により、複素数が定義されたことがわかります。

以上から、純虚数は交代行列で、複素数は二次の実正方行列として表現できることがわかりました。

## 四元数

さて、虚数の導入により、例えば

$$
a^2 + b^2 = (a+bi)(a-bi)
$$

と因数分解できるようになりました。では、これが4つの場合、すなわち

$$
a^2 + b^2 + c^2 + d^2
$$

を因数分解するにはどのようにすれば良いのでしょうか？

これは、複素数だけでは因数分解することができません。そこで、ハミルトンは虚数単位$i$だけでなく、$j$、$k$という新たな数を考え、以下の関係式を要求しました。

$$
\begin{aligned}
i^2 &= j^2 = k^2 = -1 \\
ij &= -ji = k\\
jk &= -kj = i\\
ki &= -ik = j\\
\end{aligned}
$$

$i, j, k$は「自乗すると$-1$」という虚数単位の性質を持っていますが、2つの積が別の単位を生み出し、さらに積が非可換になっています。先程の関係式は

$$
i^2 = j^2 = k^2 = ijk = -1
$$

とまとめることもできます。例えば

$$
ijk = -1
$$

の左側から$i$をかけると、

$$
-jk = -i
$$

となり、$jk = i$の関係式が得られます(他も同様)。

これらの単位を使うと、先程の式は以下のように因数分解できます。

$$
a^2 + b^2 + c^2 + d^2
=
(a + bi + cj + dk)
(a - bi - cj - dk)
$$

我々は先程と同様に、世界を4次元に拡張し、その基底$\mathbf{e}_0,\mathbf{e}_1,\mathbf{e}_2,\mathbf{e}_3$を使って上記の関係式を満たすものを探すことにします。すなわち、

$$
\begin{aligned}
\mathbf{e}_1\mathbf{e}_1 &= \mathbf{e}_2\mathbf{e}_2 = \mathbf{e}_3\mathbf{e}_3 = -\mathbf{e}_0 \\
\mathbf{e}_1\mathbf{e}_2 &= -\mathbf{e}_2\mathbf{e}_1 = \mathbf{e}_3\\
\mathbf{e}_2\mathbf{e}_3 &= -\mathbf{e}_3\mathbf{e}_2 = \mathbf{e}_1\\
\mathbf{e}_3\mathbf{e}_1 &= -\mathbf{e}_1\mathbf{e}_3 = \mathbf{e}_2
\end{aligned}
$$

を満たすような実行列表現を求めましょう、というのが本項の目標です。四元数の単位$i,j,k$を数だと思うと不思議ですが、行列だと思うと、まぁそういうのもあるかな、と思える気がします。

さて、また「カンニング」しましょう。我々は、パウリ行列が四元数の表現になっていることを知っています。パウリ行列とは以下のような行列です。

$$
\begin{aligned}
\sigma_1 &= \begin{pmatrix}
0 & 1 \\ 1 & 0
\end{pmatrix} \\
\sigma_2 &= \begin{pmatrix}
0 & -i \\ i & 0
\end{pmatrix} \\
\sigma_3 &= \begin{pmatrix}
1 & 0 \\ 0 & -1
\end{pmatrix} 
\end{aligned}
$$

パウリ行列は$\sigma_x, \sigma_y, \sigma_z$と書くことが多いですが、後の便利のために添字を1,2,3にしています。これを使って、以下のような複素行列を考えます。

$$
s_k = -i \sigma_k \qquad (k=1,2,3)
$$

また、単位行列として

$$
s_0 = \begin{pmatrix}
1 & 0 \\ 0 & 1
\end{pmatrix}
$$

も定義しておきます。

すると、これらは

$$
s_1^2 = s_2^2 =  s_3^2 = s_1 s_2 s_3 = - s_0
$$

を満たすため、四元数の単位になっています。

しかし、これらは要素として複素数を持つ複素行列になっています。我々は虚数単位なんてわけがわからないものは使いたくないので、先程の複素数の行列表現を使って、四元数の実行列表現を求めることにしましょう。

例えば$s_1$は

$$
s_1 = - i \sigma_1 = \begin{pmatrix}
0 & -i \\
-i & 0
\end{pmatrix}
$$

です。ここで、虚数単位の行列表現

$$
i \equiv \begin{pmatrix}
0 &-1\\
1 & 0
\end{pmatrix}
$$

を使って、以下のようなテンソル積を考えます。

$$
\begin{aligned}
\mathbf{e}_1 &\equiv \begin{pmatrix}
0 & -1\\
-1 & 0
\end{pmatrix}
\otimes
\begin{pmatrix}
0 &-1\\
1 & 0
\end{pmatrix} \\
&=
\begin{pmatrix}
0 & 0 & 0 & 1\\
0 & 0 & -1 & 0\\
0 & 1 & 0 & 0\\
-1 & 0 & 0 & 0
\end{pmatrix}
\end{aligned}
$$

ようするに$i$の代わりにその行列表現を突っ込んだものになっています。これにより、基底$\mathbf{e}_1$は4行4列の実行列として表現できました。

$\mathbf{e}_3$も同様です。

$$
\begin{aligned}
\mathbf{e}_3 &\equiv \begin{pmatrix}
1 & 0\\
0 & -1
\end{pmatrix}
\otimes
\begin{pmatrix}
0 & -1\\
1 & 0
\end{pmatrix} \\
&=
\begin{pmatrix}
0 & 1 & 0 & 0\\
-1 & 0 & 0 & 0\\
0 & 0 & 0 & -1\\
0 & 0 & 1 & 0
\end{pmatrix}
\end{aligned}
$$


$\mathbf{e}_2$に関しては

$$
\begin{aligned}
\mathbf{e}_2 &\equiv \begin{pmatrix}
0 & -1\\
1 & 0
\end{pmatrix}
\otimes
\begin{pmatrix}
1 & 0\\
0 & 1
\end{pmatrix} \\
&=
\begin{pmatrix}
0 & 0 & -1 & 0\\
0 & 0 & 0 & -1\\
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0
\end{pmatrix}
\end{aligned}
$$

と、実数$1$の代わりに二次元単位行列を突っ込んだものになります。

これらが先程の関係式を満たしていることを確認しましょう。面倒なのでPythonにやらせましょうか。

```py
import numpy as np
e0 = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])
e1 = np.array([[0,0,0,1],[0,0,-1,0],[0,1,0,0],[-1,0,0,0]])
e2 = np.array([[0,0,-1,0],[0,0,0,-1],[1,0,0,0],[0,1,0,0]])
e3 = np.array([[0,1,0,0],[-1,0,0,0],[0,0,0,-1],[0,0,1,0]])

# 自乗すると-1
(e1 @ e1 == -e0).all() # => True
(e2 @ e2 == -e0).all() # => True
(e3 @ e3 == -e0).all() # => True

# 非可換性
(e1@e2@e3 == -e0).all() # => True
# 上だけで十分だが、念のため
(e1 @ e2 == e3).all() # => True
(e2 @ e3 == e1).all() # => True
(e3 @ e1 == e2).all() # => True
```

成り立っていますね。

最終的に、以下のような4つの行列が得られました。

$$
\begin{aligned}
\mathbf{e}_0 &=
\begin{pmatrix}
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1
\end{pmatrix} \\
\mathbf{e}_1 &=
\begin{pmatrix}
0 & 0 & 0 & 1\\
0 & 0 & -1 & 0\\
0 & 1 & 0 & 0\\
-1 & 0 & 0 & 0
\end{pmatrix} \\
\mathbf{e}_2 &=
\begin{pmatrix}
0 & 0 & -1 & 0\\
0 & 0 & 0 & -1\\
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0
\end{pmatrix} \\
\mathbf{e}_3 &=
\begin{pmatrix}
0 & 1 & 0 & 0\\
-1 & 0 & 0 & 0\\
0 & 0 & 0 & -1\\
0 & 0 & 1 & 0
\end{pmatrix} \\
\end{aligned}
$$

これらを使うと、最初の因数分解の問題は、

$$
(a^2 + b^2 + c^2 + d^2)\mathbf{e}_0
=
(a \mathbf{e}_0+ b\mathbf{e}_1 + c\mathbf{e}_2 + d\mathbf{e}_3)
(a \mathbf{e}_0- b\mathbf{e}_1 - c\mathbf{e}_2 - d\mathbf{e}_3)
$$

と書くことができます。これが我々がやりたかったことでした。

## まとめ

虚数単位が2次の実正方行列で、四元数の単位が4次の実正方行列で書けることを見ました。一般に、何か$i$だの$j$といった抽象的なベクトル同士の積が与えられている時、その積を満たすような行列を表現と呼びます。虚数単位の「自乗すると-1」という積を満たす行列表現が2次の実交代行列で与えられます。また、四元数の単位の複素行列表現がパウリ行列(に$-i$をかけたもの)になっていますが、その実行列表現は4行4列で与えられることを見ました。

僕は最初に行列の積の定義を見た時、「なんでこんなややこしい積を考えなきゃいけないんだ」と不思議に思いましたが、今では「なんでこの積の定義だけでこんなにたくさんのものを表現できるんだろう」と不思議に思います。

本稿により少しでも行列の面白さが伝われば幸いです。

## 合わせて読みたい

* [二次方程式の話](https://zenn.dev/kaityo256/articles/quadratic_equation)
* [三角関数の話](https://zenn.dev/kaityo256/articles/trigonometric_function)
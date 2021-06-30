---
title: "Langevin方程式と確率微分方程式"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["数学","確率過程","分子動力学法","python"]
published: false
---

## はじめに

Langevin方程式という方程式があります。例えばこんなのです。

$$
\dot{v} = -\gamma v + \sqrt{2D} \hat{R}
$$

ただし、$\gamma$と$D$は定数で、$\hat{R}$は白色雑音で、

$$
\begin{aligned}
\left<\hat{R}(t)\right> &= 0 \\
\left<\hat{R}(t)\hat{R}(t')\right> &= \delta(t-t')
\end{aligned}
$$

を満たすような確率変数です。この方程式は、水の中の粒子の運動を表しており、$-\gamma v$が水の抵抗による散逸を、$\sqrt{2D} \hat{R}$の項が水分子の衝突による揺動を表現しています。定常分布は以下のガウス分布になります。

$$
f(v) = \frac{\exp{(-\beta v^2/2)}}{\sqrt{2 \pi/\beta}}
$$

ただし、$\beta = \gamma/D$です。

さて、微分方程式を解くとは、微分している変数について積分し、原始関数を求めることです。しかし、この方程式には$\hat{R}$という確率変数が含まれています。このように確率変数を含む微分方程式を確率微分方程式と呼びます。Langevin方程式は確率微分方程式の一種です。こいつを積分する、ということはどういうことか真面目に考えてみましょう、というのが本稿の目的です。

## 積分とは

そもそも積分とはなんだったでしょうか？いま、ある関数$y=f(x)$を$x_s < x < x_e$の区間で積分したいとしましょう。その値を$A$とすると

$$
A = \int_{x_s}^{x_e} f(x) dx
$$

です。この意味は、関数$f(x)$の区間$x_s < x < x_e$における面積です。とりあえず区間を$N$等分して、$f(x)$の面積を短冊の和として近似してみましょう。

![langevin_equation/riemann.png](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/riemann.png)

つまり、

$$
A \sim \sum_{k=0}^{N-1} f(x_k) h
$$

ただし、$h = (x_e-x_s)/N$、$x_k = x_s + hk$です。$f(x)$がなめらかなら、$N$無限大の極限でこの和は収束しそうです。その収束値を定積分と定義することにしましょう。つまり、以下を定積分の定義とします[^1]。

[^1]: ちゃんと定義するなら、$\varepsilon$-$\delta$論法を使いますが、ここでは詳細には触れません。

$$
\int_{x_s}^{x_e} f(x) dx \equiv \lim_{N\rightarrow \infty} \sum_{k=0}^{N-1} f(x_k)h
$$

ここで、分割は等間隔でなくてもかまいません。

$$
\int_{x_s}^{x_e} f(x) dx \equiv \lim_{N\rightarrow \infty} \sum_{k=0}^{N-1} f(x_k) (x_{k+1} - x_k)
$$

さらに言えば、今は区間$(x_k, x_{k+1})$の左端での関数の値$f(x_k)$を代表点として使って短冊を作っていますが、右側を使っても、左右の平均値を使っても同じ収束値が得られます(**伏線**)。

$$
\begin{aligned}
\int_{x_s}^{x_e} f(x) dx &\equiv \lim_{N\rightarrow \infty} \sum_{k=0}^{N-1} f(x_k) (x_{k+1} - x_k) \\
&= \lim_{N\rightarrow \infty} \sum_{k=0}^{N-1} f(x_{k+1}) (x_{k+1} - x_k) \\
&= \lim_{N\rightarrow \infty} \sum_{k=0}^{N-1} \frac{f(x_{k+1})+f(x_k)}{2} (x_{k+1} - x_k) \\
\end{aligned}
$$

![refpoint](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/refpoint.png)

さて、確率微分方程式を積分するためには、確率変数を積分する必要があります。例えば

$$
\dot{x} = \hat{R}
$$

という微分方程式において、初期条件$x(t=0)$から、任意の時刻における$x(t)$の値を求めるためには、

$$
x(t) = x(0) + \int_0^t \hat{R}(t) dt
$$

を計算する必要があります。これを定義するためには、積分区間を分割し、

$$
\int_0^t \hat{R}(t) dt \equiv \lim_{N\rightarrow \infty}\sum_{k=0}^{N-1} \hat{R}(t_k) h
$$

みたいなものを考えたくなります。しかし、右辺には確率変数があるため、この和がどういうものかは自明ではありません。一般にはこれはWiener過程として「定義」してしまいますが、これを離散的なランダムウォークからの極限として導いてみましょう。

## ランダムウォークと連続極限

以下の確率微分方程式を考えます。

$$
\dot{x} = \hat{R}
$$

ただし$\hat{R}$は$\left<\hat{R}\right>=0$、$\left<\hat{R}(t)\hat{R}(t')\right>=\delta(t-t')$を満たす確率変数です。これは連続時間、連続空間におけるランダムウォークを表していると考えることができます。簡単のため、時刻$t=0$で原点にいたとしましょう。形式的に積分すると、

$$
x(t) = \int_0^t \hat{R} dt
$$

となります。この右辺はよくわからないので、左辺を考えてみましょう。連続時間・空間だと難しいので、まずは離散時間、離散空間を考えます。毎回コインを投げ、表なら右に、裏なら左に一歩進むランダムウォークを考えます。後で連続極限を取るために、一歩の長さを$h$としておきましょう。裏と表が出る確率はいずれも1/2であるとします。

![fig](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/limit.png)

$k$ステップ目の場所を$x_k$とすると、

$$
x_{k+1} = x_k + h \hat{R}_k
$$

です。ただし$\hat{R}_k$は$1$か$-1$の値をそれぞれ1/2の確率で取る確率変数です。また、異なるステップ間は無相関であるとします。つまり、

$$
\begin{aligned}
\left< \hat{R}_k \right> & =0 \\
\left< \hat{R}_k\hat{R}_l \right> &= \delta_{k,l} \\
\end{aligned}
$$

を満たします。連続版の確率変数$\hat{R}$の振る舞いと似ていますね。さて、時刻$t=0$において、原点にいたとします。つまり$x_0 = 0$です。我々が知りたいのは、ある時刻$t$において、場所$x$にいる確率$P(x,t)$です。$n$回コインを投げたうち、表が出た枚数を$\hat{X}$としましょう。$k$枚が表であるような確率は、確率$1/2$、試行回数$n$の二項分布

$$
P(\hat{X}=k) =
\begin{pmatrix}
n \\k
\end{pmatrix}
\frac{1}{2^n}
$$

に従います。この分布の1次と2次のモーメントはすぐにわかります。

$$
\begin{aligned}
\left<\hat{X}\right> &= n/2 \\
\left<\hat{X}^2\right> &= n/4
\end{aligned}
$$

さて、$\hat{X}$枚が表だったということは、右に$\hat{X}$歩、左に$n-\hat{X}$歩進んでいるので、位置は$x_n = (2\hat{X} -n)h$の場所にいます。平均の位置$\left<x_n\right>$と、平均二乗変位$\left<x_n^2\right>$を計算してみましょう。

$$
\begin{aligned}
\left<x_n\right> &= \left< 2\hat{X}-n\right> h^2 \\
&=0\\
\left<x_n^2\right> &= \left< (2\hat{X}-n)^2\right> h^2 \\
&= 4 \left< \hat{X}^2\right>h^2 - 2n \left< \hat{X}\right>h^2 + n^2h^2 \\
&= nh^2
\end{aligned}
$$

すなわち、ランダムウォークでは平均自乗変位はステップ数に比例します。

さて、試行回数が大きい時、二項分布は同じ期待値、分散を持つ正規分布で良く近似できます。期待値$\mu$、分散$\sigma^2$を持つ正規分布を$\mathcal{n}(\mu, \sigma^2)$とするなら、確率$p=1/2$、試行回数$N$の二項分布の期待値は$N/2$、分散は$N/4$ですから、$N$回コインを投げて$k$回表がでる確率は、正規分布$\mathcal{N}(N/2, N/4)$で表現できます。$N$回コインを投げて$k$回表が出たとき、位置は$(2k-N)h$の場所にいます。したがって、$N$ステップ後の場所$x_N$の分布は、平均$0$、分散$Nh^2$の正規分布 $\mathcal{N}(0, Nh^2)$で書けます。

$$
P(x_N = x) \sim \frac{1}{\sqrt{2 \pi Nh^2}} \exp\left(-\frac{x^2}{2Nh^2} \right)
$$

さて、ランダムウォークにおいて、平均自乗変位$\left<x_N^2\right>$は$Nh^2$と、ステップ数$N$に比例するのでした。なので、$N$が大きい時、これを連続的な「時間」だとみなすことができそうです。これは、$Nh^2=t$を固定したまま$N$無限大の極限をとることに対応します。そして、改めて$N$ステップ後の時刻を$t$とみなすと、時刻$t$において位置$x(t)$が$x$付近にいる確率は

$$
P(x <x(t) < x + dx) = \frac{1}{\sqrt{2 \pi t}} \exp\left(-\frac{x^2}{2t} \right) dx
$$

となります[^2]。つまり、時刻$t=0$において原点にいた場合、時刻$t$で座標$x$にいる確率は期待値0、分散$t$の正規分布$\mathcal{N}(0,t)$に従う、ということです。

[^2]: 確率変数が連続の場合は「この範囲にいる確率」と区間を指定する必要があります。

離散的なランダムウォークを表す式はこうでした。

$$
x_{k+1} = x_k + h\hat{R}_k
$$

0ステップ目から$N$ステップ目までの和を取ると、

$$
x_{N} = \sum_{k=0}^N \hat{R}_k h
$$

$x_{N}$の$N$無限大の連続極限を取ったものを$x(t)$とみなします。これは、時間刻みを$\tau$とし、$\tau = t/N$という形で$N$無限大極限をとっていることに対応します。

$$
\lim_{N\rightarrow \infty} x_N = x(t)
$$

また、右辺を積分と同一視することで、連続版の$\hat{R}$を離散版の$\hat{R}_k$を用いて以下のように定義することとします。

$$
\int_0^t \hat{R}dt \equiv \lim_{N\rightarrow \infty} \sum_k^N \hat{R}_k h
$$

ここで、$Nh^2=t$を固定したまま$N$無限大の極限を取っていることに注意しましょう。通常のRiemann和では刻み幅は$h \sim 1/N$のように振る舞いますが、ランダムウォークの極限を取る時には$h \sim 1/\sqrt{N}$のような形で極限を取る必要があります。時間刻みは$\tau\sim 1/N$だったので、極限を取る時の時間と空間の「小さくなる早さ」が違います。

さて、$x(t)$の分布は平均0、分散$t$の正規分布$\mathcal{N}(0,t)$に従うのでした。したがって、$\hat{R}$を積分したものもそれに従います。

$$
P\left(x<  \int_0^t \hat{R}dt <x+dt \right) = \frac{1}{\sqrt{2 \pi t}} \exp\left(-\frac{x^2}{2t} \right) dx
$$

これが欲しかったものでした。ここから、例えば以下のLangevin方程式を数値積分できるようになります。

$$
\dot{v} = -\gamma v + \sqrt{2D} \hat{R}
$$

時間刻みを$h$とすると、Euler法の要領で以下のスキームを構成できます。

$$
v(t+h) = v(t) + -\gamma v(t) h  + \sqrt{2D} w
$$

ただし、$w$は平均$0$、分散$h$に従う確率変数です。Pythonなら`numpy.random.normal(0, h**0.5)`で得ることができます。この積分スキームをEuler-Maruyama法と呼びます。ちょっと試してみましょう。$\gamma=D=1$とします。

```py
import numpy as np
from matplotlib import pyplot as plt
from numba import jit

AVE = 1000
N = 100000
NA = N//AVE
h = 0.01

@jit
def additive_euler_maruyama(N):
  v = 0
  data = []
  for _ in range(N):
    v += - v * h + np.random.normal(0,np.sqrt(2.0*h))
    data.append(x)
  return data
```

`additive_euler_maruyama`は、先程の式をそのまま実装したものです。これで`data`に時系列が帰ってくるので、その定常分布を調べてみましょう。

時系列から分布関数を作る関数`dist`はこんな感じになります。ソートして累積分布関数を求め、それを微分することで分布関数を求めています(参考：[累積分布関数をソートで求める](https://qiita.com/kaityo256/items/690a463b6b865da80de6))。ただし、きれいな分布にするために、部分的に平均をとっています。

```py
def dist(data):
  d = sorted(data)
  d = [np.average(d[i*AVE:(i+1)*AVE]) for i in range(NA)]
  t = np.array([i/N for i in range(N)])
  t = [np.average(t[i*AVE:(i+1)*AVE]) for i in range(NA)]
  d = np.array(d)
  t = np.array(t)
  x = []
  y = []
  for i in range(NA-1):
    v = (t[i+1] - t[i])/(d[i+1]-d[i])
    x.append((d[i+1]+d[i])*0.5)
    y.append(v)
  return np.array(x),np.array(y)
```

プロットしてみましょう。

```py
d1, f1 = dist(additive_euler_maruyama(N))
fig, ax = plt.subplots()
theory = np.exp(-d1**2/2)/np.sqrt(3.14*2)
ax.plot(d1,f1)
ax.plot(d1,theory)
fig.show()
```

![additive](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/additive.png)

ちゃんとガウス分布になっていますね。

## Ito積分とStratonovich積分

さて、確率変数$\hat{R}$というよくわからないものを時間幅$t$だけ積分した場合、平均$0$、分散$t$の正規分布に従う確率変数とみなすことができることがわかりました。これは積分区間のとり方(Riemann分割の仕方)に無関係に定義できるため、めでたしめでたしな気がしますが、よくわからないものを積分するとよくわからないことがおきます。

まず、Langevin方程式において、確率変数にかかっている係数が定数である場合、それを相加性ノイズ(additive noise)と呼びます。以下のような方程式の場合は定数なので相加性です。

$$
\dot{v} = -\gamma v + \sqrt{2D} \hat{R}
$$

ここで$D$は拡散定数です。問題は、ノイズに変数がかかっている場合です。例えば拡散定数が速度に依存する場合などです。

$$
\dot{v} = -\gamma v + \sqrt{2D(v)} \hat{R}
$$

ここでは$D$が$v$の関数になっています。このようなノイズを相乗性ノイズ(multiplicative noise)、この過程を相乗過程と呼びます[^4]。

[^4]: multiplicativeの日本語訳は一定しません。相乗性、相乗的、乗法的などと呼ばれるようです。同様にadditiveも加法的とも訳されるようです。

簡単な相乗過程の例として、こんな式を考えましょう。

$$
\dot{x} = f(x)\hat{R}
$$

$t$から$t+h$まで形式的に積分します。

$$
\int_{t}^{t+h} \dot{x}dt = \int_{t}^{t+h} f(x)\hat{R} dt
$$

$h$が小さい時、右辺を「短冊」で近似したくなります。

$$
\int_{t}^{t+h} f(x)\hat{R} dt \sim f(x_t)w
$$

ただし、$x_t$は時刻$t$における座標$x(t)$で、$w$は平均$0$、分散$h$の確率変数です。この極限として定義される積分を伊藤積分と呼びます[^5]。

[^5]: 普通はWiener過程で定義しますが、ここでは普通の積分っぽく表記しています。

ここでは短冊の高さとして積分区間の左端を使いましたが、時刻$t$と$t+h$の平均値を使うこともできます。

$$
\int_{t}^{t+h} f(x)\hat{R} dt \sim \frac{f(x_{t+h})+f(x_t)}{2}w
$$

この極限として定義される積分をStratonovich積分といいます。通常のRiemann積分では、「短冊」の高さの参照点をどこにとっても結果は同じでした。しかし、確率過程においては「短冊」の高さをどこにとるかによって極限の行き先が異なってしまいます。すなわち、伊藤積分とStratonovich積分は異なる公式を与えます。これは、確率微分方程式を、どう解釈するか、という問題となります。数値解法も解釈に依存し、もちろんその結果も解釈に依存します。

![fig](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/representation.png)

以下の乗法過程を考えてみます。

$$
\dot{x} = -x^3 + x \sqrt{2} \hat{R}_1 + \sqrt{2}\hat{R}_2
$$

$\hat{R}_1$と$\hat{R}_2$は独立な白色雑音で、理論曲線が簡単になるように$\sqrt{2}$をつけてあります。$\hat{R}_1$に$x$がかかっているため、結果が解釈に依存します。二つ揺動力をつけたのは、$\hat{R}_1$だけだと$x=0$の時に$\dot{x}=0$となり、変数の符号が変わらなくなる(エルゴード性が満たされなくなる)のを防ぐためです。

これを伊藤解釈で数値積分する場合は簡単です。単純にEuler-Maruyama法を適用すれば良いので、時間刻みを$h$として

$$
x_{t+h} = x_t - x_t^3h - x_t * w_1 + w_2
$$

とするだけです。ただし$w_1$、$w_2$は平均$0$、分散$2h$の白色雑音です。

一方、Stratonovich解釈を採用すると、確率変数にかかっている係数の部分は一つ先のステップの値との平均値を使うので、こんな感じになります。

$$
x_{t+h} = x_t - x_t^3h - \frac{x_{t+h}+x_t}{2} * w_1 + w_2
$$

右辺に未知の値である$x_{t+h}$があらわれてしまいました。つまり、本質的に陰解法となります。もっとも単純には、まず伊藤解釈で$x_{t+h}$を評価してやり、その値を使ってStratonovich解釈を実現することでしょう。

$$
\begin{aligned}
x_{t+h}^I &= x_t - x_t^3h - x_t * w_1 + w_2\\
x_{t+h} &= x_t - x_t^3h - \frac{x_{t+h}^I+x_t}{2} * w_1 + w_2
\end{aligned}
$$

これをTwo-step法と呼び、Stratonovich解釈で数値積分を行うもっとも簡単な方法の一つです。

実際にシミュレーションしてやりましょう。伊藤解釈で数値積分を行う関数を`multiplicative_euler_maruyama`、Stratonovich解釈で数値積分を行う関数を`multiplicative_two_step`として実装してあります。

```py
import numpy as np
from matplotlib import pyplot as plt
from numba import jit
AVE = 1000
N = 100000
NA = N//AVE
h = 0.01

@jit
def multiplicative_euler_maruyama(N):
  x = 0
  data = []
  for _ in range(N):
    w1 = np.random.normal(0,np.sqrt(2*h))
    w2 = np.random.normal(0,np.sqrt(2*h))
    x += -x*x*x*h
    x += x*w1
    x += w2
    data.append(x)
  return data

@jit
def multiplicative_two_step(N):
  x = 0
  data = []
  for _ in range(N):
    w1 = np.random.normal(0,np.sqrt(2*h))
    w2 = np.random.normal(0,np.sqrt(2*h))
    x_i = x + (-x * x * x) * h + x * w1 + w2
    x = x + (-x * x * x) * h  + (x+x_i)*0.5*w1 + w2
    data.append(x)
  return data
```

伊藤解釈とStratonovich解釈の分布関数をプロットしてみましょう。

```py
d1, f1 = dist(multiplicative_euler_maruyama(N))
d2, f2 = dist(multiplicative_two_step(N))
fig, ax = plt.subplots()
ax.plot(d1,f1)
ax.plot(d2,f2)
```

![plot](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/plot.png)

明らかにずれています。

今回のケースは定常分布関数の厳密解が求まります[^exact]。伊藤解釈の場合はこんな感じです。

[^exact]: 本稿では定常分布関数は導きません。いつか導出を書きます(多分)。

$$
f_\mathrm{I}(x) = \frac{1}{C} \frac{\exp(-x/2)}{\sqrt{1+x^2}}
$$

$C \sim 1.98$は規格化定数です。Stratonovich解釈の場合はガウス分布になります。

$$
f_\mathrm{S}(x) = \frac{\exp(-x^2/2)}{\sqrt{2 \pi}}
$$

重ねてプロットしてみましょう。

```py
d1, f1 = dist(multiplicative_euler_maruyama(N))
d2, f2 = dist(multiplicative_two_step(N))
fig, ax = plt.subplots()
ito = np.exp(-d1**2/2)/np.sqrt(1+d1**2)/1.98
stratonovich = np.exp(-d1**2/2)/np.sqrt(3.14*2)
ax.plot(d1,f1)
ax.plot(d2,f2)
ax.plot(d1,ito,color='blue',label="Ito")
ax.plot(d1,stratonovich,color='red',label='Stratonovich')
ax.legend()
```

![plot](https://github.com/kaityo256/zenn-content/raw/main/articles/langevin_equation/theory.png)

それぞれ理論曲線と一致していますね。

## まとめ

微分方程式に確率変数を含むような確率微分方程式の積分を考えてみました。確率変数$\hat{R}$は、連続だがいたるところ微分不可能という不思議な関数で、それを積分しようとすると通常のRiemann積分の定義では一意に定義できず、「どう解釈するか」という任意性が生じます。そのため、同じ微分方程式でも、「どう解釈したか」によって数値解法が異なり、もちろん結果も異なります。解釈の方法は無限にありますが、広く使われているのは伊藤解釈とStratonovich解釈で、それぞれ一長一短があります。二つの解釈をいったりきたりすることもあるので、相乗的なノイズを含む確率微分方程式を扱う場合は「いまどちらの解釈を使っているか」を意識しなければなりません。なお、ノイズが相加的な場合は両者は同じ結果を与えるので気にしなくてOKです。

Langevin方程式は揺動散逸定理の導出やFokker-Planck方程式の議論などいろいろおもしろい話題がありますが、本稿では触れられませんでした。別の機会にどこかで書ければと思っています。

## 参考文献

* [Multiplicativeなノイズを持つLangevin方程式とIto/Stratonovich解釈](https://qiita.com/kaityo256/items/6e9957b0739f5a3690f2)
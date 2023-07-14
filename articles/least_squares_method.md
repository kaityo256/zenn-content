---
title: "最小二乗法の話"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["数学","math"]
published: true
---

## はじめに

最小二乗法はデータ解析の基本ですが、意外にその内容の理解が難しかったりします。特に、入力データと出力データの積の和が出てくる理由があいまいな人も多いんじゃないでしょうか。以下では、最小二乗法の公式の意味をちょっと考えてみたいと思います。

## 最小二乗法

何か実験をして、観測値を得ることを考えます。例えば抵抗値のわからないものに、様々な電圧をかけて、流れる電流を測ったとしましょう。
この時、入力電圧を$x$、出力電流を$y$とすると

$$
y = a x
$$

という比例関係が期待されます。この比例定数$a$を実験から精度よく求めたい時、どうすればよいでしょうか？

実験を$N$回繰り返すことにして、$i$番目の実験の入力電圧$x_i$に対し、出力電流$y_i$を得たとしましょう。このデータセット$(x_i, y_i)$を使って、最もよく$a$を推定したい、というのが本稿の目的です。

ここで考えなくてはいけないのが「最も良く$a$を推定する」の「良い推定」とはどういうものか、ということです。そこで、予測値と、実際の値の差を考えます。入力電圧が$x_i$である時、我々は$y=ax$という形を期待しているので、予測値は$a x_i$になります。しかし、実際の値は$y_i$なので、その差

$$
\varepsilon_i = y_i - a x_i
$$

を考えます。これを残差と呼びます。この残差は正にも負にもなるため、この二乗和を全体の誤差ということにしましょう。

$$
\begin{align}
E &\equiv \sum_i^N (\varepsilon_i)^2 \\
&= \sum_i^N(y_i - a x_i)^2 \\
&= a^2 \sum_i^N x_i^2 - 2a \sum_i^N x_i y_i + \sum_i^N y_i^2
\end{align}
$$

さて、この誤差は、比例定数$a$の関数です。$a$が大きすぎても小さすぎても誤差が大きくなるので、どこかにちょうど良い$a$の値があるでしょう。その「ちょうど良い」値のとき、$a$を増やしても減らしても$E$の値は大きくなるはずです。したがって、$E$を$a$で微分してゼロとなる点が、$E$を最小にする$a$です。$E$を$a$で微分すると、

$$
\frac{dE}{da} = 2a \sum_i^N x_i^2 - 2 \sum_i^N x_i y_i 
$$

これがゼロとなるのですから、最終的に$a$の推定値は

$$
a = \frac{\sum_i^N x_i y_i }{\sum_i^N x_i^2 }
$$

となります。これは、よく知られた最小二乗法となります。$y=ax$でフィッティングするタイプの最小二乗法では、分母に入力データの分散、分子に入力データと出力データの共分散が現れます。その意味をもう少し考えてみましょう。

## 最小二乗法の意味

もともと、我々が欲しいのは、$y=ax$の傾きでした。もし、データが一つしかなければ、その傾きは

$$
a = \frac{y_1}{x_1}
$$

と、入力と出力の比で表すしかありません。これを、データ1による$a$の推定値$a_1$としましょう。同様に$a_2, a_3, \cdots$が定義されるので、その平均、すなわち

$$
\tilde{a} = \frac{1}{N} \sum_i^N \frac{y_i}{x_i}
$$

で$a$を推定しても良さそうです。先程の推定値

$$
a = \frac{\sum_i^N x_i y_i }{\sum_i^N x_i^2 }
$$

とは何が違うのでしょうか？

実は、最小二乗法による$a$の推定値は、入力データ$x_i$の値が大きいほど、大きな重みを持って足していることに対応しています。

$y=ax$という形で、$x$と$y$から傾き$a$を推定したい時、$(x, y) = (1.1, 0.9)$のデータよりも、$(x, y) = (9.9, 10.1)$のデータの方が信頼できます。そこで、原点から遠いほど、それに比例した重みをつけて足すことにします。ここから分子の

$$
\sum_i^N x_i y_i
$$

の項が出てきます。同様に、分母も同じ重みを考慮しなければならないため、最終的に

$$
a = \frac{\sum_i^N x_i y_i }{\sum_i^N x_i^2 }
$$

が出てきます。つまり、最小二乗法は「$y=ax$型のフィッティングをするなら、我々は原点から遠いデータほど重視するよ」というポリシーを含意します。

## 異なる誤差による定義

逆に、各データセットによる傾きの推定値の単純平均、すなわち

$$
\tilde{a} = \frac{1}{N} \sum_i^N \frac{y_i}{x_i}
$$

を与える誤差を考えることができます。以下のような残差を考えましょう。

$$
\tilde{\varepsilon}_i \equiv a - \frac{y_i}{x_i}
$$

すなわち、データから求めた傾きがどれだけ正しいかを示すものです。この二乗和を全体の誤差と定義します。

$$
\begin{align}
\tilde{E} &\equiv \sum_i^N \tilde{\varepsilon}_i^2\\
&= \sum_i^N \left(a - \frac{y_i}{x_i} \right) \\
&= N a^2 - 2 a \sum_i^N\frac{y_i}{x_i} + \sum_i^N \left(\frac{y_i}{x_i}\right)^2
\end{align}
$$

$a$で微分すると

$$
\frac{d\tilde{E}}{da} = 2N a - 2 \sum_i^N\frac{y_i}{x_i}
$$

これがゼロとなるような$a$は、先程考えた、傾きの単純平均による推定値

$$
\tilde{a} = \frac{1}{N} \sum_i^N \frac{y_i}{x_i}
$$

となります。

## まとめ

データセット$(x_i, y_i)$が与えられた時、$y=ax$の形でフィッティングし、$a$を求めたい時、「測定値と推定値の差」を残差として、その二乗和を最小にする$a$を求めることで、いわゆる最小二乗法の公式

$$
a = \frac{\sum_i^N x_i y_i }{\sum_i^N x_i^2 }
$$

が出てきます。この式には「原点から離れているデータほど大きい重みを持って考慮する」という意味があります。

逆に、「傾きの測定値と推定値の差」を残差とし、その二乗和を最小にしようとすると、傾きの推定値として各データセットから求まる傾きの単純平均の形

$$
a = \frac{1}{N} \sum_i^N \frac{y_i}{x_i}
$$

が出てきます。こちらは分散や共分散が出てこない簡単な式になり、「原点からの距離に対して重みをかけたりせず、全てのデータを平等に扱う」というポリシーを採用したことになります。

ここで注意すべきは「残差の二乗和を最小にする」という意味でどちらも「最小二乗法」になっていることです。一般に最小二乗法というと前者を指しますが、後者を排除する理由は全くありません。我々が普段「推定の良さとして前者を選ぶ」という選択をしている、ということです。

一般に何かを推定する際には、「何が良い推定であるか」を定義する必要があり、そこにはなんらかの意思決定があります。最も簡単な$y=ax$型の最小二乗法によりフィッティングでそれがわかりやすい見られる例なので挙げてみました。参考になれば幸いです。
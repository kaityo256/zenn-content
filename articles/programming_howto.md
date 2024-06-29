---
title: "プログラム、下から作るか？上から作るか？"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python"]
published: false
---

## TL;DL

* プログラムは「下から組む方法」と「上から組む方法」がある
* プログラムを組む時は少しずつテストしながら組む

## はじめに

なにかゼロからプログラムを組むとします。そのプログラムのアルゴリズムや、何をやるべきかはなんとなくわかっているけれど、どこから手をつけてよいかがわからず、ChatGPTに全部書かせて、その後修正できずに困る、という事例を何度か観測しています。

プログラムをゼロから書くのは慣れが必要です。プログラムをゼロから書く場合、小さな部品を一つ一つ作っていって、最後にそれらを組み上げる「下から書く」方法と、「こういう関数が必要であるはず」と外枠から書いていって最後に中身を埋める「上から書く」方法があります。その一般論を論じるのは私の能力を超えるため、以下では「下から」と「上から」の例を挙げて、その「気持ち」を説明してみようと思います。言語はなんでも良いですが、ここではPythonを使います。

## 下から書く例「パーコレーション」

### Union-Find

正方格子が与えられたとします。その格子のボンドが確率$p$で通行可能(アクティブ)、確率$1-p$で通行不能(インアクティブ)である時、この系の上辺から下辺まで、通行可能なボンドだけをたどって到達できる確率$P(p)$を求めなさい、というのがパーコレーション問題です。これは森林火災や病気の伝染などのモデルになっています。

各格子点をノードと呼び、それらに通し番号をつけ、アクティブなボンドで接続されたノードは同じクラスターであるとします。この時、「友達の友達は友達」と定義し、ノードAとBが同じクラスター、BとCが同じクラスターなら、AとCも同じクラスターであると定義します。ノードの集合と、アクティブなボンドでつながったノードペアの集合が与えられた時、任意の2つのノードが同じクラスターに属すかどうかを調べる手段を提供するのがUnion-Findアルゴリズムです。

Union-Findアルゴリズムは、2つのノードをつなげるunion関数と、あるノードのクラスター番号を返すfind関数の2つからなります。いくつか実装がありますが、一番簡単な一次元配列を使う実装にしましょう。では、コードを書き始めます。

### `main`関数の作成

最初にやることは、以下のように`main`関数を作ることです。

```py
def main():
    pass


if __name__ == "__main__":
    main()
```

`if __name__ == `はPythonのイディオムで、このスクリプトを直接実行した時のみ実行されるようにするものです(他のスクリプトからimportされた時は実行されない)。ここから`main`関数を呼び、あとはそこに処理を追加していきます。このように`main`関数を作る意味はグローバル変数を使わないようにするためです。グローバル変数はあとでバグの温床になります。プログラムの起点を関数にしておき、必要な変数を関数内で定義しておくと、「必要な変数は引数として渡す」という癖がつきます。

この`if`の中にテストコードを書いてはいけません。Pythonのif文はスコープを作らないため、ここに書いた変数はグローバス変数になります。`main`でも`test`でもどんな名前でもかまいませんが、スタート地点は関数にしておく必要があります。

あとは、関数を追加しては、`main`関数にテストコードを書いて呼び出す、という手順を繰り返します。

### `find`関数の作成

最初に作るのは`find`関数です。自分の「親」をたどっていって、一番上に到達したらその番号を返す、というコードです。インデックス(`index`)と一次元配列(`cluter`)を受け取って、`while`を回すだけの簡単な関数です。こんな感じのコードになるでしょうか(わざと間違えています)。

```py
def find(index, cluster):
    while index != cluster[index]:
        index = cluster[index]
        return index
```

このコードを試してみましょう。テストコードを`main`に書きます。5つノードがあり、$i$番目のノードの親が$i-1$で、ノード番号$0$の親は自分自身、つまり、すべてのノードが同じクラスターに属している状態です。この状態で、それぞれのノードのクラスター番号を表示させます。

```py
def main():
    cluster = [0, 0, 1, 2, 3]
    for i in range(len(cluster)):
        print(i, find(i, cluster))
```

想定される出力は、すべてのクラスター番号が0と表示されるものです。しかし、実行してみるとこうなります。

```txt
0 None
1 0
2 1
3 2
4 3
```

想定出力と異なります。ここで`find`関数を見ると、`return`文のインデントを間違えていることに気づきます。直しましょう。

```py
def find(index, cluster):
    while index != cluster[index]:
        index = cluster[index]
    return index # ここのインデントがおかしかった。
```

もう一度実行します。

```txt
0 0
1 0
2 0
3 0
4 0
```

想定通りの出力になりました。まだコーナーケースのバグは残っているかもしれませんが、とりあえず`find`関数は完成です。こうやって、**一つ関数を書くたびに、必ず簡単なケースでテストします**。

### `union`関数の作成

次に`union`を作ります。2つのノードをつなぐのが目的です。それぞれのノード番号を受け取り、`find`を使ってクラスター番号を受け取って、小さい方のクラスター番号に揃えます。これも簡単な関数です。

```py
def union(index1, index2, cluster):
    c1 = find(index1, cluster)
    c2 = find(index2, cluster)
    if c1 < c2:
        cluster[c2] = c1
    else:
        cluster[c1] = c2
```

試してみましょう。5つノードがあり、1と2、3と4、最後に1と4をつなぎます。すると、0以外のノードがすべてクラスター番号1になるはずです。

```py
def main():
    N = 5
    cluster = [i for i in range(N)]
    union(1, 2, cluster)
    union(3, 4, cluster)
    union(1, 4, cluster)
    for i in range(N):
        print(i, find(i, cluster))
```

実行してみましょう。

```txt
0 0
1 1
2 1
3 1
4 1
```

想定通りの出力になりました。

### `show`関数の作成

これからのデバッグのため、すべてのノードのクラスター番号を表示する関数を作っておきます。乱数を使うようなコードは、特にデバッグに気を使わなくてはいけません。システムサイズを$L \times L$の正方形とすることにして、`cluster`配列を受け取って、その中身を表示する関数`show`を作っておきましょう。

```py
def show(L, cluster):
    for iy in range(L):
        for ix in range(L):
            index = ix + iy * L
            c = find(index, cluster)
            print(f"{c:02d} ", end="")
        print()
```

デバッグのため、とりあえずクラスター番号は2桁で止めておきます。

`cluster`を初期化しておいて、`show`を呼ぶテストを書きましょう。

```py
def main():
    L = 5
    N = L * L
    cluster = [i for i in range(N)]
    show(L, cluster)
```

実行してみます。

```txt
00 01 02 03 04 
05 06 07 08 09 
10 11 12 13 14 
15 16 17 18 19 
20 21 22 23 24 
```

まだどのノードも接続していないため、すべてのノードのクラスター番号が異なる状態です。

### `mc_onestep`関数の作成

次に、確率$p$でランダムにアクティブ/インアクティブなボンドを作って、ノードを接続していくコードを書きましょう。モンテカルロを1ステップだけ実行するため、`mc_onestep`という名前にしましょうか。これはサイズと確率$p$を受け取り、最終的に「上と下がつながったか」を0/1で返す関数です。

そのためには、座標を2つ受け取り、確率$p$でその座標のノードを接続する`connect`関数も必要です。これらは同時に作りましょう。

まず、`connect`関数はこんな感じになるでしょう。デバッグ用にどことどこをつないだか表示しておきます。

```py
def connect(p, x1, y1, x2, y2, L, cluster):
    i1 = x1 + y1 * L
    i2 = x2 + y2 * L
    if random.random() < p:
        union(i1, i2, cluster)
        print(f"Connect: {i1} {i2}")
```

`connect`を呼ぶ、`mc_onestep`関数はこうなるでしょう。

```py
def mc_onestep(p, L):
    L = 5
    N = L * L
    cluster = [i for i in range(N)]
    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix + 1, iy, L, cluster)  # (1)
    show(L, cluster)
```

本当は、`# (1)`の部分は`connect(p, ix, iy, ix, iy + 1, L, cluster)`と、y方向につなぐ必要がありますが、コピペして修正し忘れた、という想定で間違えています。また、最後にデバッグ用に`show`を呼んでいます。

また、ここには書いていませんが、コードの冒頭に`import random`を追加します。

これらをテストする`main`関数を書きます。まずは確率0.5でためしましょう。

```py
def main():
    random.seed(0)
    L = 5
    p = 0.5
    mc_onestep(p, L)
```

ここで`random.seed(0)`を指定していることに注意してください。**乱数を使うコードは、デバッグ時は必ずシードを固定します**。そうしないと「あれ？」と思った時に状況が再現できずに困るからです。デバッグの前提は、同じ状況で同じ結果が出ることです。そこが崩れるとデバッグが極めて困難になります。サーバ系や並列コードなど、非同期な処理のデバッグが難しいのは、全く同じ状況を再現することが難しいことによります。

さて、実行しましょう。

```txt
Connect: 5 6
Connect: 5 6
Connect: 10 11
Connect: 15 16
Connect: 1 2
Connect: 11 12
Connect: 16 17
Connect: 12 13
Connect: 3 4
Connect: 3 4
Connect: 8 9
Connect: 18 19
00 01 01 03 03 
05 05 07 08 08 
10 10 10 10 14 
15 15 15 18 18 
20 21 22 23 24 
```

必ず2回実行し、同じ結果が得られることを確認します。乱数系のコードは、例えば`numpy`や`tensorflow`は独自のシードを持っていたりするため、シードを固定しても結果が変わる場合があります。「毎回同じ結果になる」ことを確認してから次に進みます。

さて、このコードを見て「あっ、y方向の接続を忘れた」と気づくのは難しいでしょう。ですが、$p=1$を試すとどうでしょうか？

```py
def main():
    random.seed(0)
    L = 5
    p = 1.0
    mc_onestep(p, L)
```

すべてのボンドがアクティブなのだから、すべてのノードがつながっているはずです。実行してみましょう。

```txt
00 00 00 00 00 
05 05 05 05 05 
10 10 10 10 10 
15 15 15 15 15 
20 21 22 23 24
```

これを見ると、x方向だけが接続され、y方向の接続を忘れているのが一目瞭然です。修正しましょう。

```py
def mc_onestep(p, L):
    L = 5
    N = L * L
    cluster = [i for i in range(N)]
    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster) # ここを修正
    show(L, cluster)
```

改めて実行してみます。

```txt
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 24 
```

右下が接続されていません。これは、ループを`range(L-1)`で回したため、右端と下端の接続を忘れていたためです(すみません、これはわざとではなく素で忘れました)。

右端と下端の接続を追加し、それ以外の接続をなしにして、ちゃんと繋がるか確認しましょう。

まずは右端のみの確認です。

```py
def mc_onestep(p, L):
    L = 5
    N = L * L
    cluster = [i for i in range(N)]
    """
    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster)
    """

    for iy in range(L - 1):
        connect(p, L - 1, iy, L - 1, iy + 1, L, cluster)
    show(L, cluster)
```

実行します。

```txt
00 01 02 03 04 
05 06 07 08 04 
10 11 12 13 04 
15 16 17 18 04 
20 21 22 23 04 
```

右端が繋がりましたね。同様に下端も確認します。

```py
def mc_onestep(p, L):
    L = 5
    N = L * L
    cluster = [i for i in range(N)]
    """
    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster)

    for iy in range(L - 1):
        connect(p, L - 1, iy, L - 1, iy + 1, L, cluster)
    """

    for ix in range(L - 1):
        connect(p, ix, L - 1, ix + 1, L - 1, L, cluster)
    show(L, cluster)
```

```txt
00 01 02 03 04 
05 06 07 08 09 
10 11 12 13 14 
15 16 17 18 19 
20 20 20 20 20 
```

下端が繋がりました。改めて全部をつなげてみましょう。

```py
def mc_onestep(p, L):
    L = 5
    N = L * L
    cluster = [i for i in range(N)]

    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster)

    for iy in range(L - 1):
        connect(p, L - 1, iy, L - 1, iy + 1, L, cluster)

    for ix in range(L - 1):
        connect(p, ix, L - 1, ix + 1, L - 1, L, cluster)

    show(L, cluster)
```

実行します。

```txt
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 00
```

ちゃんと繋がりました。

適当な確率、例えば$p=0.5$あたりで確認します。

```txt
Connect: 5 6
Connect: 5 10
Connect: 10 15
Connect: 15 20
Connect: 1 2
Connect: 11 12
Connect: 16 21
Connect: 12 13
Connect: 3 4
Connect: 3 8
Connect: 8 9
Connect: 18 19
Connect: 4 9
Connect: 19 24
Connect: 21 22
00 01 01 03 03 
05 05 07 03 03 
05 11 11 11 14 
05 16 17 18 18 
05 16 16 23 18
```

ちゃんとノートに図を書いて、どことどこがつながったからこのクラスターになるはず、ということを確認しましょう。ここまで大丈夫そうなので次に行きます。

もう大丈夫そうなので`union`関数のデバッグ表示は消しておきましょう。

### `percolation_check`関数の作成

クラスタリングが終了したら、上辺と下辺がつながっていることを確認します。もっと効率的なコードはありますが、まずはナイーブ組みましょう。上辺と下辺のノードのクラスター番号が一致しているかどうか調べ、一致していたら`True`を、そうでなければ`False`を返す関数です。こんな感じになるでしょうか。

```py
def percolation_check(L, cluster):
    for ix1 in range(L):
        c1 = find(ix1, cluster)
        for ix2 in range(L):
            c2 = find(ix2 + (L - 1) * L, cluster)
            if c1 == c2:
                return True
    return False
```

これを`mc_onestep`から呼び出します。

```py
def mc_onestep(p, L):
    N = L * L
    cluster = [i for i in range(N)]

    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster)

    for iy in range(L - 1):
        connect(p, L - 1, iy, L - 1, iy + 1, L, cluster)

    for ix in range(L - 1):
        connect(p, ix, L - 1, ix + 1, L - 1, L, cluster)

    show(L, cluster)
    if percolation_check(L, cluster):
        print("Percolated")
    else:
        print("Not Percolated")
```

`main`関数から10回ほど実行してみましょう。

```py
def main():
    random.seed(0)
    L = 5
    p = 0.5
    for _ in range(10):
        mc_onestep(p, L)
```

実行してみます。

```txt
00 01 01 03 03 
05 05 07 03 03 
05 11 11 11 14 
05 16 17 18 18 
05 16 16 23 18 
Not Percolated

00 00 00 00 04 
00 00 07 00 09 
00 00 00 00 00 
00 00 17 00 00 
20 21 22 00 00 
Percolated

00 01 02 03 03 
05 06 02 03 03 
05 02 02 03 14 
05 16 03 03 03 
20 21 21 23 24 
Not Percolated

00 00 00 00 00 
00 00 00 00 00 
00 00 00 00 14 
00 00 00 00 19 
00 00 19 19 19 
Percolated

00 00 02 02 02 
00 00 02 02 02 
00 00 00 02 02 
00 00 00 02 02 
00 00 00 02 02 
Percolated

00 00 00 03 04 
00 00 00 03 04 
10 10 12 12 12 
15 12 12 12 12 
12 12 12 12 12 
Not Percolated

00 01 01 03 03 
01 01 07 08 08 
10 11 12 08 08 
10 10 17 17 08 
10 10 10 17 17 
Not Percolated

00 00 00 03 04 
00 00 00 00 00 
00 00 12 00 00 
00 00 00 00 00 
00 00 00 00 24 
Percolated

00 00 00 00 00 
00 00 00 00 09 
00 00 00 00 09 
15 00 17 00 00 
00 00 17 00 00 
Percolated

00 00 00 00 04 
00 00 00 00 09 
10 00 00 13 14 
15 00 00 18 19 
20 21 21 18 19 
Not Percolated
```

上から下までつながっている時に`Percolated`、そうで無いときに`Not Percolated`と表示されていますね。

### `mc_average`関数の作成

次に`mc_onestep`を何度も呼んで、パーコレーション確率を計算する関数`mc_average`を書きましょう。サンプル回数を受け取り、その回数だけ`mc_onestep`を呼び出して、平均を返すだけです。

まず、`mc_onestep`関数を、パーコレートしていたら1.0を、そうでなければ0.0を返すように修正します。デバッグ情報の`show`も削除しておきます。

```py
def mc_onestep(p, L):
    N = L * L
    cluster = [i for i in range(N)]

    for ix in range(L - 1):
        for iy in range(L - 1):
            connect(p, ix, iy, ix + 1, iy, L, cluster)
            connect(p, ix, iy, ix, iy + 1, L, cluster)

    for iy in range(L - 1):
        connect(p, L - 1, iy, L - 1, iy + 1, L, cluster)

    for ix in range(L - 1):
        connect(p, ix, L - 1, ix + 1, L - 1, L, cluster)

    if percolation_check(L, cluster):
        return 1.0
    else:
        return 0.0
```

`mc_average`は、確率`p`、サンプル数`num_samples`、システムサイズ`L`を受け取り、その確率$p$でのパーコレーション確率を返す関数です。

```py
def mc_average(p, num_samples, L):
    sum = 0.0
    for _ in range(num_samples):
        sum += mc_onestep(p, L)
    sum /= num_samples
    return sum
```

このあたりは難しくないので、ミスも少ないでしょう。

`main`関数から呼び出します。

```py
def main():
    random.seed(0)
    L = 5
    p = 0.5
    num_samples = 100
    print(mc_average(p, num_samples, L))
```

実行しましょう。

```txt
0.58
```

この時、`p=0`のときに0になることと、`p=1`の時に1.0になることを必ず確認する癖をつけておきましょう。乱数を使ったコードのデバッグは大変ですが、パラメータの極限では厳密に値がわかっていることが多いです。例えばスピン系のモンテカルロ法なら、高温極限と低温極限は必ず確認する癖をつけるようにします。

### `mc_all`関数の作成

最後に、様々な$p$の値でパーコレーション確率$P$を求める関数`mc_all`を作ります。受け取る引数はシステムサイズとサンプル数で良いでしょう。

```py
def mc_all(L, num_samples):
    ND = 20
    for i in range(ND + 1):
        p = i / ND
        print(f"{p} {mc_average(p, num_samples,L)}")
```

確率$p$を何点とるかは、とりあえずこの関数のローカル変数`ND`としていますが、あとで必要になったら引数で渡すように修正しましょう。

`main`から呼び出します。

```py
def main():
    random.seed(0)
    L = 5
    num_samples = 100
    mc_all(L, num_samples)
```

実行しましょう。

```txt
0.0 0.0
0.05 0.0
0.1 0.0
0.15 0.0
0.2 0.01
0.25 0.06
0.3 0.1
0.35 0.22
0.4 0.34
0.45 0.38
0.5 0.61
0.55 0.82
0.6 0.84
0.65 0.92
0.7 0.93
0.75 0.99
0.8 1.0
0.85 1.0
0.9 1.0
0.95 1.0
1.0 1.0
```

できてそうですね。サイズとサンプル数を増やして、プロットしてみましょう。`L=16`の例です。

![L=16](/images/programming_howto/L16.png)

相転移していそうです。

最後に、結果を標準出力に吐くのではなく、システムサイズによってファイル名を決め、そこに出力するように修正しておきましょう。また、実行時引数としてサイズを受け取るように修正します。なお、コードの冒頭に`import sys`が必要です。

```py
def mc_all(L, num_samples):
    ND = 20
    filename = f"L{L:02d}.dat"
    print(filename)
    with open(filename, "w") as f:
        for i in range(ND + 1):
            p = i / ND
            f.write(f"{p} {mc_average(p, num_samples,L)}\n")


def main():
    random.seed(0)
    if len(sys.argv) != 2:
        print("usage: python3 percolation.py systemsize")
        return
    L = int(sys.argv[1])
    num_samples = 1000
    mc_all(L, num_samples)
```

実行してみましょう。

```txt
$ python3 percolation.py
usage: python3 percolation.py systemsize

$ python3 percolation.py 8
L08.dat

$ python3 percolation.py 16
L16.dat

$ python3 percolation.py 32
L32.dat
```

プロットするとこんな感じです。

![L=16](/images/programming_howto/finite_size.png)

サイズが大きくなるにつれて、パーコレーション確率の変化が急峻になっていることがわかります。これが有限サイズ効果です。

あとはシステムサイズやサンプル数、何点観測するかを、例えばYAMLやTOMLから指定できるようにすると良いでしょう。

## 上から書く例「LAMMPSの出力解析」


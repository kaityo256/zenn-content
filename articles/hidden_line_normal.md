---
title: "隠線処理の話"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [Python, 数学, math]
published: true
---

## 概要

分子動力学シミュレーションの結果を可視化する際に、隠線処理をする必要がありました。隠線処理とは、こんな感じに3次元の立体を2次元に描画するときに線が隠れるようにする処理のことです。

![rotate.gif](/images/hidden_line_normal/rotate.gif)

本稿では、この隠線処理のうち、法線ベクトル法の説明をします。Pythonによるサンプルコードは以下にあります。そのままGoogle Colabで試すことができるサンプルもあります。

[https://github.com/kaityo256/hidden-line](https://github.com/kaityo256/hidden-line)

また、この隠線処理を実装したシミュレーション可視化コードは以下にあります。

[https://github.com/kaityo256/trj-render](https://github.com/kaityo256/trj-render)

## はじめに

3次元の物体を2次元に射影することを考えます。例えば立方体を描画するとこんな感じになります。

![fig1](/images/hidden_line_normal/fig1.png)

ここでは立方体の辺が針金でできているかのように全て見えていますが、もしこの物体の中身が詰まっていて不透明なら以下のように見えるでしょう。

![fig2](/images/hidden_line_normal/fig2.png)

先ほどの場合と比較して、三本の線が消えました。このように「こういう状況ならこの視点からは見えないはず」という条件を計算し、見えない部分を描かないようにするのが隠線処理です。

隠線処理にはいろいろなアルゴリズムがあります。簡単なのは、奥から面を描画していき、上書きしていく方法です。これを塗り重ね法と呼びます。この方法は簡単ですが、この立方体の内部にさらに物体があったりする場合に対応できません。

今回、分子動力学シミュレーションの実行結果の可視化に使いたい、というニーズがあり、「空間にあるワイヤーフレーム状の直方体の中に多数の球がある」という状態を描画する必要がありました。例えば、立方体の中に一つだけ大きな球があるとこんな感じになります。

![fig3](/images/hidden_line_normal/fig3.png)

このような描画を行うためには、

1. 球の後ろにある線を描画する
  ![fig4a](/images/hidden_line_normal/fig4a.png)
2. その上に球を描画する
  ![fig4b](/images/hidden_line_normal/fig4b.png)
3. さらにその上に残りの線を描画する
  ![fig3](/images/hidden_line_normal/fig3.png)

みたいなことをする必要があります。要するに、空間に浮いている立方体(直方体)の辺のうち、視線から見て後ろ側にあるか、前側にあるかを判定する必要があるということです。

このように、与えられた立体の辺のうち、どの辺が「向こう側」にあり、どの辺が「こちら側」にあるかを判定するアルゴリズムが法線ベクトル法です。法線ベクトル法は、凸多面体にしか使えませんが、アルゴリズムが単純なので、今回はこれを採用しました。

## 法線ベクトル法の原理

簡単のために2次元で考えましょう。いま、左から右を見ていて、その方向に正方形があるとします(長方形でも話は同じです)。

![normal1](/images/hidden_line_normal/normal1.png)

もし立方体が不透明なら、ユーザから青い点は見えますが、赤い点は見えません。なので、青い点が「こちら側」、赤い点が「向こう側」です。このように、点がどちら側に属すのかを判定しましょう、というのが法線ベクトル法です。そのために、まず辺がどちら側にあるかを考えます。

![normal2](/images/hidden_line_normal/normal2.png)

もし立方体が不透明である時、ユーザから見える辺を青、見えない辺を赤で塗ったのが上の図です。これを見ると、点につながる辺が2つとも見えない場合にのみ、その点が見えず、それ以外の点は見える、ということがわかります。したがって、辺が「こちら側」を向いているか、「向こう側」を向いているかを判定すれば良いことになります。

![normal3](/images/hidden_line_normal/normal3.png)

そのためには、各辺に物体の中心から遠ざかる向きの法線ベクトルを考え、視線ベクトルと同じ向きであるかどうか判定すればよいことになります。つまり、各辺の法線ベクトルと視線ベクトルの内積をとり、内積が負なら逆向き、すなわちその面は「こちら向き」であり、内積が正ならその面は「向こう向き」であることになります。

以上の理屈は3次元であっても全く同じです。いま、複数の面からなる凸多面体がある時、以下のようにして辺がこちら側にあるか、奥側にあるかを判定できます。

1. 各面の法線ベクトル(方向を多面体から外側にとります)について、視線ベクトルと内積をとり、その正負によって、面が「こちら向き」であるか「向こう向き」であるかを判定します。
2. 各辺について、その辺に接する面の向きを調べます。もし2つの面ともに「向こう向き」であれば、線は見えません。それ以外は見えると判定できます。

## 具体的な実装

### 頂点、面、線のインデックス

さて、法線ベクトル法のコンセプトは簡単なのですが、実装はわりと面倒です。もともとの目的が分子動力学シミュレーションの可視化なので、以後、描画する直方体のことをシミュレーションボックスと呼びます。

最初に、シミュレーションボックスをx, y, z軸にそろえておきます。すなわち、$x_\mathrm{min} < x < x_\mathrm{max}, y_\mathrm{min} < y < y_\mathrm{max},z_\mathrm{min} < z < z_\mathrm{max}$を満たすような領域をシミュレーションボックスと定義します。

この世界を、3次元回転行列$R$によって回転させた結果、どの辺が見えなくなるかを判定するコードを考えます。そのために、まずはシミュレーションボックスを構成する頂点、面、辺に番号をつけましょう。

まずは頂点に番号をつけます。頂点は8個ありますが、以下のように2進数的なノリで番号付けすると良いでしょう。

![index1.png](/images/hidden_line_normal/index1.png)

| 頂点番号 | 座標 |
| ---- | ---- |
| 0 | $(x_\mathrm{min}, y_\mathrm{min}, z_\mathrm{min})$ |
| 1 | $(x_\mathrm{max}, y_\mathrm{min}, z_\mathrm{min})$ |
| 2 | $(x_\mathrm{min}, y_\mathrm{max}, z_\mathrm{min})$ |
| 3 | $(x_\mathrm{max}, y_\mathrm{max}, z_\mathrm{min})$ |
| 4 | $(x_\mathrm{min}, y_\mathrm{min}, z_\mathrm{max})$ |
| 5 | $(x_\mathrm{max}, y_\mathrm{min}, z_\mathrm{max})$ |
| 6 | $(x_\mathrm{min}, y_\mathrm{max}, z_\mathrm{max})$ |
| 7 | $(x_\mathrm{max}, y_\mathrm{min}, z_\mathrm{max})$ |

次に、面に番号をつけましょう。まず、$x = x_\mathrm{min}$であるような面を0として、対面する面はインデックスが3だけずれるようにしましょう。また、それぞれの法線ベクトルもまとめておきます。

![index2.png](/images/hidden_line_normal/index2.png)

| 面番号 | 座標 | 法線ベクトル |
| ---- | ---- | ---- |
| 0 | $x = x_\mathrm{min}$| $(-1, 0, 0)$ |
| 1 | $y = y_\mathrm{min}$| $(0, -1, 0)$ |
| 2 | $z = z_\mathrm{min}$| $(0, 0, -1)$ |
| 3 | $x = x_\mathrm{max}$| $(1, 0, 0)$ |
| 4 | $y = y_\mathrm{max}$| $(0, 1, 0)$ |
| 5 | $z = z_\mathrm{max}$| $(0, 0, 1)$ |

最後に、辺に番号をつけます。先ほど定義した点を2つ組み合わせることで辺を表現しましょう。例えば、辺番号0番は$(x_\mathrm{min}, y_\mathrm{min}, z_\mathrm{min})$から$(x_\mathrm{max}, y_\mathrm{min}, z_\mathrm{min})$までの線分とします。これは0番の点と1番の点なので$(0, 1)$と表現します。また、重要なのはこれらの辺がどの面と接しているかです。例えば、辺番号0番は、面番号1と2に接しています。以上の情報を表にまとめましょう。


| 辺番号 | 点の組み合わせ |  接する面 |
| ---- | ---- | ---- | 
| 0    | $(0, 1)$ | $(1, 2)$ |
| 1    | $(2, 3)$ | $(2, 4)$ |
| 2    | $(4, 5)$ | $(1, 5)$ |
| 3    | $(6, 7)$ | $(4, 5)$ |
| 4    | $(0, 2)$ | $(0, 2)$ |
| 5    | $(1, 3)$ | $(2, 3)$ |
| 6    | $(4, 6)$ | $(0, 5)$ |
| 7    | $(5, 7)$ | $(3, 5)$ |
| 8    | $(0, 4)$ | $(0, 1)$ |
| 9    | $(1, 5)$ | $(1, 3)$ |
| 10   | $(2, 6)$ | $(0, 4)$ |
| 11   | $(3, 7)$ | $(3, 4)$ |

### 回転行列と内積

もともとx, y, z軸に平行だったシミュレーションボックスを、3行3列の回転行列$R$で回転させ、それを$x$軸正の方向から負の方向に向かう視点で描画することにしましょう。3次元ライブラリでは奥行きを表現するため、奥になるほどスケールが小さくする場合もありますが、今回はそのような変換はしないことにします。

行列はNumPy配列として定義しておきましょう。

```py
R = np.eye(3)
```

この行列をx,y,z軸にたいして回転させる関数は以下のようにかけます。ただし、回転角の単位はラジアンではなく度にしています。

```py
def rotateX(R, s):
    rad = np.deg2rad(s)
    Rx = np.array(
        [[1, 0, 0], [0, np.cos(rad), -np.sin(rad)], [0, np.sin(rad), np.cos(rad)]]
    )
    return R @ Rx


def rotateY(R, s):
    rad = np.deg2rad(s)
    Ry = np.array(
        [[np.cos(rad), 0, np.sin(rad)], [0, 1, 0], [-np.sin(rad), 0, np.cos(rad)]]
    )
    return R @ Ry


def rotateZ(R, s):
    rad = np.deg2rad(s)
    Rz = np.array(
        [[np.cos(rad), -np.sin(rad), 0], [np.sin(rad), np.cos(rad), 0], [0, 0, 1]]
    )
    return R @ Rz
```

法線ベクトル$\vec{n}$は、この行列で$R\vec{n}$と変換されます。このベクトルと視線ベクトル$\vec{v}$の内積$(\vec{v}, R\vec{n})$を計算し、その正負により向きが判定できます。

いま、$x$軸正の方向から負の方向に向かう視点を採用したため、視線ベクトルは$\vec{v}= (-1,0,0)$と表現できます(縦ベクトルと横ベクトルを同一視しています)。すなわち、$(\vec{v}, R\vec{n})$は、$R\vec{n}$の$x$成分に負符号をつけたものになります。

以上から、6つの面が視線と同じ向き(True)か、逆向き(False)かであるかのリスト`is_face_front[6]`は以下のように書けます。

```py
    is_face_front = [True] * 6
    is_face_front[0] = bool((R @ [1, 0, 0])[0] < 0)
    is_face_front[3] = not is_face_front[0]
    is_face_front[1] = bool((R @ [0, 1, 0])[0] < 0)
    is_face_front[4] = not is_face_front[1]
    is_face_front[2] = bool((R @ [0, 0, 1])[0] < 0)
    is_face_front[5] = not is_face_front[2]
```

面番号0番の法線ベクトルは$(-1,0,0)$なので、$R$で内積をとってから視線ベクトル$(-1,0,0)$との内積が正であるかどうかを判定することになりますが、両辺に-1をかけて、$(1,0,0)$を$R$で回転させて内積が負であるかどうかにしています。

また、0番と3番、1番と4番、2番と5番は法線ベクトルが逆向きなので、否定をとっています。

面の法線ベクトルが視線と逆向き(見える)か、同じ向き(見えない)かのリストができたら、それぞれの辺の可視性は接する2つの面の可視性の論理和により決定できます。

```py
is_edge_visible[0] = is_face_front[1] or is_face_front[2]
is_edge_visible[1] = is_face_front[2] or is_face_front[4]
is_edge_visible[2] = is_face_front[1] or is_face_front[5]
is_edge_visible[3] = is_face_front[4] or is_face_front[5]
is_edge_visible[4] = is_face_front[0] or is_face_front[2]
is_edge_visible[5] = is_face_front[2] or is_face_front[3]
is_edge_visible[6] = is_face_front[0] or is_face_front[5]
is_edge_visible[7] = is_face_front[3] or is_face_front[5]
is_edge_visible[8] = is_face_front[0] or is_face_front[1]
is_edge_visible[9] = is_face_front[1] or is_face_front[3]
is_edge_visible[10] = is_face_front[0] or is_face_front[4]
is_edge_visible[11] = is_face_front[3] or is_face_front[4]
```

これにより、`is_edge_visible[i]`の真偽により、視線の奥側にあるか、手前側にあるかを判定できるようになりました。

### 描画

以上の準備のもと、辺を描画する関数は以下のように書けます。

```py
def draw_edges(draw, points, edges, R, sy, sz, draw_front):
    scale = 150

    is_edge_visible = get_visible(R)

    def project(v):
        v = np.asarray(v, dtype=float)
        Vr = R @ v
        y, z = Vr[1], Vr[2]
        return (scale * y + sy, scale * z + sz)

    for i, e in enumerate(edges):
        if is_edge_visible[i] ^ draw_front:
            continue
        p1 = project(points[e[0]])
        p2 = project(points[e[1]])
        draw.line([p1, p2], fill="black", width=2)
```

`project`は、ベクトルを受け取り、回転行列を適用させたあと、適切にスケール変換、原点位置の移動を行う(要するにアフィン変換をする)関数です。最終的に2次元のCanvasに描画するので、いい感じに見えるように拡大縮小移動をします。NumPy配列なら行列ベクトル積が`@`で書けるので便利ですね。

`draw_front`は`True`なら手前側、`False`なら奥側を描画するフラグです。これにより、手前側の辺だけを描画する`draw_front_edges`と、奥側のみ描画する`draw_back_edges`は以下のように書けます。

```py
def draw_front_edges(draw, points, edges, R, sy, sz):
    draw_edges(draw, points, edges, R, sy, sz, True)


def draw_back_edges(draw, points, edges, R, sy, sz):
    draw_edges(draw, points, edges, R, sy, sz, False)
```

最後のTrueとFalseを入れ替えるだけです。

これらを使って、立方体の中に大きな球があるような状態を描画する関数は以下のように書けます。

```py
def draw(R, width, height, points, edges):
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw_back_edges(draw, points, edges, R, width // 2, height // 2)
    cx, cy = width / 2, height / 2
    r = 150
    bbox = (cx - r, cy - r, cx + r, cy + r)
    draw.ellipse(bbox, fill="red", width=3)
    draw_front_edges(draw, points, edges, R, width // 2, height // 2)
    return img
```

回転行列とイメージの幅、高さ、そして頂点の座標`point`と、その組み合わせである辺`edges`を受け取り、以下の順番で描画します。

1. 最初に奥側の辺を描画し(`draw_back_edges`)
  ![fig4a](/images/hidden_line_normal/fig4a.png)
2. その上に球を描画し(`draw.ellipse`)
  ![fig4b](/images/hidden_line_normal/fig4b.png)
3. 最後に手前の線を描画すれば完成(`draw_front_edges`)
  ![fig3](/images/hidden_line_normal/fig3.png)

分子動力学シミュレーションの結果の可視化も全く同様にできます。

## まとめ

3次元空間上に直方体のシミュレーションボックスがあり、その中に球が多数あるような系について、直方体をワイヤーフレームとして表現し、球を円として射影して描画するコードを書いてみました。そのためには視線から隠れているべき線についてちゃんと描画する、隠線処理を行う必要があります。本稿では、単純な隠線処理アルゴリズムである法線ベクトル法を紹介しました。このアルゴリズムは単純ではありますが、一次変換とか内積とか出てくるので、ちょっと紙と鉛筆をつかって計算しないと「アレ」と混乱しがちです(っていうか混乱しました)。

高校生の頃、友人とワイヤーフレームで表現された3Dのダンジョンゲームを作りました。ハードはPC-98、OSはMS-DOSです。言語はQuick C+アセンブリだったかな。当然3Dグラフィックライブラリなんてありませんから、隠線処理は自前で書く必要があります。友人はスラスラ書いていましたが、自分にはそのアルゴリズムは全く理解できませんでした。今回、機会があって自分で書いてみたのですが、高校生が書くにはまぁまぁハードルが高かったのでは、と思います。改めて考えると当時の友人はすごかったな。

こういう隠線処理みたいなグラフィックの基礎的なアルゴリズムは、昔はベーシックマガジンのような雑誌でよく特集された記憶がありますが、現在はほぼ3Dグラフィックライブラリを使うため、直接アルゴリズムについて学ぶ人は減った気がします。そういう意味で法線ベクトル法も「古(いにしえ)の技術」となりつつある気がします。令和の時代にもなって「法線ベクトル法を学びたい」という誰かにこの記事が届くことを祈っています。

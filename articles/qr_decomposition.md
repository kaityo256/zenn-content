---
title: "QRコードをQR分解する"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Python","数学"]
published: true
---

## 概要

QRコードをQR分解します。

## QRコードをQR分解する

QRコードを良く目にすると思います。例えばこんなのです。

![QR](https://github.com/kaityo256/zenn-content/blob/main/articles/qr_decomposition/qrcode.png?raw=true)

これを見ると、まるで疎行列のように見えてきますね。なので、これを行列だと思ってQR分解したくなりますね。

QR分解とは、正方行列$A$を、直交行列$Q$と上三角行列$R$の積、

$$
A = QR
$$

と分解することです。なぜQR分解が必要かはその辺にいるガチ勢に聞いてください。ではさっそくQRコードをQR分解してみましょう。以下、Google Colabで実行することを想定していますが、何を使ってもかまいません。

まずはQRコードを作るのに必要な`qrcode`をインストールしておきましょう。

```sh
!pip install qrcode
```

必要なライブラリをimportしましょう。

```py
import qrcode
import numpy as np
import scipy.linalg as linalg
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
```

では早速QRコードを作ります。

```py
BOX_SIZE = 10
qr = qrcode.QRCode(box_size=BOX_SIZE,border=0)
qr.add_data('Hello QR Code')
qr.make()
img = qr.make_image()
img
```

いきなり`qrcode.make("Hello QR Code")`としてQRコードを作ることもできますが、そうするとまわりに「枠」ができてしまうので、それを消すために`QRCode`クラスのコンストラクタで`boder=0`を指定しています。

ここから行列$A$を作りましょう。要素を見て、`BOX_SIZE`倍縮小するだけです。

```py
LX, LY = img.size
data = np.array(img.getdata()).reshape(LX, LY)
X, Y = LX//BOX_SIZE, LY//BOX_SIZE
A = np.zeros((X, Y))
for ix in range(X):
  for iy in range(Y):
    A[ix][iy] = 255-data[ix*BOX_SIZE][iy*BOX_SIZE]
```

あとで使うので、行列を可視化する関数を作っておきましょう。

```py
def get_image(M):
  M = np.abs(M)
  M = M/np.max(M)
  im = Image.new("L",(LX,LY), "white")
  draw = ImageDraw.Draw(im)
  for ix in range(X):
    for iy in range(Y):
      c = 255-int(M[iy][ix]*255)
      sx = ix*BOX_SIZE
      sy = iy*BOX_SIZE
      draw.rectangle((sx, sy, sx+BOX_SIZE, sy+BOX_SIZE), fill=c)
  return im
```

これで先ほどの行列$A$を可視化してみます。

```py
get_image(A)
```

![A](https://github.com/kaityo256/zenn-content/blob/main/articles/qr_decomposition/A.png?raw=true)

できてるっぽいですね。

次に、$A$をQR分解します。`linalg.qr`を呼ぶだけです。

```py
Q, R = linalg.qr(A)
```

それぞれ可視化してみましょう。

```py
get_image(Q)
```

![Q](https://github.com/kaityo256/zenn-content/blob/main/articles/qr_decomposition/Q.png?raw=true)

これが直交行列のはずですが、パッと見ではわかりませんね。

```py
get_image(R)
```

![R](https://github.com/kaityo256/zenn-content/blob/main/articles/qr_decomposition/R.png?raw=true)

こちらは上三角行列だということがわかりやすいですね。

さて、$A=QR$なので、$Q$と$R$をかけたら元に戻るはずです。確認してみましょう。

```py
get_image(Q @ R)
```

![QR](https://github.com/kaityo256/zenn-content/blob/main/articles/qr_decomposition/QR.png?raw=true)

ちゃんと元に戻りました。

## まとめ

QRコードを行列だと思ってQR分解してみました。本稿がQRコードをQR分解したい人の参考になれば幸いです。

## 関連記事

* [大名行列を特異値分解してみる
](https://qiita.com/kaityo256/items/78b16c58228e131f8144)
* [大名行列をTucker分解してみる](https://qiita.com/kaityo256/items/2e3f45377a6b9760f3e0)
* [大名行列をHOOIでTucker分解してみる](https://qiita.com/kaityo256/items/ab9555ada7b07a65bc12)
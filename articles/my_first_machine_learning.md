---
title: "はじめての機械学習(自分でデータセットを作る編)"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

## はじめに

機械学習をやってみたくて、とりあえずサンプルを実行して、何かできているっぽいけれど、その後どうして良いかわからない、そんな人は多いと思います。
この記事では、全くの機械学習初心者向けに、自分でデータセットを作ってニューラルネットワークに学習させてみるサンプルを作ってみます。

## MNISTの学習

機械学習のデータセットといえば、MNISTです。これは手書き数字のデータセットで、0から9までの手書き数字データと、その正解ラベルがセットになっています。多くの機械学習フレームワークで、MNISTは標準でサポートされています。

TensorFlowを実行するために、まずはTensorFlowをインストールする必要があります。Google Colabとかで実行するのが楽ですが、もしローカルで実行したい場合は、今後のために仮想環境を作っておくと良いでしょう。適当なディレクトリ(例えば`my_first_ml`)を作って、そこで作業しましょう。

```sh
mkdir my_first_ml
cd my_first_ml
```

次に、仮想環境を作ります。Pythonは様々なパッケージをインストールして使いますが、それらのパッケージがぶつかったり、バージョンが異なるとふるまいが変わったりして不便です。これをコンピュータ全体で管理すると、別のプロジェクトでインストールしたパッケージが別のプロジェクトとぶつかって、いつのまにか動かなくなっていた、なんてことがおきたりします。それを防ぐために、プロジェクトごとにパッケージを管理します。そのために使うのが仮想環境です。

```sh
python3 -m venv myenv
source myenv/bin/activate
```

これにより、仮想環境`myenv`がアクティベートされました。以後、インストールされるパッケージは、`my_first_ml/myenv`以下に入ります。

```sh
python3 -m pip install --upgrade pip
python3 -m pip install tensorflow
```

TensorFlowがインストールされたかどうか確認しましょう。IPythonを使うのが良いと思います。

```sh
$ ipython3
In [1]: import tensorflow as tf
In [2]: tf.__version__
Out[2]: '2.10.0'
In [3]: exit 
```

`tf.__version__`を評価して、バージョンが帰ってきたら正しくインストールされています。`exit`でIPythonを抜けておきましょう。

これでTensorFlowを使う準備が整いました。実際に機械学習をしてみましょう。

TensorFlow/Kerasでニューラルネットワークを組んでMNISTを学習させるサンプルはこんな感じになります。

```py
import numpy as np
import tensorflow as tf
from tensorflow import keras


def get_data():
    train_data, test_data = keras.datasets.mnist.load_data()
    train_images, train_labels = train_data
    test_images, test_labels = test_data
    train_images = train_images / 255.0
    test_images = test_images / 255.0
    return(train_images, train_labels, test_images, test_labels)


def create_model():
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


(train_images, train_labels, test_images, test_labels) = get_data()

model = create_model()

model.fit(train_images, train_labels, epochs=5)

test_loss, test_acc = model.evaluate(test_images, test_labels)

print(f"Test Loss = {test_loss}")
print(f"Test Accuracy = {test_acc}")
```

たったこれだけです。これを`mnist.py`という名前で保存し、実行しましょう。

```sh
$ python3 mnist.py
(snip)
Epoch 1/5
1875/1875 [==============================] - 4s 2ms/step - loss: 0.2640 - accuracy: 0.9252
Epoch 2/5
1875/1875 [==============================] - 4s 2ms/step - loss: 0.1173 - accuracy: 0.9649
Epoch 3/5
1875/1875 [==============================] - 4s 2ms/step - loss: 0.0807 - accuracy: 0.9762
Epoch 4/5
1875/1875 [==============================] - 4s 2ms/step - loss: 0.0597 - accuracy: 0.9816
Epoch 5/5
1875/1875 [==============================] - 5s 2ms/step - loss: 0.0467 - accuracy: 0.9852
313/313 [==============================] - 1s 2ms/step - loss: 0.0815 - accuracy: 0.9746
Test Loss = 0.08145684003829956
Test Accuracy = 0.9746000170707703
```

最初にごちゃごちゃ表示されるのはTensorFlowをインポートした時のメッセージなので、とりあえず無視してかまいません。今回はエポックを5にしたので、5回分学習し、徐々に精度が上がっていること、最後にテストデータに対して精度を確認し、ロスが0.081、精度が97.4%であったことが表示されています。

## コードの説明

さて、わずか数十行書いたら機械学習ができる時代になりましたが、その分、実装が隠蔽されており、何が起きているかわかりにくくなっています。先ほどのコードが何をしているか、調べてみましょう。

```py
import numpy as np
import tensorflow as tf
from tensorflow import keras
```

最初の方はライブラリのインポートです。`as`はインポートしたパッケージに別名をつける命令で、慣習として`numpy`は`np`、`tensorflow`は`tf`と略します。今後、`tensorflow.hogehoge`と書くかわりに`tf.hogehoge`と書けるようになります。

```py
def get_data():
    train_data, test_data = keras.datasets.mnist.load_data()
    train_images, train_labels = train_data
    test_images, test_labels = test_data
    train_images = train_images / 255.0
    test_images = test_images / 255.0
    return(train_images, train_labels, test_images, test_labels)
```

これは、MNISTのデータを取得する関数です。`keras`には標準でいくつかのデータセットが付属しており、`keras.datasets.hogehoge.load_data()`でデータを持ってこれます。MNISTの場合は、`keras.datasets.mnist.load_data()`とすると、訓練データとテストデータがタプルで渡されるので、それをタプルで受け取ります。

受け取った訓練データ、テストデータは、それぞれイメージデータと正解ラベルのタプルになっています。なので、それらをタプルとして分離します。

```py
train_images, train_labels = train_data
test_images, test_labels = test_data
```

`train_images`や`test_images`は、NumPy配列になっています。例えば`train_images[0]`とすると、最初のデータを受け取れます。このデータは28x28のNumPy配列になっており、文字の「輝度」が0から255の整数で格納されています。

TODO:図解

後の学習のため、これを0か1の実数に正規化しておきます。それが以下の行です。

```sh
train_images = train_images / 255.0
test_images = test_images / 255.0
```

正解ラベルは、NumPyの一次元配列で、たとえば`train_labels[0]`には「5」が格納されており、0番目のイメージデータの正解ラベルが5であることがわかります。

あとは、正規化した訓練データ、そのラベル、テストデータ、そのラベルを4つのタプルとして返しています。

次にモデルの構築です。

```sh
def create_model():
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model
```

この関数では、28x28の入力を受け取り、10種類に分類するニューラルネットワークを組んでいます。最初の

```py
keras.layers.Flatten(input_shape=(28, 28)),
```

が入力層です。28x28のデータを受け取るよ、と書いてあります。

次の行が中間層の定義です。

```py
keras.layers.Dense(128, activation='relu'),
```

128個のニューロンからなる中間層で、活性化関数としてReLUを使うよ、と書いてあります。

最後が出力層です。

```py
keras.layers.Dense(10, activation='softmax')
```

10個のニューロンからなる出力層を作るよ、と書いてあります。これにより、入力層と中間層、中間層と出力層がそれぞれ全結合した三層のニューラルネットワークができます。

最後の行がモデルの構築です。

```py
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
```

最適化手法はAdam、ロス(目的関数)はクロスエントロピー、途中経過で`accuracy`を表示するように指定しています。分類問題を扱うなら、慣れるまではここは変えなくてよいと思います。

最後に作ったモデルを返しています。

さて、データを作る関数と、モデルを作る関数を作ったので、それらを使って学習しましょう。データとモデルを用意して、`fit`という関数に訓練データを食わせるだけです。

```py
(train_images, train_labels, test_images, test_labels) = get_data()
model = create_model()
model.fit(train_images, train_labels, epochs=5)
```

`model.fit`の第一引数に訓練データ、第二引数に正解ラベル、最後にエポック数を指定しています。他にもいろいろ指定できますが、まずはエポックだけいじるのが良いと思います。

これで、`train_images`を受け取り、その正解ラベルである`train_labels`に対応するニューロンの重みが一番大きくなるように学習が進みます。

学習が済んだら、「学習に使っていないデータ」を使ってモデルの検証を行いましょう。先程わけておいたテストデータを使います。

```py
test_loss, test_acc = model.evaluate(test_images, test_labels)
print(f"Test Loss = {test_loss}")
print(f"Test Accuracy = {test_acc}")
```

`model.evaluate`の第一引数のテストデータ、第二引数に正解ラベルを渡すと、このテストデータのうち、何個正解できたかを返してくれます。また、ロスとしてクロスエントロピーも計算してくれます。それらを`print`で表示しておしまいです。97～98%程度の正答率が出せていることがわかると思います。

## データの保存と読み込み

せっかく学習したモデルなので、あとで使いたいですよね。そのためにモデルを保存することができます。

先程作成したコード`mnist.py`の最後に一行付け加えるだけです。

```py
model.save_weights('model')
```

```sh
python3 mnist.py
```

として実行すると、また学習をして、最後にモデルデータを保存します。ファイルは`model.data-00000-of-00001`と`model.index`になります。これを読み込んで、テストデータを食わせて結果を表示するコードを書いてみましょう。以下のようなコードを`mnist_load.py`として作成します。

```py
import numpy as np
import tensorflow as tf
from tensorflow import keras


def get_data():
    train_data, test_data = keras.datasets.mnist.load_data()
    train_images, train_labels = train_data
    test_images, test_labels = test_data
    train_images = train_images / 255.0
    test_images = test_images / 255.0
    return(train_images, train_labels, test_images, test_labels)


def create_model():
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    return model


(train_images, train_labels, test_images, test_labels) = get_data()

model = create_model()
model.load_weights('model')

predictions = model.predict(test_images[0:20])

for i in range(5):
    predicted_index = np.argmax(predictions[i])
    print(f"prediction= {predicted_index} answer = {test_labels[i]}")
```

途中まで`mnist.py`とほとんど同じです。慣れたら共通部分を同じファイルにまとめると良いでしょう。異なるのは、`model.fit`で重みをロードしていたところが、`mode.load_weights`で重みを読み込んでいるところです。TensorFlowは、モデルの「形」は保存してくれないので、このように`create_model`関数はモデルの保存、読み込みの両方で必要です。コードでモデルの形だけ作って、その重みをファイルからロードするイメージです。

さて、重みを読み込んだモデルが「学習済みモデル」になるため、画像データを入力したら、それがどの手書き数字であるかを予測してくれることになります。とりあえず`test_images`の先頭の20個を食わせることにしましょう。コードのこの部分です。

```py
predictions = model.predict(test_images[0:10])
```

モデルを分類器をとして使う場合は、`model.predict`に配列を渡します。ここで注意ですが、効率のために画像をまとめて渡すことが前提になっています。つまり、画像をまとめて渡すと、それらに対する結果をまとめて返す、という形になっています。ここでは20枚のデータを渡したので、20個分の結果が`predictions`として帰ってきます。

さて、`predictions`は、ニューラルネットワークの生の出力になっています。20枚のデータを食わせたので、`predictions`は20次元の配列ですが、その配列の要素`predictions[i]`は、ニューラルネットワークが10個の分類器であることを反映して、10次元の配列になっています。これは、最後の10個のニューロンの出力です。そこで、10次元配列`predictions[i]`のうち、最大の値を持つインデックスを`numpy.argmax`で探してやりましょう。このうち、一番大きな出力を出したニューロンのインデックスが、このモデルが予測する結果となります。

実行結果はこんな感じになります。

```sh
$ python3 mnist_load.py
prediction= 7 answer = 7
prediction= 2 answer = 2
prediction= 1 answer = 1
prediction= 0 answer = 0
prediction= 4 answer = 4
prediction= 1 answer = 1
prediction= 4 answer = 4
prediction= 9 answer = 9
prediction= 6 answer = 5
prediction= 9 answer = 9
prediction= 0 answer = 0
prediction= 6 answer = 6
prediction= 9 answer = 9
prediction= 0 answer = 0
prediction= 1 answer = 1
prediction= 5 answer = 5
prediction= 9 answer = 9
prediction= 7 answer = 7
prediction= 3 answer = 3
prediction= 4 answer = 4
```

途中で6と5を１つ間違えたようですね。

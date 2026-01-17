---
title: "Pythonで音を鳴らす"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python","wav","sound"]
published: true
---

## はじめに

なにか音を鳴らすプログラムを組みたくなる時があります。以下ではJupyter Notebook (Google Colab)上で音を鳴らすサンプルです。

ソースコードは以下においてあります。

[kaityo256/python_play_sound](https://github.com/kaityo256/python_play_sound)

Google Colabで開いてそのまま試すこともできます。

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kaityo256/python_play_sound/blob/main/play_mml.ipynb)

## 音の鳴らし方

音を鳴らすには、波形データをNumPy配列で作って`IPython.display.Audio`に突っ込むのが簡単です。例えばサンプリングレート48kHz、長さ1秒で、基準となるラの音(440Hz)を鳴らすには、以下のようなコードになります。

```py
import numpy as np
import IPython

rate = 48000
duration = 1.0
t = np.linspace(0., duration, int(rate*duration))
x = np.sin(2.0*np.pi*440.0*t)
IPython.display.Audio(x, rate=rate, autoplay=True)
```

サンプリングレートは1秒間にあるデータの数なので、それに秒数をかけたものが総データ数になります。サンプリングレートは44.1kHzか、48kHzにすることが多いようです。

そのデータ数だけの波形データを用意すれば良いわけですが、今回は440Hzのサインカーブ$\sin(2 \pi f t)$を書き込んだ配列`x`を、`IPython.display.Audio`に突っ込めばOKです。例えばGoogle Colabで実行すると以下のような画面が出て、音がなります。

![実行画面](/images/python_play_sound/playsound.png)

後のために、テンポから４分音符の長さを求めて、その長さだけ演奏するようにしましょう。4分音符の音の長さはBPM (Beat Per Minutes)から決まります。BPMは1分あたりの4分音符の数です。なのでBPM=60なら4分音符は1秒、120なら0.5です。ここではBPM=120、つまり4分音符の長さは0.5秒としましょう。

```py
rate = 48000
BPM = 120
qn_duration = 60.0/BPM
t = np.linspace(0., qn_duration, int(rate*qn_duration))
x = np.sin(2.0*np.pi*440.0*t)
IPython.display.Audio(x, rate=rate, autoplay=True)
```

## MMLから音を鳴らす

Music Macro Language (MML)という、音楽のためのDSLがあります。古の時代、BASICのPLAY文で音を鳴らすことができました。CDEFGABがそれぞれドレミファソラシド、Rが休符です。例えば4分音符は`C4`、2分音符は`C2`と数字を続けますが、今回は全部4分音符ということにして音階だけ表現することにしましょう。

音階ですが、「ラ(A)」の音を基準とし、周波数を2倍にすると1オクターブ上がり、半分にすると1オクターブ下がります。1オクターブを12個の音に分け、それぞれ以下のように名前をつけましょう。

* C
* C#
* D
* D#
* E
* F
* F#
* G
* G#
* A
* A#
* B

これを対数スケールで均等に分けるのが平均律、すべての音を周波数比3:2でわけていくのがピタゴラス音律です。ここでは平均律を採用しましょう。ラ(A)の音を440Hzとします。1オクターブ上がると周波数が2倍になり、それを対数スケールで12等分するので、隣の音の周波数は$2^{1/12}$倍になります。

上記で言えば、Aの音を基準の440Hzとして、一つ下の音(G#)は415.3Hz、一つ上の音(A#)は466.2Hzになります。平均律では隣合う音は$2^{1/12}$倍なので、Cの半音上げたおとC#(ドのシャープ)と、Dの半音下げた音Db(レのフラット)は全く同じ音になります。これを異名同音と言います。ちなみに、ピタゴラス音律では異名同音の周波数が微妙に変わります。

この12個の音と、休符をあわせて13個の周波数を作りましょう。

```py
freqs = [0] + [440.0 * 2.0**((i-9)/12.0) for i in range(12)]
```

音階の文字列と周波数を辞書に入れておきます。

```py
notes = ["R", "C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
dic = {}
for i, s in enumerate(notes):
    dic[s] = i
```

今回は使いませんが、`C#`なんかも一応定義しておきます。

さて、これでMMLを音に直す準備ができました。MMLを受け取って音を鳴らす関数`play_mml`は以下のように書けるでしょう。

```py
def play_mml(mml):
    rate = 48000
    BPM = 120
    qn_duration = 60.0/BPM
    t = np.linspace(0.0, qn_duration, int(rate*qn_duration))
    music = np.array([])
    for s in list(mml):
        f = freqs[dic[s]]
        music = np.append(music, np.sin(2.0*np.pi*f*t))
    return IPython.display.Audio(music, rate=rate, autoplay=True)
```

「キラキラ星」を鳴らしてみましょうか。

```py
mml_twinkle_star = "CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR"
play_mml(mml_twinkle_star)
```

「キラキラ星」が演奏されたはずです。

「かえるのうた」も同様に演奏できます。

```py
mml_frog_song = "CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR"
play_mml(mml_frog_song)
```

BPMを変えれば演奏速度を変えることができます。

## ピアノロールからの演奏

ピアノロールが画像として与えられた時、それを音に変換したいことがあります。まずはMMLからピアノロールを作成し、逆にピアノロールから音を鳴らすルーチンも作ってみましょう。

### MMLからピアノロール

まずはMMLからピアノロールを作成する関数を作ります。ここでは、音は1オクターブ(12音)だけを扱い、二次元のNumPy配列でピアノロールを表現することにしましょう。画像を扱うためのライブラリ`PIL`をインポートして、4分音符のピアノロール上での長さ`qn_length`も定義しておきます。ここでは8ドットにしておきしょう。

```py
from PIL import Image, ImageDraw, ImageFont
qn_length = 8
```

MMLの文字列を受け取って、ピアノロール用のNumPy配列を返す関数はこんな感じになります。

```py
def mml2data(mml):
    data = np.zeros((12, qn_length*len(mml)), dtype=np.uint8)
    for i, s in enumerate(list(mml)):
        if s == "R":
            continue
        j = notes.index(s) - 1
        data[11-j, (i*qn_length):((i+1)*qn_length)] = 255
    return data
```

キラキラ星のMMLを食わせてNumPy配列を作り、それを画像として可視化してやりましょう。

```py
data = mml2data("CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR")
Image.fromarray(data)
```

こんな画像が得られます。

![キラキラ星](/images/python_play_sound/pn_twinkle_star.png)

「かえるのうた」も同様です。

```py
data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
Image.fromarray(data)
```

![かえるのうた](/images/python_play_sound/pn_frog_song.png)

ピアノロールなら音を複数同時に鳴らす表現が可能なので、既存のデータにMMLを追加する関数を作りましょう。

```py
def mml2data_append(data, mml):
    for i, s in enumerate(list(mml)):
        if s == "R":
            continue
        j = notes.index(s) - 1
        data[11-j, (i*qn_length):((i+1)*qn_length)] = 255
    return data
```

これを使うと、「かえるのうた」の輪唱を作ることができます。

```py
data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
data = mml2data_append(data, "RRRRRRRRCDEFEDCREFGAGFERCRCRCRCR")
data = mml2data_append(data, "RRRRRRRRRRRRRRRRCDEFEDCREFGAGFER")
Image.fromarray(data)
```

![かえるのうた](/images/python_play_sound/pn_frog_song2.png)

面倒なので、最初の人が歌い終わったらおしまいにしています。

### ピアノロールから音を鳴らす

次に、このピアノロールから音を鳴らす関数を作りましょう。画像を行ごとに走査して、音のなり始めと終わりを検出し、その場所に対応する周波数でサインカーブを乗せるだけです。

```py
def data2audio(img):
    _, length = img.shape
    rate =48000
    BPM = 120
    qn_duration = 60.0/BPM
    x = np.zeros(int(length / qn_length * qn_duration * rate))
    for i in range(12):
        note_on = False
        start = 0
        for j in range(length):
            if note_on:
                if img[i][j] == 0:
                    note_on = False
                    start = start / qn_length
                    end = j / qn_length
                    note_length = end - start
                    note_len_r = int(note_length*qn_duration*rate)
                    t = np.linspace(0.0, note_length*qn_duration, note_len_r)
                    start_r = int(start * qn_duration * rate)
                    x[start_r:start_r+note_len_r] += np.sin(2.0*np.pi*freqs[12-i]*t)
            else:
                if img[i][j] == 255:
                    note_on = True
                    start = j
    return IPython.display.Audio(x, rate=rate, autoplay=True)
```

キラキラ星を鳴らしてみましょう。

```py
data = mml2data("CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR")
IPython.display.display(Image.fromarray(data))
data2audio(data)
```

以下のように、食わせたピアノロールが表示されつつ、音もなったはずです。

![キラキラ星](/images/python_play_sound/play_pn_twinkle_star.png)

「かえるのうた」の輪唱版も鳴らしてみましょう。

```py
data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
data = mml2data_append(data, "RRRRRRRRCDEFEDCREFGAGFERCRCRCRCR")
data = mml2data_append(data, "RRRRRRRRRRRRRRRRCDEFEDCREFGAGFER")
IPython.display.display(Image.fromarray(data))
data2audio(data)
```

![かえるのうた(輪唱版)](/images/python_play_sound/play_pn_frog_song.png)

「かえるのうた」が聞こえてきたでしょうか？

## まとめ

Pythonで音を鳴らしてみました。基本的には音に対応する一次元のNumPy配列を作って`IPython.display.Audio`につっこむだけです。ローカルのJupyter NotebookやGoogle Colabで音がなるのでちょっと楽しいかもしれません。応用例として、簡易MMLを鳴らしたり、ピアノロールっぽいものを作って音に変換したりしてみました。生音を作るシーンはほとんど無いと思いますが、もし何かデータを音に変換したくなったりしたときに、この記事が参考になれば幸いです。

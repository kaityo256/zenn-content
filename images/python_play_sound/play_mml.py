# -*- coding: utf-8 -*-
"""play_mml.ipynb
# MMLの演奏及びピアノロールの演奏サンプル
"""

import IPython
from PIL import Image, ImageDraw, ImageFont
import numpy as np

"""## 音を鳴らす
### ラの音(440Hz)を1秒鳴らす """

rate = 48000
duration = 1.0
t = np.linspace(0., duration, int(rate*duration))
x = np.sin(2.0*np.pi*440.0*t)
IPython.display.Audio(x, rate=rate, autoplay=True)

"""### テンポ(BPM)を指定し、４分音符の長さだけ鳴らす

BPM=120であるため、4分音符の長さは60/BPM=0.5秒
"""

rate = 48000
BPM = 120
qn_duration = 60.0/BPM
t = np.linspace(0., qn_duration, int(rate*qn_duration))
x = np.sin(2.0*np.pi*440.0*t)
IPython.display.Audio(x, rate=rate, autoplay=True)

"""## MMLの演奏

周波数を12種類定義。ただし、`freqs[0]`は休符(周波数0)。
"""

freqs = [0] + [440.0 * 2.0**((i-9)/12.0) for i in range(12)]

"""MMLとfreqsのインデックスの対応辞書を作る。"""

notes = ["R", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
dic = {}
for i, s in enumerate(notes):
    dic[s] = i

"""MMLを受け取って音を鳴らす関数"""


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


# キラキラ星
mml_twinkle_star = "CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR"
play_mml(mml_twinkle_star)

# かえるのうた
mml_frog_song = "CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR"
play_mml(mml_frog_song)

"""## ピアノロールからの演奏
`qn_length`は、4分音符のドット数
"""

qn_length = 8

"""### MMLからピアノロール作成

MMLからNumPy配列を作る関数。y座標は12行。ドからシまでに対応。
"""


def mml2data(mml):
    data = np.zeros((12, qn_length*len(mml)), dtype=np.uint8)
    for i, s in enumerate(list(mml)):
        if s == "R":
            continue
        j = notes.index(s) - 1
        data[11-j, (i*qn_length):((i+1)*qn_length)] = 255
    return data


# キラキラ星
data = mml2data("CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR")
Image.fromarray(data)

data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
Image.fromarray(data)

"""既存の既存のデータのMMLを追加(輪唱用)。"""


def mml2data_append(data, mml):
    for i, s in enumerate(list(mml)):
        if s == "R":
            continue
        j = notes.index(s) - 1
        data[11-j, (i*qn_length):((i+1)*qn_length)] = 255
    return data


# かえるのうた(輪唱)
data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
data = mml2data_append(data, "RRRRRRRRCDEFEDCREFGAGFERCRCRCRCR")
data = mml2data_append(data, "RRRRRRRRRRRRRRRRCDEFEDCREFGAGFER")
Image.fromarray(data)

"""### MMLから音に変換"""


def data2audio(img):
    _, length = img.shape
    rate = 48000
    BPM = 120
    qn_duration = 60.0/BPM
    x = np.zeros(int(length / qn_length * qn_duration * rate))
    note_on = False
    start = 0
    for i in range(12):
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
                    x[start_r:start_r +
                        note_len_r] += np.sin(2.0*np.pi*freqs[12-i]*t)
            else:
                if img[i][j] == 255:
                    note_on = True
                    start = j
    return IPython.display.Audio(x, rate=rate, autoplay=True)


data = mml2data("CCGGAAGRFFEEDDCRGGFFEEDRGGFFEEDRCCGGAAGRFFEEDDCR")
IPython.display.display(Image.fromarray(data))
data2audio(data)

data = mml2data("CDEFEDCREFGAGFERCRCRCRCRCDEFEDCR")
data = mml2data_append(data, "RRRRRRRRCDEFEDCREFGAGFERCRCRCRCR")
data = mml2data_append(data, "RRRRRRRRRRRRRRRRCDEFEDCREFGAGFER")
IPython.display.display(Image.fromarray(data))
data2audio(data)

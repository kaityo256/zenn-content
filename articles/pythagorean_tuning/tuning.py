from fractions import Fraction
import numpy as np
import IPython

# Pythagorean

ratio_p = [1] * 8

ratio_p[7] = ratio_p[0] * 2  # C->C

ratio_p[4] = ratio_p[0] * Fraction(3, 2)      # C->G
ratio_p[1] = ratio_p[4] * Fraction(3, 2) / 2  # G->D
ratio_p[5] = ratio_p[1] * Fraction(3, 2)      # D->A
ratio_p[2] = ratio_p[5] * Fraction(3, 2) / 2  # A->E
ratio_p[6] = ratio_p[2] * Fraction(3, 2)      # E->B

ratio_p[3] = ratio_p[0] * Fraction(2, 3) * 2  # C->F

for n, r in zip(list("CDEFGABC"), ratio_p):
    print(f"{n}: {r}")

# Just

ratio_j = [1] * 8
ratio_j[7] = ratio_j[0] * 2  # C->C

# C:E:G = 4:5:6
ratio_j[2] = ratio_j[0] * Fraction(5, 4)
ratio_j[4] = ratio_j[0] * Fraction(6, 4)

# G:B:D = 4:5:6
ratio_j[6] = ratio_j[4] * Fraction(5, 4)
ratio_j[1] = ratio_j[4] * Fraction(6, 4) / 2

# F:A:C = 4:5:6
ratio_j[3] = ratio_j[0] * Fraction(4, 6) * 2
ratio_j[5] = ratio_j[0] * Fraction(5, 6) * 2

for n, r in zip(list("CDEFGABC"), ratio_j):
    print(f"{n}: {r}")

# Equal
n = [0, 2, 4, 5, 7, 9, 11, 12]
ratio_e = [2**(i / 12.0) for i in n]

for n, r in zip(list("CDEFGABC"), ratio_e):
    print(f"{n}: {r}")

# Make frequency

freq_p = [440.0 / ratio_p[5] * ratio_p[i] for i in range(8)]
freq_j = [440.0 / ratio_j[5] * ratio_j[i] for i in range(8)]
freq_e = [440.0 / ratio_e[5] * ratio_e[i] for i in range(8)]

for i, r in enumerate(list("CDEFGABC")):
    print(f"{r} {freq_p[i]:.2f} {freq_j[i]:.2f} {freq_e[i]:.2f}")


def play_all(freq):
    rate = 48000
    duration = 0.5
    x = np.zeros(int(rate * duration * 8))
    for i in range(8):
        t = np.linspace(0., duration, int(rate * duration))
        start = int(rate * duration * i)
        end = int(rate * duration * (i + 1))
        x[start:end] = np.sin(2.0 * np.pi * freq[i] * t)
    return IPython.display.Audio(x, rate=rate, autoplay=True)


def play_CEGC(freq):
    rate = 48000
    duration = 1.0
    rd = int(rate * duration)
    x = np.zeros(rd * 4)
    t = np.linspace(0., duration * 4, rd * 4)
    x[0:rd * 4] += np.sin(2.0 * np.pi * freq[0] * t)
    t = np.linspace(0., duration * 3, rd * 3)
    x[rd:rd * 4] += np.sin(2.0 * np.pi * freq[2] * t)
    t = np.linspace(0., duration * 2, rd * 2)
    x[rd * 2:rd * 4] += np.sin(2.0 * np.pi * freq[4] * t)
    t = np.linspace(0., duration * 1, rd)
    x[rd * 3:rd * 4] += np.sin(2.0 * np.pi * freq[7] * t)
    return IPython.display.Audio(x, rate=rate, autoplay=True)


def play_two(freq1, freq2):
    rate = 48000
    duration = 4.0
    t = np.linspace(0., duration, int(rate * duration))
    x = np.sin(2.0 * np.pi * freq1 * t)
    x += np.sin(2.0 * np.pi * freq2 * t)
    return IPython.display.Audio(x, rate=rate, autoplay=True)


# ピタゴラス音律と純正律
play_two(freq_p[0], freq_j[0])

# 純正律と平均律
play_two(freq_j[0], freq_e[0])

# ピタゴラス音律と平均律
play_two(freq_p[0], freq_e[0])

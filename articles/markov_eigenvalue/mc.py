import random

N = 5


def one_trial(start):
    position = start
    while position in range(1, N):
        position += random.choice([-1, 1])
    return position == N


def win_probability(start):
    n_trial = 100000
    win = 0
    for _ in range(n_trial):
        if one_trial(start):
            win += 1
    win_rate = win / n_trial
    print(f"{start} {win_rate}")


for s in range(1, N):
    win_probability(s)

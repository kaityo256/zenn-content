import numpy as np

N = 1000
v = 0.0
gamma = 0.1
np.random.seed(1)

for t in range(10*N):
    v += np.random.randn()*0.1
    v -= gamma * v
    print(f"{t} {v}")

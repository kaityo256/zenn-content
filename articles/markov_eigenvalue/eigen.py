import numpy as np
import numpy.linalg as LA

# マスの数(0からNまで)
N = 4

# 遷移行列Mを作る
M = np.zeros((N + 1, N + 1))
for i in range(N + 1):
    if i in (0, N):
        M[i][i] = 1.0
    else:
        M[i + 1][i] = 0.5
        M[i - 1][i] = 0.5


# Mのべき乗を計算し、M^{\infty}がどうなりそうか見てみる
np.set_printoptions(precision=3)
Minf = M
for _ in range(100):
    Minf = M@Minf
print(Minf)

# 固有ベクトルを求め、Mを対角化する
w, P = LA.eig(M)
Pinv = LA.inv(P)
D = np.diag(w)
print("D=")
print(D)
print("P^-1MP=")
print(Pinv@M@P)

# M^{\infty}を求める
Dinf = np.diag([1, 1, 0, 0, 0])
Minf = P@Dinf@Pinv
print(Minf)

# 1のマスから始めた場合
a = (np.array([0, 1, 0, 0, 0]))
print(Pinv@a)

# 2のマスから始めた場合
a = (np.array([0, 0, 1, 0, 0]))
print(Pinv@a)

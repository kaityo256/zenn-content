import random
import sys


def find(index, cluster):
    while index != cluster[index]:
        index = cluster[index]
    return index


def union(index1, index2, cluster):
    c1 = find(index1, cluster)
    c2 = find(index2, cluster)
    if c1 < c2:
        cluster[c2] = c1
    else:
        cluster[c1] = c2


def show(L, cluster):
    for iy in range(L):
        for ix in range(L):
            index = ix + iy * L
            c = find(index, cluster)
            print(f"{c:02d} ", end="")
        print()


def connect(p, x1, y1, x2, y2, L, cluster):
    i1 = x1 + y1 * L
    i2 = x2 + y2 * L
    if random.random() < p:
        union(i1, i2, cluster)


def percolation_check(L, cluster):
    for ix1 in range(L):
        c1 = find(ix1, cluster)
        for ix2 in range(L):
            c2 = find(ix2 + (L - 1) * L, cluster)
            if c1 == c2:
                return True
    return False


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


def mc_average(p, num_samples, L):
    sum = 0.0
    for _ in range(num_samples):
        sum += mc_onestep(p, L)
    sum /= num_samples
    return sum


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


if __name__ == "__main__":
    main()

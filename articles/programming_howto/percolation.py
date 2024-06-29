def find(index, cluster):
    while index != cluster[index]:
        index = cluster[index]
    return index


def main():
    cluster = [0, 0, 1, 2, 3]
    for i in range(len(cluster)):
        print(i, find(i, cluster))


if __name__ == "__main__":
    main()

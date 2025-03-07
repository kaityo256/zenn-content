class Atom:
    def __init__(self, x, y, z, vx, vy, vz):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def __str__(self):
        return f"{self.x} {self.y} {self.z} {self.vx} {self.vy} {self.vz} "


def read_atoms(f):
    atoms = []
    for line in f:
        if "ITEM: TIMESTEP" in line:
            return atoms
        a = line.split()
        x = float(a[2])
        y = float(a[3])
        z = float(a[4])
        vx = float(a[5])
        vy = float(a[6])
        vz = float(a[7])
        atom = Atom(x, y, z, vx, vy, vz)
        atoms.append(atom)
    return atoms  # ここを追加


def read_file(filename):
    frames = []
    with open(filename) as f:
        for line in f:
            if "ITEM: ATOMS" in line:
                atoms = read_atoms(f)
                frames.append(atoms)
    return frames


def temperature(atoms):
    N = len(atoms)
    K = 0.0
    for a in atoms:
        K += a.vx**2
        K += a.vy**2
        K += a.vz**2
    T = K / 3.0 / N
    return T


def main():
    filename = "sample.lammpstrj"
    frames = read_file(filename)
    for atoms in frames:
        print(temperature(atoms))


if __name__ == "__main__":
    main()

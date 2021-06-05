import numpy as np
import random


def get_lattice_number(L, rho):
    m = np.ceil((L**3 * rho / 4.0)**(1.0 / 3.0))
    return int(m)


def make_fcc_pure(L, rho):
    m = get_lattice_number(L, rho)
    a = L / m
    ha = a * 0.5
    atoms = []
    for i in range(m**3):
        ix = i % m
        iy = (i // m) % m
        iz = i // (m * m)
        x = ix * a
        y = iy * a
        z = iz * a
        atoms.append((x, y, z))
        atoms.append((x + ha, y + ha, z))
        atoms.append((x + ha, y, z + ha))
        atoms.append((x, y + ha, z + ha))
    return atoms


def make_fcc_defect(L, rho):
    atoms = make_fcc_pure(L, rho)
    n = int(rho * L**3)
    return random.sample(atoms, n)


atoms = make_fcc_defect(10.0, 0.489)
for a in atoms:
    print(f"{a[0]} {a[1]} {a[2]}")

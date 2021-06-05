import numpy as np


def get_lattice_number(L, rho):
    m = np.floor((L**3 * rho / 4.0)**(1.0 / 3.0))
    drho1 = np.abs(4.0 * m**3 / L**3 - rho)
    drho2 = np.abs(4.0 * (m + 1)**3 / L**3 - rho)
    if drho1 < drho2:
        return int(m)
    else:
        return int(m + 1)


def make_fcc_pure(L, rho):
    m = get_lattice_number(L, rho)
    a = L / m
    ha = a * 0.5
    atoms = []
    for ix in range(m):
        for iy in range(m):
            for iz in range(m):
                x = ix * a
                y = iy * a
                z = iz * a
                atoms.append((x, y, z))
                atoms.append((x + ha, y + ha, z))
                atoms.append((x + ha, y, z + ha))
                atoms.append((x, y + ha, z + ha))
    return atoms


def plot_pure():
    L = 10
    for i in range(70):
        rho = 0.2 + 0.01 * i
        m = get_lattice_number(L, rho)
        rho_a = 4.0 * m**3 / L**3
        print(f"{rho} {rho_a} {m}")


atoms = make_fcc_pure(10.0, 0.5)
for a in atoms:
    print(f"{a[0]} {a[1]} {a[2]}")

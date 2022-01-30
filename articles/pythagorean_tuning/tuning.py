from fractions import Fraction

# Pythagorean

ratio_p = [1] * 8

ratio_p[7] = ratio_p[0] * 2  # C->C

ratio_p[4] = ratio_p[0] * Fraction(3, 2)      # C->G
ratio_p[1] = ratio_p[4] * Fraction(3, 2) / 2  # G->D
ratio_p[5] = ratio_p[1] * Fraction(3, 2)      # D->A
ratio_p[2] = ratio_p[5] * Fraction(3, 2) / 2  # A->E
ratio_p[6] = ratio_p[2] * Fraction(3, 2)      # E->B

ratio_p[3] = ratio_p[0] * Fraction(2, 3) * 2  # C->F

for r in ratio_p:
    print(r)

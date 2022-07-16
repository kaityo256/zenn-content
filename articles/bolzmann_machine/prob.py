import itertools
import numpy as np
from fractions import Fraction

w_a = Fraction(3,1)
w_b = Fraction(1,2)
w_c = Fraction(1,2)

w_ac = Fraction(1,9)
w_bc = Fraction(4,1)

print("A B C")
sum = Fraction(0,1)
for a,b,c in itertools.product([0,1],[0,1],[0,1]):
    prob = 1
    if a:
        prob *= w_a
    if b:
        prob *= w_b
    if c:
        prob *= w_c
    if a and c:
        prob *= w_ac
    if b and c:
        prob *= w_bc
    print(f"{a} {b} {c} {prob}")
    sum += prob
print(sum)
print("A C")
for a,c in itertools.product([0,1],[0,1]):
    prob = 1
    if a:
        prob *= w_a
    if c:
        prob *= w_c
    if a and c:
        prob *= w_ac
    print(f"{a} {c} {prob}")

print()
print("B C")
for b,c in itertools.product([0,1],[0,1]):
    prob = 1
    if b:
        prob *= w_b
    if c:
        prob *= w_c
    if b and c:
        prob *= w_bc
    print(f"{b} {c} {prob}")




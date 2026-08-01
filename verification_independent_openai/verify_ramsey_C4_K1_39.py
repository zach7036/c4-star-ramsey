#!/usr/bin/env python3
"""Exact audit of the polynomial certificate for R(C4, K_{1,39}) = 46.

This script deliberately uses only Python's standard library.  It verifies:

* both displayed polynomial factorizations coefficient by coefficient;
* Q(x) = 1 - q(-x);
* the two moment substitutions as identities in T; and
* the final strict rational inequalities for every 0 <= T <= 92.

The combinatorial derivation of the moment data is proved in the accompanying
manuscript; this program checks the otherwise error-prone exact arithmetic.
"""

from __future__ import annotations

from fractions import Fraction


Polynomial = tuple[int, ...]  # coefficients in ascending order


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    values = [0] * size
    for index, coefficient in enumerate(left):
        values[index] += coefficient
    for index, coefficient in enumerate(right):
        values[index] += coefficient
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def scale(polynomial: Polynomial, scalar: int) -> Polynomial:
    return tuple(scalar * coefficient for coefficient in polynomial)


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    values = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            values[i + j] += a * b
    return tuple(values)


def product(*factors: Polynomial) -> Polynomial:
    result: Polynomial = (1,)
    for factor in factors:
        result = multiply(result, factor)
    return result


def substitute_minus_x(polynomial: Polynomial) -> Polynomial:
    return tuple(
        coefficient if index % 2 == 0 else -coefficient
        for index, coefficient in enumerate(polynomial)
    )


DENOMINATOR = 26_468_750

# q numerator:
# (2x+5)^2(3x+5)(4904x^2-38072x+85705).
q_numerator = product(
    (5, 2),
    (5, 2),
    (5, 3),
    (85_705, -38_072, 4_904),
)

# Numerator of the displayed factorization of 1-q:
# (3-x)(2x-5)^2(14712x^2+101560x+210075).
one_minus_q_factored = product(
    (3, -1),
    (-5, 2),
    (-5, 2),
    (210_075, 101_560, 14_712),
)
assert add(q_numerator, one_minus_q_factored) == (DENOMINATOR,)

# Q = 1-q(-x).  Verify two useful factorizations.
q_at_minus_x = substitute_minus_x(q_numerator)
Q_numerator = add((DENOMINATOR,), scale(q_at_minus_x, -1))
Q_factored = product(
    (3, 1),
    (5, 2),
    (5, 2),
    (210_075, -101_560, 14_712),
)
assert Q_numerator == Q_factored

Q_minus_one_factored = product(
    (-5, 2),
    (-5, 2),
    (-5, 3),
    (85_705, 38_072, 4_904),
)
assert add(Q_minus_one_factored, (DENOMINATOR,)) == Q_numerator

# The nonprincipal power sums are
# s_0,...,s_5 = 45,-7,273,-67,1785,T-615.
fixed_moments = (45, -7, 273, -67, 1785)


def moment_sum(
    numerator: Polynomial, *, t_coefficient: int, t_constant: int
) -> tuple[Fraction, Fraction]:
    """Return constant + coefficient*T after substituting the moments."""

    assert len(numerator) == 6
    constant = sum(
        Fraction(numerator[index] * fixed_moments[index], DENOMINATOR)
        for index in range(5)
    )
    constant += Fraction(numerator[5] * t_constant, DENOMINATOR)
    coefficient = Fraction(numerator[5] * t_coefficient, DENOMINATOR)
    return constant, coefficient


q_constant, q_T = moment_sum(
    q_numerator, t_coefficient=1, t_constant=-615
)
Q_constant, Q_T = moment_sum(
    Q_numerator, t_coefficient=1, t_constant=-615
)

assert q_T == Fraction(58_848, DENOMINATOR)
assert q_constant - 21 == Fraction(1_084_790, DENOMINATOR)
assert Q_T == Fraction(58_848, DENOMINATOR)
assert 22 - Q_constant == Fraction(8_562_180, DENOMINATOR)

lower_margin_at_T0 = q_constant - 21
upper_margin_at_T92 = 22 - (Q_constant + 92 * Q_T)

assert lower_margin_at_T0 == Fraction(542_395, 13_234_375)
assert upper_margin_at_T92 == Fraction(1_574_082, 13_234_375)
assert lower_margin_at_T0 > 0
assert upper_margin_at_T92 > 0

print("All exact polynomial identities passed.")
print(f"sum q - 21 at T=0:  {lower_margin_at_T0}")
print(f"22 - sum Q at T=92: {upper_margin_at_T92}")
print("Certificate conclusion: 21 < N_+ < 22, an impossibility.")

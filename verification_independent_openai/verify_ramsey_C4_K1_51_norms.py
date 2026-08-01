#!/usr/bin/env python3
"""Independent exact audit of the cyclotomic norm step in the f(51) proof.

The proposed proof of R(C4, K_{1,51}) = 59 reduces its only finite
number-theory check to the following question.  For

    mu = 2*cos(2*pi/d),

can 7 - mu be a square in Q(mu)?  If it were, its field norm

    Psi_d(7) = Norm_{Q(mu)/Q}(7 - mu)

would be an integer square.  Here Psi_d is the minimal polynomial of mu.

This script constructs every Psi_d exactly with SymPy and tests the required
norms.  It also audits the analogous f(83) computation at 9 and records the
one deliberately excluded rational case d=4, where Psi_4(9)=9.

No floating-point arithmetic is used.
"""

from __future__ import annotations

from math import isqrt

import sympy as sp


x = sp.symbols("x")


def cosine_minimal_polynomial(d: int) -> sp.Poly:
    """Return the monic minimal polynomial of 2*cos(2*pi/d) over Q."""

    expression = 2 * sp.cos(2 * sp.pi / d)
    polynomial = sp.Poly(sp.minimal_polynomial(expression, x), x, domain=sp.ZZ)
    assert polynomial.LC() == 1
    assert polynomial.degree() == sp.totient(d) // 2
    return polynomial


def is_integer_square(value: int) -> bool:
    if value < 0:
        return False
    root = isqrt(value)
    return root * root == value


def norm_scan(argument: int, maximum_order: int) -> list[tuple[int, int]]:
    """Return all d for which Psi_d(argument) is an integer square."""

    squares: list[tuple[int, int]] = []
    for d in range(3, maximum_order + 1):
        polynomial = cosine_minimal_polynomial(d)
        norm = int(polynomial.eval(argument))
        assert norm > 0
        if is_integer_square(norm):
            squares.append((d, norm))
    return squares


def lucas_fibonacci_audit(maximum_order: int) -> None:
    """Check V_d(7)-2 = L_{4d}-2 = 5*F_{2d}^2 exactly."""

    v_previous = 2
    v_current = 7
    for d in range(1, maximum_order + 1):
        if d == 1:
            v_d = v_current
        else:
            v_previous, v_current = v_current, 7 * v_current - v_previous
            v_d = v_current
        expected = sp.lucas(4 * d) - 2
        fibonacci_form = 5 * sp.fibonacci(2 * d) ** 2
        assert v_d - 2 == expected == fibonacci_form


def ground_truth_checks() -> None:
    """Audit the examples and the known square escape cases at argument 6."""

    expected_at_seven = {
        3: 8,
        4: 7,
        5: 55,
        6: 6,
        7: 377,
        13: 121_393,
    }
    for d, expected in expected_at_seven.items():
        assert int(cosine_minimal_polynomial(d).eval(7)) == expected

    # These are the genuine square cases that make the same method correctly
    # inconclusive for a hypothetical 7-regular graph on 45 vertices.
    assert int(cosine_minimal_polynomial(14).eval(6)) == 13**2
    assert int(cosine_minimal_polynomial(15).eval(6)) == 31**2


def main() -> None:
    ground_truth_checks()
    lucas_fibonacci_audit(93)

    squares_at_seven = norm_scan(argument=7, maximum_order=59)
    assert squares_at_seven == []

    squares_at_nine = norm_scan(argument=9, maximum_order=93)
    assert squares_at_nine == [(4, 9)]

    # d=4 gives mu=0, hence sqrt(9-mu)=+/-3.  This is the rational
    # eigenvalue case already retained in the trace argument, not an
    # unexamined Galois escape.
    rational_orders = {3, 4, 6}
    nonrational_squares_at_nine = [
        pair for pair in squares_at_nine if pair[0] not in rational_orders
    ]
    assert nonrational_squares_at_nine == []

    print("All exact cyclotomic norm checks passed.")
    print("argument 7, orders 3..59: no square norms")
    print(
        "argument 9, orders 3..93: only (d, norm)=(4, 9), "
        "the separately handled rational case mu=0"
    )
    print("ground-truth square cases at argument 6: d=14 and d=15 confirmed")
    print("Lucas-Fibonacci identity at argument 7 confirmed through d=93")


if __name__ == "__main__":
    main()

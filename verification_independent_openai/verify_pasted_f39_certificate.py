#!/usr/bin/env python3
"""Exact audit of the degree-five f(39) certificate in the pasted manuscript.

This certificate is different from the factored certificate already archived
in outputs/verify_ramsey_C4_K1_39.py.  The present checker verifies the four
pointwise inequalities by exact rational real-root isolation, including the
algebraic endpoints +/-sqrt(3), and then performs the exact moment
substitution for every 0 <= kappa <= 46.
"""

from __future__ import annotations

import sympy as sp


x = sp.symbols("x")

p = (
    sp.Rational(423, 200_000) * x**5
    + sp.Rational(19, 15_625) * x**4
    - sp.Rational(8_719, 200_000) * x**3
    - sp.Rational(4_087, 250_000) * x**2
    + sp.Rational(390_143, 1_000_000) * x
    + sp.Rational(277_973, 500_000)
)

q = (
    sp.Rational(11, 5_000) * x**5
    - sp.Rational(203, 250_000) * x**4
    - sp.Rational(45_053, 1_000_000) * x**3
    + sp.Rational(5_561, 500_000) * x**2
    + sp.Rational(98_979, 250_000) * x
    + sp.Rational(114_939, 250_000)
)


def unique_root_interval(expression: sp.Expr) -> tuple[sp.Rational, sp.Rational]:
    """Return a tight exact interval containing the expression's only real root."""

    intervals = sp.intervals(
        sp.Poly(expression, x, domain=sp.QQ),
        eps=sp.Rational(1, 10**12),
    )
    assert len(intervals) == 1
    interval, multiplicity = intervals[0]
    assert multiplicity == 1
    left, right = interval
    return sp.Rational(left), sp.Rational(right)


def sign_audit() -> None:
    """Prove the four interval inequalities from isolated-root locations."""

    # p-1 has its only root below sqrt(3), so p>=1 on [sqrt(3),3].
    _, right = unique_root_interval(p - 1)
    assert right > 0 and right**2 < 3
    assert sp.simplify((p - 1).subs(x, 3)) > 0

    # p has its only root below -3, so p>=0 on [-3,-sqrt(3)].
    _, right = unique_root_interval(p)
    assert right < -3
    assert sp.simplify(p.subs(x, -3)) > 0

    # 1-q has its only root above 3, so q<=1 on [sqrt(3),3].
    left, _ = unique_root_interval(1 - q)
    assert left > 3
    assert sp.simplify((1 - q).subs(x, 3)) > 0

    # -q has its only root above -sqrt(3), so q<=0 on [-3,-sqrt(3)].
    left, _ = unique_root_interval(-q)
    assert left < 0 and left**2 < 3
    assert sp.simplify((-q).subs(x, -3)) > 0

    # Directly retain the exact algebraic endpoint margins as an additional
    # guard against accidentally replacing sqrt(3) by 1.73.
    assert sp.simplify((p - 1).subs(x, sp.sqrt(3))) > 0
    assert sp.simplify((-q).subs(x, -sp.sqrt(3))) > 0


def moment_sum(expression: sp.Expr) -> tuple[sp.Rational, sp.Rational]:
    """Return constant + slope*kappa under the six exact power sums."""

    polynomial = sp.Poly(expression, x, domain=sp.QQ)
    fixed_moments = (45, -7, 273, -67, 1_785)
    constant = sum(polynomial.nth(i) * fixed_moments[i] for i in range(5))
    constant += polynomial.nth(5) * (-615)
    slope = polynomial.nth(5) * 2
    return sp.Rational(constant), sp.Rational(slope)


def moment_audit() -> None:
    p_constant, p_slope = moment_sum(p)
    q_constant, q_slope = moment_sum(q)

    assert q_constant == sp.Rational(4_234_009, 200_000)
    assert p_constant + 46 * p_slope == sp.Rational(4_361_769, 200_000)
    assert q_slope >= 0 and p_slope >= 0

    for kappa in range(47):
        lower = q_constant + kappa * q_slope
        upper = p_constant + kappa * p_slope
        assert 21 < lower <= upper < 22


def main() -> None:
    sign_audit()
    moment_audit()
    print("All exact inequalities for the pasted f(39) certificate passed.")
    print("For every 0 <= kappa <= 46:")
    print("  4234009/200000 <= N_+ <= 4361769/200000")
    print("  hence 21 < N_+ < 22, impossible for an integer N_+")


if __name__ == "__main__":
    main()

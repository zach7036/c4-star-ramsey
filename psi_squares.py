r"""
The decisive computation for (59,8), i.e. for f(51) = R(C_4, K_{1,51}).

Setting: an 8-regular C_4-free graph on 59 vertices would have deficiency graph D
that is 2-regular (deg_D = z = 58 - 56 = 2), i.e. a disjoint union of cycles, and
A^2 = 7I + J - D with AD = DA.  On the complement of the all-ones vector every
eigenvalue theta of A satisfies theta^2 = 7 - mu with mu an eigenvalue of D, and
spec(D) is EXPLICIT: mu = 2cos(2 pi j / ell) per cycle of length ell.

Galois argument:
  * char poly of A is in Z[x]  =>  its spectrum is a Galois-stable multiset;
  * for mu with 7 - mu NOT a square in Q(mu), the minimal polynomial of
    sqrt(7 - mu) has degree 2*[Q(mu):Q] and its roots include both signs over every
    conjugate, so +sqrt(7-mu) and -sqrt(7-mu) carry EQUAL multiplicity and the pair
    contributes 0 to the trace;
  * rational theta requires theta^2 = 7 - mu in {5,...,9} to be a perfect square
    with mu a rational algebraic integer in [-2,2]:  only theta = +-3 (mu = -2);
  * therefore  sum theta = -8  becomes  3*(a - b) = -8  UNLESS some cycle length
    ell has a divisor d with 7 - 2cos(2 pi/d) a square in Q(zeta_d)^+.
    Since 3 does not divide 8, the graph cannot exist -- provided no such d <= 59.

Necessity check for the square case: if 7 - mu = alpha^2 with alpha an algebraic
integer in Q(mu), then N(7 - mu) = N(alpha)^2 is a perfect square in Z, where
N(7 - mu) = psi_d(7) and psi_d = minimal polynomial of 2cos(2 pi/d).

Closed form used (verified below two independent ways):
  prod_{j=0}^{d-1} (x - 2cos(2 pi j/d)) = V_d(x) - 2,  V_0 = 2, V_1 = x,
  V_d = x V_{d-1} - V_{d-2}     (for x = 7:  V_d - 2 = 5 F_{2d}^2, Fibonacci F).
Then by Mobius inversion over divisors, for d >= 3:
  psi_d(x)^2 = prod_{e | d} (V_e(x) - 2)^{mobius(d/e)}.

This script computes psi_d(7) exactly for every 3 <= d <= 59, cross-checks small d
against sympy's minimal_polynomial, and tests each for being a perfect square.
It also runs the same test for x = 9 (the k = 10 analogue on 93 vertices, which
would similarly force 3(a-b) = -10) for d <= 93.
"""
import sympy as sp
from sympy import divisors, integer_nthroot, mobius, minimal_polynomial, cos, pi, Rational


def V_values(x, dmax):
    V = [2, x]
    for _ in range(2, dmax + 1):
        V.append(x * V[-1] - V[-2])
    return V


def psi_at(x, d, V):
    num, den = 1, 1
    for e in divisors(d):
        m = mobius(d // e)
        t = V[e] - 2
        if m == 1:
            num *= t
        elif m == -1:
            den *= t
    assert num % den == 0, (d, num, den)
    q = num // den
    if d >= 3:
        r, exact = integer_nthroot(q, 2)
        assert exact, f"Q({d}) not a perfect square -- identity violated"
        return r
    return q


def crosscheck_identity(x_val, dmax=12):
    """Verify V_d(x)-2 = prod (x - 2cos(2 pi j/d)) and psi_d via sympy, d small."""
    V = V_values(x_val, dmax)
    for d in range(1, dmax + 1):
        prod = sp.Integer(1)
        for j in range(d):
            prod *= (x_val - 2 * cos(2 * pi * j / d))
        diff = abs(sp.N(prod - (V[d] - 2), 50))
        assert diff < sp.Rational(1, 10**30), f"identity fails at d={d}: diff={diff}"
    print(f"  [OK] product identity verified to 30 digits for d <= {dmax}, x = {x_val}")
    t = sp.symbols('t')
    for d in range(3, dmax + 1):
        mp = minimal_polynomial(2 * cos(2 * pi / d), t)
        val = abs(mp.subs(t, x_val))
        mine = psi_at(x_val, d, V)
        assert val == mine, (d, val, mine)
    print(f"  [OK] psi_d({x_val}) matches sympy minimal_polynomial for 3 <= d <= {dmax}")


def scan(x_val, dmax, rational_d=(1, 2, 3, 4, 6)):
    V = V_values(x_val, dmax)
    squares = []
    print(f"\n  psi_d({x_val}) for 3 <= d <= {dmax}:")
    for d in range(3, dmax + 1):
        v = psi_at(x_val, d, V)
        r, exact = integer_nthroot(v, 2)
        note = ""
        if d in rational_d:
            note = "  (mu rational -- handled separately, square-status irrelevant)"
        if exact and d not in rational_d:
            squares.append(d)
            note = "  *** PERFECT SQUARE -- potential escape ***"
        if d <= 16 or exact:
            print(f"    d={d:2d}: {v}{note}")
    return squares


if __name__ == "__main__":
    print("cross-checks:")
    crosscheck_identity(7, 12)

    print("\n=== k = 8, N = 59 (decides f(51)) ===")
    sq7 = scan(7, 59)
    print(f"\n  perfect squares among relevant d: {sq7 if sq7 else 'NONE'}")
    if not sq7:
        print("  => every irrational eigenvalue pair of A is sign-balanced;")
        print("     the only rational non-principal eigenvalues are +-3;")
        print("     trace forces 3*(a-b) = -8, impossible.")
        print("  => NO 8-regular C4-free graph on 59 vertices exists.")
        print("  => R(C_4, K_{1,51}) = 59  (lower bound f(51) >= 59: Boza Prop. 11)")

    print("\n=== k = 10, N = 93 (would decide f(83) <= 93) ===")
    sq9 = scan(9, 93)
    print(f"\n  perfect squares among relevant d: {sq9 if sq9 else 'NONE'}")
    if not sq9:
        print("  rational theta: theta^2 = 9 - mu in {7..11} -> only 9 (mu = 0, d = 4);")
        print("  trace forces 3*(a-b) = -10, impossible.")
        print("  => NO 10-regular C4-free graph on 93 vertices exists.")

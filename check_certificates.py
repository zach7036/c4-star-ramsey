r"""
Exact verification of the two dual certificates for Theorem 1 (f(39) = 46),
using ONLY rational arithmetic (Sturm counts on rational intervals + rational
bracketing of sqrt3 via t < sqrt3 <=> t^2 < 3 for t > 0).

IMPORTANT: the certificate is TIGHT at sqrt3 (e.g. p(1.73) - 1 < 0), so naive
verification on a rational super-interval [1.73, 3] FALSELY REJECTS it.  Each
constraint polynomial here has exactly one real root, lying just outside the
required algebraic interval; we bracket that root rationally by bisection and
compare the bracket against sqrt3 by squaring.

Claim verified:  p >= 1 and q <= 1 on [sqrt3, 3];  p >= 0 and q <= 0 on
[-3, -sqrt3].  Summing p (resp. q) over the non-principal spectrum and using
the exact moments M = (45, -7, 273, -67, 1785) with M5 in [-615, -523] gives
    4234009/200000 <= N_+ <= 4361769/200000,
an integer-free interval — contradiction, since N_+ counts eigenvalues.
"""
import sympy as sp

x = sp.symbols('x')

p = (sp.Rational(423, 200000) * x**5 + sp.Rational(19, 15625) * x**4
     - sp.Rational(8719, 200000) * x**3 - sp.Rational(4087, 250000) * x**2
     + sp.Rational(390143, 1000000) * x + sp.Rational(277973, 500000))
q = (sp.Rational(11, 5000) * x**5 - sp.Rational(203, 250000) * x**4
     - sp.Rational(45053, 1000000) * x**3 + sp.Rational(5561, 500000) * x**2
     + sp.Rational(98979, 250000) * x + sp.Rational(114939, 250000))

M = {0: 45, 1: -7, 2: 273, 3: -67, 4: 1785}
M5_MIN, M5_MAX = -615, -523
failures = []


def bracket_root(P, a, b, steps=300):
    """Rational bisection bracket of the unique root of P in [a, b] (sign change
    assumed).  Returns (a, b) with the root inside."""
    va = P.eval(a)
    for _ in range(steps):
        m = (a + b) / 2
        vm = P.eval(m)
        if vm == 0:
            return m, m
        if (vm > 0) == (va > 0):
            a, va = m, vm
        else:
            b = m
        if (b - a) < sp.Rational(1, 10**12):
            break
    return a, b


def below_sqrt3(t):
    """For rational t: is t < sqrt(3)?  Exact."""
    return t < 0 or t * t < 3


def check_pos_interval(name, poly):
    """poly >= 0 on [sqrt3, 3]."""
    P = sp.Poly(poly, x)
    LO, HI = sp.Rational(17, 10), sp.Integer(3)         # 17/10 < sqrt3
    n = P.count_roots(LO, HI)
    ok = P.eval(HI) > 0
    if n == 0:
        ok = ok and P.eval(LO) > 0
    elif n == 1:
        a, b = bracket_root(P, LO, HI)
        # root r in [a,b]; harmless iff r < sqrt3, guaranteed if b < sqrt3
        ok = ok and below_sqrt3(b) and P.eval(sp.Rational(9, 5)) > 0  # 1.8 > sqrt3
    else:
        ok = False
    print(f"  {name}: {'OK' if ok else 'FAIL'} (roots in [1.7,3]: {n})")
    if not ok:
        failures.append(name)


def check_neg_interval(name, poly):
    """poly >= 0 on [-3, -sqrt3]."""
    P = sp.Poly(poly, x)
    LO, HI = sp.Integer(-3), sp.Rational(-17, 10)       # -sqrt3 < -17/10
    n = P.count_roots(LO, HI)
    ok = P.eval(LO) > 0
    if n == 0:
        ok = ok and P.eval(HI) > 0
    elif n == 1:
        a, b = bracket_root(P, LO, HI)
        # root r in [a,b] with a,b < 0; harmless iff r > -sqrt3, i.e. -r < sqrt3,
        # guaranteed if -a < sqrt3 (then r > a > -sqrt3)
        ok = ok and below_sqrt3(-a) and P.eval(sp.Rational(-9, 5)) > 0
    else:
        ok = False
    print(f"  {name}: {'OK' if ok else 'FAIL'} (roots in [-3,-1.7]: {n})")
    if not ok:
        failures.append(name)


print("Certificate inequalities (all-rational verification):")
check_pos_interval("p - 1 >= 0 on [sqrt3, 3]", p - 1)
check_neg_interval("p     >= 0 on [-3, -sqrt3]", p)
check_pos_interval("1 - q >= 0 on [sqrt3, 3]", 1 - q)
check_neg_interval("-q    >= 0 on [-3, -sqrt3]", -q)

print("\nBound values (exact rational):")
Pp, Pq = sp.Poly(p, x), sp.Poly(q, x)
cp = {d: Pp.coeff_monomial(x**d if d else 1) for d in range(6)}
cq = {d: Pq.coeff_monomial(x**d if d else 1) for d in range(6)}
ub = sum(cp[d] * M[d] for d in range(5)) + cp[5] * (M5_MAX if cp[5] > 0 else M5_MIN)
lb = sum(cq[d] * M[d] for d in range(5)) + cq[5] * (M5_MIN if cq[5] > 0 else M5_MAX)
print(f"  N_+ <= {ub} = {float(ub):.6f}   (expected 4361769/200000)")
print(f"  N_+ >= {lb} = {float(lb):.6f}   (expected 4234009/200000)")
ok_vals = (ub == sp.Rational(4361769, 200000) and lb == sp.Rational(4234009, 200000))
ints = [n for n in range(60) if lb <= n <= ub]
print(f"  integers in the closed interval: {ints if ints else 'NONE'}")

if not failures and ok_vals and not ints:
    print("\nCERTIFICATE VALID: N_+ confined to an integer-free interval.")
else:
    print("\nCERTIFICATE CHECK FAILED:", failures or "bound values mismatch")
    raise SystemExit(1)

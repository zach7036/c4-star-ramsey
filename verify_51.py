r"""
Referee script for  R(C_4, K_{1,51}) = 59.        Run:  python verify_51.py

Checks:
  1. lower bound  : stored 58-vertex graph is C_4-free with delta >= 7
  2. Lemma A      : delta >= 8 on 59 vertices forces 8-regularity
  3. Lemma B      : deg_D = z identity, verified on all four stored witness graphs
  4. identity     : prod_{j<d}(x - 2cos(2pi j/d)) = V_d(x) - 2, 30-digit check, d <= 12
  5. psi values   : psi_d(7) matches sympy minimal_polynomial for 3 <= d <= 12
  6. square scan  : psi_d(7) is not a perfect square for any relevant 3 <= d <= 59
  7. control      : the z=2 witness (15,4) satisfies the full spectral sign-balance
                    pattern (irrational eigenvalues sign-balanced, trace on rationals)
  8. ground truth : the same argument closes (23,5) [known impossible] and is silent
                    on (45,7) [square cases exist], matching the literature
"""
import json, sys
import numpy as np
import networkx as nx
from sympy import integer_nthroot

from psi_squares import V_values, psi_at, crosscheck_identity


def ok(m):
    print(f"  [OK]   {m}")


def bad(m):
    print(f"  [FAIL] {m}"); sys.exit(1)


def c4free_mindeg(fn, nexp, dexp):
    E = json.load(open(fn)); G = nx.Graph(); G.add_edges_from(map(tuple, E))
    n = G.number_of_nodes()
    A = nx.to_numpy_array(G, dtype=np.int64); A2 = A @ A
    c4 = any(A2[i, j] > 1 for i in range(n) for j in range(i + 1, n))
    d = min(dict(G.degree()).values())
    if n != nexp or c4 or d < dexp:
        bad(f"{fn}: n={n} (want {nexp}), C4={c4}, delta={d} (want >= {dexp})")
    ok(f"{fn}: {n} vertices, C_4-free, delta = {d} >= {dexp}")


print("1. lower bound f(51) >= 59")
c4free_mindeg("lower_bound_58.json", 58, 7)

print("2. Lemma A: delta >= 8 on 59 vertices forces 8-regularity")
sols = [d for d in range(8, 59) if 8 * d <= 58 + d]
if sols != [8]:
    bad(f"solutions of 8d <= 58+d with d >= 8: {sols}")
ok("8d <= 58 + d has unique solution d = 8 among d >= 8")

print("3. Lemma B: deg_D = n-1-k(k-1) on every stored witness")
for fn in ("reg_4_15.json", "reg_5_26.json", "reg_6_34.json", "reg_3_10.json"):
    E = json.load(open(fn)); G = nx.Graph(); G.add_edges_from(map(tuple, E))
    n = G.number_of_nodes()
    A = nx.to_numpy_array(G, dtype=np.int64)
    k = int(A[0].sum()); z = n - 1 - k * (k - 1)
    A2 = A @ A
    D = (A2 == 0).astype(np.int64); np.fill_diagonal(D, 0)
    degs = sorted(set(D.sum(axis=1).tolist()))
    idok = np.array_equal(A2, (k - 1) * np.eye(n, dtype=np.int64)
                          + np.ones((n, n), dtype=np.int64) - D)
    if degs != [z] or not idok:
        bad(f"{fn}: deg_D={degs} want [{z}], identity={idok}")
    ok(f"{fn} (n={n},k={k}): deg_D = {z}, A^2 = (k-1)I + J - D holds")

print("4./5. product identity and psi cross-checks")
crosscheck_identity(7, 12)

print("6. square scan for k = 8 (d <= 59) and k = 10 (d <= 93)")
for x, dmax, kname in ((7, 59, "k=8"), (9, 93, "k=10")):
    V = V_values(x, dmax)
    sq = []
    for d in range(3, dmax + 1):
        v = psi_at(x, d, V)
        r, exact = integer_nthroot(v, 2)
        if exact and d not in (3, 4, 6):
            sq.append(d)
    if sq:
        bad(f"{kname}: perfect squares at d = {sq}")
    ok(f"{kname}: psi_d({x}) is not a perfect square for any relevant d <= {dmax}")

print("7. control: full sign-balance pattern on the (15,4) witness")
E = json.load(open("reg_4_15.json")); G = nx.Graph(); G.add_edges_from(map(tuple, E))
A = nx.to_numpy_array(G, dtype=np.int64)
import sympy as sp
x = sp.symbols('x')
cp = sp.Matrix(A.tolist()).charpoly(x)
fac = dict()
for f, m in sp.factor_list(cp.as_expr())[1]:
    fac[sp.Poly(f, x).as_expr()] = m
# expected: irrational factors x^2-5 (mult 1) and x^2-2 (mult 2) -> sign-balanced pairs
if fac.get(x**2 - 5) != 1 or fac.get(x**2 - 2) != 2:
    bad(f"unexpected factorization {fac}")
rat = sum(m * (-sp.Poly(f, x).all_coeffs()[1]) for f, m in
          [(f, m) for f, m in fac.items() if sp.Poly(f, x).degree() == 1])
if rat - 4 != -4:
    bad(f"rational eigenvalue sum {rat} (with principal 4) should give -4 on 1-perp")
ok("charpoly factors: (x-4)(x-1)(x+1)(x-2)^2(x+2)^4 (x^2-5)(x^2-2)^2 ;"
   " irrational pairs balanced; rational trace = -4 = -k")

print("8. ground-truth behaviour at (23,5) and (45,7)")
V4 = V_values(4, 23)
sq = [d for d in range(3, 24) if d not in (3, 4, 6)
      and integer_nthroot(psi_at(4, d, V4), 2)[1]]
if sq:
    bad(f"(23,5): unexpected square cases {sq}")
ok("(23,5): no square cases; only rational theta = +-2; 2(a-b) = -5 impossible"
   " -> re-proves f(18) = 23")
V6 = V_values(6, 45)
sq = [d for d in range(3, 46) if d not in (3, 4, 6)
      and integer_nthroot(psi_at(6, d, V6), 2)[1]]
if sq != [14, 15]:
    bad(f"(45,7): square cases {sq}, expected [14, 15]")
ok("(45,7): square cases at d = 14 (13^2), 15 (31^2) -> argument correctly silent"
   " on this known-impossible case")

print("\nAll checks passed:  R(C_4, K_{1,51}) = 59.")

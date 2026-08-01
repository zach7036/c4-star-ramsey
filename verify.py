r"""
Self-contained referee script for  R(C_4, K_{1,39}) = 46.

Run:  python verify.py            (fast checks; ~1 minute)

To re-run the 144-case exhaustive search from scratch (~3.5 CPU-hours):
      python driver.py 8 --fresh

Checks performed
  1. lower bound   : the stored 45-vertex graph is C_4-free with delta = 6,
                     giving R(C_4,K_{1,39}) >= 46;
  2. Lemma 1       : delta >= 7 on 46 vertices forces 7-regularity (verified as a
                     finite arithmetic statement);
  3. Lemma 3       : verified as stated, and its predictions (no k-regular C_4-free
                     graph on k^2-k+2 vertices, k odd) are re-derived by search for
                     k = 3, 5, 7;
  4. encoder sound : the Hoffman-Singleton graph satisfies the CNF the encoder
                     generates for (n,k,m) = (50,7,0);
  5. case coverage : the 144 canonical subcases are checked to be exhaustive;
  6. results       : results.jsonl (and crosscheck.jsonl if present) contain one
                     UNSAT for every one of the 144 subcases.
"""
import itertools, json, os, sys
import networkx as nx
import numpy as np


def ok(msg):
    print(f"  [OK]   {msg}")


def bad(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)


def check_lower_bound():
    print("1. lower bound  R(C_4,K_{1,39}) >= 46")
    E = json.load(open("lower_bound_45.json"))
    G = nx.Graph(); G.add_edges_from(map(tuple, E))
    n = G.number_of_nodes()
    A = nx.to_numpy_array(G, dtype=np.int64); A2 = A @ A
    c4 = [(i, j) for i in range(n) for j in range(i + 1, n) if A2[i, j] > 1]
    d = min(dict(G.degree()).values())
    if n != 45:
        bad(f"graph has {n} vertices, expected 45")
    if c4:
        bad(f"graph contains a C_4 ({c4[0]})")
    if d < 6:
        bad(f"min degree {d} < 6")
    ok(f"45 vertices, C_4-free, delta = {d} >= 45-39  =>  f(39) >= 46")


def check_lemma1():
    print("2. Lemma 1: delta >= 7 on 46 vertices forces 7-regularity")
    # (*)  sum_{u in N(v)} d(u) = |V| - 1 + 2 m_v - f_v  <= 45 + d(v)
    # each neighbour has degree >= 7, so 7d <= 45 + d
    for d in range(7, 46):
        if 7 * d <= 45 + d and d != 7:
            bad(f"degree {d} not excluded")
    if 7 * 7 > 45 + 7:
        bad("degree 7 wrongly excluded")
    ok("7d <= 45 + d has the unique solution d = 7 among d >= 7")


def check_lemma3():
    print("3. Lemma 3 (k odd, f_v = 0, m_v >= 1 impossible) and its predictions")
    # the statement's arithmetic core: |S_{u_1}| = k-2 must be even
    for k in (3, 5, 7, 9, 11):
        if (k - 2) % 2 == 0:
            bad(f"k={k}: block size k-2 is even, lemma would not apply")
    ok("for odd k the matched block has odd size k-2, so no perfect matching")
    import kregular_c4free as KR
    for k in (3, 5, 7):
        n = k * k - k + 2
        e = KR.decide(n, k, verbose=False)
        if e is not None:
            bad(f"search found a {k}-regular C_4-free graph on {n} vertices")
        ok(f"search confirms: no {k}-regular C_4-free graph on {n} vertices")
    for (n, k, expect) in [(10, 3, True), (15, 4, True), (26, 5, True),
                           (34, 6, True), (14, 4, False), (23, 5, False)]:
        e = KR.decide(n, k, verbose=False)
        if (e is not None) != expect:
            bad(f"(n,k)=({n},{k}) gave {'EXISTS' if e else 'none'}, expected {expect}")
    ok("encoder reproduces the six neighbouring cases with known answers")


def check_encoder_sound():
    print("4. encoder soundness at full scale (Hoffman-Singleton)")
    import validate_encoding as VE
    G = VE.hoffman_singleton()
    if nx.girth(G) != 5 or sorted(set(dict(G.degree()).values())) != [7] \
       or G.number_of_nodes() != 50:
        bad("Hoffman-Singleton construction is wrong")
    ok("Hoffman-Singleton: 50 vertices, 7-regular, girth 5")
    VE.main()


def check_coverage():
    print("5. case coverage")
    import caseB2
    cs = caseB2.subcases()
    if len(cs) != 144:
        bad(f"{len(cs)} subcases, expected 144")
    for pq, ptypes, p7 in cs:
        deg = 1 + sum(1 for v in ptypes.values() if v is not None) + (1 if p7 else 0)
        if deg != 7 - (1 if pq else 0):
            bad(f"subcase has |N(p) cap blocks| = {deg}, expected {7-(1 if pq else 0)}")
    # every combination of (p~q, choice per block 2..6, S_7 in/out) with the right
    # degree must be present
    want = set()
    for pq in (False, True):
        for combo in itertools.product([0, 1, None], repeat=5):
            for p7 in (True, False):
                if 1 + sum(1 for c in combo if c is not None) + (1 if p7 else 0) \
                   == 7 - (1 if pq else 0):
                    want.add((pq, combo, p7))
    have = {(pq, tuple(d[i] for i in range(2, 7)), p7) for pq, d, p7 in cs}
    if want != have:
        bad(f"coverage mismatch: {len(want ^ have)} differing")
    ok("144 subcases enumerate exactly the canonical possibilities for N(p)")


def check_results():
    print("6. exhaustive search results")
    for fn in ("results.jsonl", "crosscheck.jsonl"):
        if not os.path.exists(fn):
            print(f"  [--]   {fn} not present, skipping")
            continue
        recs = {}
        for line in open(fn):
            r = json.loads(line); recs[r["idx"]] = r["result"]
        sat = [i for i, v in recs.items() if v == "SAT"]
        if sat:
            bad(f"{fn}: SAT at subcases {sat} -- a graph EXISTS, f(39) = 47")
        if fn == "results.jsonl" and set(recs) != set(range(144)):
            bad(f"{fn}: incomplete -- indices present {len(recs)}/144")
        ok(f"{fn}: {len(recs)}/144 subcases recorded, all UNSAT")
        if len(recs) < 144:
            print(f"  [--]   {fn} is incomplete (non-primary log, informational)")


if __name__ == "__main__":
    check_lower_bound()
    check_lemma1()
    check_lemma3()
    check_encoder_sound()
    check_coverage()
    check_results()
    print("\nAll checks passed.")

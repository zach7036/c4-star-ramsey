r"""
General SAT search: does a k-regular C_4-free graph on n vertices exist?

General structure (all forced, for k-regular C_4-free on n vertices):
  deg_D(v) = n - 1 - k(k-1)  is constant  =: r          (D = "no common neighbour" graph)
  m_v := #triangles through v  satisfies  ceil((k*k-n+1)/2) <= m_v <= floor(k/2)
  f_v := #vertices at distance >= 3 from v  =  n - 1 + 2 m_v - k^2
  N(v) induces a matching of size m_v; S_u = N(u)\N[v] for u in N(v) partitions the
  distance-2 set, |S_u| = k - 1 - [u matched].

We branch on m := m_{v_0} for a fixed root v_0 and fix the whole distance partition
around v_0 (a sound isomorph reduction: some vertex has each admissible m value,
so trying every m covers all graphs).
"""
import itertools, sys, time, json
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195


def admissible_m(n, k):
    lo = max(0, -(-(k * k - n + 1) // 2))
    hi = k // 2
    return [m for m in range(lo, hi + 1) if n - 1 + 2 * m - k * k >= 0]


class Inst:
    def __init__(self, n, k, m):
        self.n, self.k, self.m = n, k, m
        self.pool = IDPool(); self.cnf = CNF(); self.fixed = {}

    def setedge(self, i, j, val):
        key = frozenset((i, j))
        if key in self.fixed:
            assert self.fixed[key] == val
        self.fixed[key] = val

    def lit(self, i, j):
        key = frozenset((i, j))
        if key in self.fixed:
            return self.fixed[key]
        return self.pool.id(('e', min(i, j), max(i, j)))

    def neg(self, l):
        return (not l) if isinstance(l, bool) else -l

    def add(self, lits):
        out = []
        for l in lits:
            if l is True:
                return
            if l is False:
                continue
            out.append(l)
        if not out:
            raise ValueError("UNSAT at build")
        self.cnf.append(out)


def build(n, k, m):
    I = Inst(n, k, m)
    f = n - 1 + 2 * m - k * k                # # vertices at distance >= 3 from v0
    nbr = list(range(1, k + 1))
    matched = list(range(1, 2 * m + 1))
    free = list(range(2 * m + 1, k + 1))
    for u in nbr:
        I.setedge(0, u, True)
    pairs = {frozenset((matched[2 * t], matched[2 * t + 1])) for t in range(m)}
    for i, j in itertools.combinations(nbr, 2):
        I.setedge(i, j, frozenset((i, j)) in pairs)
    blocks, nxt = {}, k + 1
    for u in nbr:
        sz = k - 1 - (1 if u in matched else 0)
        blocks[u] = list(range(nxt, nxt + sz)); nxt += sz
    far = list(range(nxt, nxt + f)); nxt += f
    if nxt != n:
        raise ValueError(f"layout mismatch {nxt} != {n}")
    for u in nbr:
        for w in blocks[u]:
            I.setedge(u, w, True); I.setedge(0, w, False)
            for u2 in nbr:
                if u2 != u:
                    I.setedge(u2, w, False)
    for w in far:
        I.setedge(0, w, False)
        for u in nbr:
            I.setedge(u, w, False)

    # G[S_u] is a matching
    for u in nbr:
        S = blocks[u]
        for a in S:
            for b, c in itertools.combinations([x for x in S if x != a], 2):
                I.add([I.neg(I.lit(a, b)), I.neg(I.lit(a, c))])
    # no C_4
    for i, j in itertools.combinations(range(n), 2):
        others = [x for x in range(n) if x != i and x != j]
        for x, y in itertools.combinations(others, 2):
            I.add([I.neg(I.lit(i, x)), I.neg(I.lit(j, x)),
                   I.neg(I.lit(i, y)), I.neg(I.lit(j, y))])
    # degrees
    for v in range(n):
        lits, base = [], 0
        for u in range(n):
            if u == v:
                continue
            l = I.lit(v, u)
            if l is True:
                base += 1
            elif l is not False:
                lits.append(l)
        need = k - base
        if need < 0 or need > len(lits):
            raise ValueError(f"degree impossible at {v}")
        if lits:
            I.cnf.extend(CardEnc.equals(lits=lits, bound=need, vpool=I.pool,
                                        encoding=EncType.seqcounter).clauses)
        elif need:
            raise ValueError("degree impossible")
    return I


def decide(n, k, verbose=True, tlimit=None):
    ms = admissible_m(n, k)
    if verbose:
        r = n - 1 - k * (k - 1)
        print(f"n={n} k={k}: deficiency graph is {r}-regular; m in {ms}", flush=True)
    for m in ms:
        t0 = time.time()
        try:
            I = build(n, k, m)
        except ValueError as e:
            if verbose:
                print(f"  m={m}: build contradiction ({e})", flush=True)
            continue
        with Cadical195(bootstrap_with=I.cnf) as s:
            res = s.solve()
            dt = time.time() - t0
            if verbose:
                print(f"  m={m}: {'SAT' if res else 'UNSAT'}  "
                      f"({I.cnf.nv} vars, {len(I.cnf.clauses)} cls, {dt:.1f}s)", flush=True)
            if res:
                model = {l for l in s.get_model() if l > 0}
                edges = [(i, j) for i, j in itertools.combinations(range(n), 2)
                         if (I.lit(i, j) is True) or
                            (not isinstance(I.lit(i, j), bool) and I.lit(i, j) in model)]
                return edges
    return None


if __name__ == "__main__":
    cases = [(10, 3), (15, 4), (14, 4), (26, 5), (25, 5), (34, 6), (33, 6)]
    if len(sys.argv) > 2:
        cases = [(int(sys.argv[1]), int(sys.argv[2]))]
    for n, k in cases:
        t0 = time.time()
        e = decide(n, k)
        print(f"==> n={n},k={k}: {'EXISTS' if e else 'does NOT exist'} "
              f"[{time.time()-t0:.1f}s]\n", flush=True)
        if e:
            json.dump(e, open(f"reg_{k}_{n}.json", "w"))

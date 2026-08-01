r"""
CASE B for n=46, k=7.

Case A (some vertex with m_v = 2) is impossible -- short proof:
    if m_v = 2 then f_v = 2*m_v - 4 = 0, so V = {v} u N(v) u D_2(v).
    For x in S_1 = N(u_1)\N[v] (|S_1| = 5, u_1 matched with u_2 inside N(v)):
      * x has exactly one neighbour in N(v), namely u_1, so 6 neighbours in D_2;
      * x has at most one neighbour in each block S_j (two would give a C_4 through u_j);
      * x has NO neighbour in S_2 (u_1 x y u_2 would be a C_4);
      * so the 6 neighbours sit in S_1, S_3, S_4, S_5, S_6, S_7 -- one in EACH.
    Hence G[S_1] is a perfect matching on 5 vertices: impossible.

So every vertex lies in exactly 3 triangles (m_v = 3, f_v = 2) and:
    * the triangle-free edges form a perfect matching M,
    * G = (46 edge-disjoint triangles) u M,
    * the "distance >= 3" graph is 2-regular.

This script encodes Case B with:
    * the full distance partition around vertex 0 fixed,
    * the induced matchings inside every block fixed (sound isomorph reduction),
    * C_4-freeness via common-neighbour indicator variables (strong propagation),
    * the global constraint "exactly 3 triangles at every vertex".
"""
import itertools, sys, time, json
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

N, K = 46, 7
NBR = list(range(1, 8))
BLOCK = {1: list(range(8, 13)), 2: list(range(13, 18)), 3: list(range(18, 23)),
         4: list(range(23, 28)), 5: list(range(28, 33)), 6: list(range(33, 38)),
         7: list(range(38, 44))}
FAR = [44, 45]
PARTNER = {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5, 7: None}


class Enc:
    def __init__(self):
        self.pool = IDPool(); self.cnf = CNF(); self.fx = {}

    def setedge(self, i, j, val):
        k = frozenset((i, j))
        if k in self.fx:
            assert self.fx[k] == val, (i, j, val)
        self.fx[k] = val

    def e(self, i, j):
        k = frozenset((i, j))
        return self.fx.get(k, None) if k in self.fx else self.pool.id(('e', min(i, j), max(i, j)))

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
            raise ValueError("build UNSAT")
        self.cnf.append(out)

    def AND(self, a, b):
        """literal equivalent to a AND b (constants folded)."""
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        v = self.pool.id(('and', min(a, b), max(a, b)))
        self.cnf.append([-v, a]); self.cnf.append([-v, b]); self.cnf.append([v, -a, -b])
        return v


def build(pq_adjacent):
    E = Enc()
    # ---- layer structure around vertex 0
    for u in NBR:
        E.setedge(0, u, True)
    mpairs = {frozenset((1, 2)), frozenset((3, 4)), frozenset((5, 6))}
    for i, j in itertools.combinations(NBR, 2):
        E.setedge(i, j, frozenset((i, j)) in mpairs)
    for u in NBR:
        for w in BLOCK[u]:
            E.setedge(u, w, True); E.setedge(0, w, False)
            for u2 in NBR:
                if u2 != u:
                    E.setedge(u2, w, False)
    for w in FAR:
        E.setedge(0, w, False)
        for u in NBR:
            E.setedge(u, w, False)
    # ---- inside each block: matching fixed (m_{u_i} = 3 forces its size)
    for u in NBR:
        S = BLOCK[u]
        need = 3 - (1 if PARTNER[u] else 0)          # 2 for u=1..6, 3 for u=7
        pairs = {frozenset((S[2 * t], S[2 * t + 1])) for t in range(need)}
        for a, b in itertools.combinations(S, 2):
            E.setedge(a, b, frozenset((a, b)) in pairs)
    # ---- no edges between partner blocks
    for u in NBR:
        p = PARTNER[u]
        if p and u < p:
            for a in BLOCK[u]:
                for b in BLOCK[p]:
                    E.setedge(a, b, False)
    E.setedge(44, 45, pq_adjacent)

    # ---- at most one neighbour of a given vertex inside any block (C_4 through u_i)
    for u in NBR:
        S = BLOCK[u]
        outside = [x for x in range(N) if x not in S and x != u]
        for x in outside:
            for a, b in itertools.combinations(S, 2):
                E.add([E.neg(E.e(x, a)), E.neg(E.e(x, b))])

    # ---- common-neighbour variables + C_4-freeness (at most one common neighbour)
    common = {}
    for i, j in itertools.combinations(range(N), 2):
        lits = []
        for w in range(N):
            if w == i or w == j:
                continue
            c = E.AND(E.e(i, w), E.e(j, w))
            if c is not False:
                lits.append(c)
        common[(i, j)] = lits
        cl = [l for l in lits if l is not True]
        if sum(1 for l in lits if l is True) > 1:
            raise ValueError("build UNSAT: two forced common neighbours")
        if any(l is True for l in lits):
            for l in cl:
                E.cnf.append([-l])                    # all others must be false
        else:
            for a, b in itertools.combinations(cl, 2):
                E.cnf.append([-a, -b])

    # ---- degrees exactly 7
    for v in range(N):
        lits, base = [], 0
        for u in range(N):
            if u == v:
                continue
            l = E.e(v, u)
            if l is True:
                base += 1
            elif l is not False:
                lits.append(l)
        need = K - base
        if need < 0 or need > len(lits):
            raise ValueError("degree impossible")
        if lits:
            E.cnf.extend(CardEnc.equals(lits=lits, bound=need, vpool=E.pool,
                                        encoding=EncType.seqcounter).clauses)

    # ---- exactly one triangle-free edge at every vertex  (M is a perfect matching)
    # y[v][u] <=> (v~u) and (v,u have no common neighbour)
    for v in range(N):
        ys = []
        for u in range(N):
            if u == v:
                continue
            ev = E.e(v, u)
            if ev is False:
                continue
            cl = common[(min(u, v), max(u, v))]
            if any(l is True for l in cl):
                continue                              # edge lies in a triangle already
            y = E.pool.id(('y', min(u, v), max(u, v)))
            # y -> ev  and  y -> not c  for every c
            if ev is not True:
                E.cnf.append([-y, ev])
            for c in cl:
                E.cnf.append([-y, -c])
            # y <- ev and all c false
            body = ([] if ev is True else [E.neg(ev)]) + list(cl)
            E.cnf.append(body + [y])
            ys.append(y)
        E.cnf.extend(CardEnc.equals(lits=ys, bound=1, vpool=E.pool,
                                    encoding=EncType.seqcounter).clauses)
    return E


if __name__ == "__main__":
    for pq in (False, True):
        t0 = time.time()
        try:
            E = build(pq)
        except ValueError as err:
            print(f"p~q={pq}: contradiction while building ({err})", flush=True)
            continue
        print(f"p~q={pq}: {E.cnf.nv} vars, {len(E.cnf.clauses)} clauses "
              f"({time.time()-t0:.1f}s build)", flush=True)
        with Cadical195(bootstrap_with=E.cnf) as s:
            r = s.solve()
            print(f"p~q={pq}: {'SAT' if r else 'UNSAT'}  ({time.time()-t0:.1f}s)", flush=True)
            if r:
                model = {l for l in s.get_model() if l > 0}
                edges = []
                for i, j in itertools.combinations(range(N), 2):
                    l = E.e(i, j)
                    if l is True or (not isinstance(l, bool) and l in model):
                        edges.append((i, j))
                json.dump(edges, open(f"caseB_solution_pq{int(pq)}.json", "w"))
                print("SOLUTION FOUND, saved.", flush=True)
                sys.exit(0)

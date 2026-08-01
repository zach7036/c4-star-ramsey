r"""
Case B for n=46,k=7, with the block automorphisms used to canonicalise p = vertex 44.

Facts used (all proved in notes):
  * every vertex lies in exactly 3 triangles; blocks S_1..S_6 have 5 vertices and
    induce a 2-matching (so one unmatched vertex z_i), S_7 has 6 and induces a
    perfect matching;
  * p,q (the two vertices at distance 3 from the root 0) have at most one neighbour
    in each block, and p has 7-[p~q] neighbours, all inside the blocks;
  * z_i (i<=6) has NO neighbour in S_i and none in the partner block, so its 6
    non-u_i neighbours fit in only 5 blocks -> z_i is adjacent to p or to q.

Symmetry reduction:
  * swapping p,q  =>  WLOG  p ~ z_1;
  * Aut(block S_i) (i=2..6) is transitive on the 4 matched vertices and fixes z_i,
    so WLOG p's neighbour in S_i (if any) is S_i[0] or z_i;
  * Aut(block S_7) is transitive on its 6 vertices, so WLOG p's neighbour in S_7
    (if any) is vertex 38.
These groups act on disjoint vertex sets and preserve everything fixed so far.
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
Z = {i: BLOCK[i][4] for i in range(1, 7)}          # unmatched vertex of S_i


class Enc:
    def __init__(self):
        self.pool = IDPool(); self.cnf = CNF(); self.fx = {}

    def setedge(self, i, j, val):
        k = frozenset((i, j))
        if k in self.fx:
            if self.fx[k] != val:
                raise ValueError(f"conflict {i},{j}")
        self.fx[k] = val

    def e(self, i, j):
        k = frozenset((i, j))
        if k in self.fx:
            return self.fx[k]
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
            raise ValueError("build UNSAT")
        self.cnf.append(out)

    def AND(self, a, b):
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        v = self.pool.id(('and', min(a, b), max(a, b)))
        self.cnf.append([-v, a]); self.cnf.append([-v, b]); self.cnf.append([v, -a, -b])
        return v


def build(pq_adjacent, ptypes, p7):
    """ptypes: dict i -> 0 (S_i[0]) / 1 (z_i) / None (no neighbour of p in S_i), i=2..6
       p7: True if p has its S_7 neighbour (which is then 38)."""
    E = Enc()
    for u in NBR:
        E.setedge(0, u, True)
    mp = {frozenset((1, 2)), frozenset((3, 4)), frozenset((5, 6))}
    for i, j in itertools.combinations(NBR, 2):
        E.setedge(i, j, frozenset((i, j)) in mp)
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
    for u in NBR:
        S = BLOCK[u]
        need = 3 - (1 if PARTNER[u] else 0)
        pairs = {frozenset((S[2 * t], S[2 * t + 1])) for t in range(need)}
        for a, b in itertools.combinations(S, 2):
            E.setedge(a, b, frozenset((a, b)) in pairs)
    for u in NBR:
        pr = PARTNER[u]
        if pr and u < pr:
            for a in BLOCK[u]:
                for b in BLOCK[pr]:
                    E.setedge(a, b, False)
    E.setedge(44, 45, pq_adjacent)

    # --- canonicalised neighbourhood of p = 44
    for w in BLOCK[1]:
        E.setedge(44, w, w == Z[1])                # WLOG p ~ z_1
    for i in range(2, 7):
        S = BLOCK[i]
        tgt = None if ptypes[i] is None else (S[0] if ptypes[i] == 0 else Z[i])
        for w in S:
            E.setedge(44, w, w == tgt)
    for w in BLOCK[7]:
        E.setedge(44, w, p7 and w == 38)

    # --- at most one neighbour inside a block
    for u in NBR:
        S = BLOCK[u]
        for x in [t for t in range(N) if t not in S and t != u]:
            for a, b in itertools.combinations(S, 2):
                E.add([E.neg(E.e(x, a)), E.neg(E.e(x, b))])

    # --- common neighbours + C_4-freeness
    common = {}
    for i, j in itertools.combinations(range(N), 2):
        lits = []
        for w in range(N):
            if w in (i, j):
                continue
            c = E.AND(E.e(i, w), E.e(j, w))
            if c is not False:
                lits.append(c)
        if sum(1 for l in lits if l is True) > 1:
            raise ValueError("two forced common neighbours")
        cl = [l for l in lits if l is not True]
        if any(l is True for l in lits):
            for l in cl:
                E.cnf.append([-l])
            common[(i, j)] = [True]
        else:
            for a, b in itertools.combinations(cl, 2):
                E.cnf.append([-a, -b])
            common[(i, j)] = cl

    # --- degrees
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
            raise ValueError(f"degree impossible at {v}")
        if lits:
            E.cnf.extend(CardEnc.equals(lits=lits, bound=need, vpool=E.pool,
                                        encoding=EncType.seqcounter).clauses)
        elif need:
            raise ValueError("degree impossible")

    # --- exactly one triangle-free edge per vertex
    for v in range(N):
        ys = []
        for u in range(N):
            if u == v:
                continue
            ev = E.e(v, u)
            if ev is False:
                continue
            cl = common[(min(u, v), max(u, v))]
            if cl and cl[0] is True:
                continue
            y = E.pool.id(('y', min(u, v), max(u, v)))
            if ev is not True:
                E.cnf.append([-y, ev])
            for c in cl:
                E.cnf.append([-y, -c])
            E.cnf.append(([] if ev is True else [E.neg(ev)]) + list(cl) + [y])
            ys.append(y)
        if not ys:
            raise ValueError(f"no possible M-edge at {v}")
        E.cnf.extend(CardEnc.equals(lits=ys, bound=1, vpool=E.pool,
                                    encoding=EncType.seqcounter).clauses)
    return E


def subcases():
    """Enumerate the canonical possibilities for N(p)."""
    out = []
    for pq in (False, True):
        ndeg = 7 - (1 if pq else 0)      # neighbours of p inside the blocks
        # p ~ z_1 always; choose for i=2..6 one of {0,1,None} and S_7 in/out
        for combo in itertools.product([0, 1, None], repeat=5):
            for p7 in (True, False):
                cnt = 1 + sum(1 for c in combo if c is not None) + (1 if p7 else 0)
                if cnt != ndeg:
                    continue
                out.append((pq, dict(zip(range(2, 7), combo)), p7))
    return out


if __name__ == "__main__":
    cases = subcases()
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else len(cases)
    print(f"{len(cases)} canonical subcases; running [{lo},{hi})", flush=True)
    T0 = time.time()
    for idx in range(lo, min(hi, len(cases))):
        pq, ptypes, p7 = cases[idx]
        t0 = time.time()
        try:
            E = build(pq, ptypes, p7)
        except ValueError as err:
            print(f"[{idx}] pq={int(pq)} {ptypes} S7={int(p7)}: build-contradiction ({err}) "
                  f"[{time.time()-t0:.1f}s]", flush=True)
            continue
        with Cadical195(bootstrap_with=E.cnf) as s:
            r = s.solve()
            print(f"[{idx}] pq={int(pq)} {[ptypes[i] for i in range(2,7)]} S7={int(p7)}: "
                  f"{'SAT' if r else 'UNSAT'}  {len(E.cnf.clauses)}cls  "
                  f"[{time.time()-t0:.1f}s, total {time.time()-T0:.0f}s]", flush=True)
            if r:
                model = {l for l in s.get_model() if l > 0}
                edges = [(i, j) for i, j in itertools.combinations(range(N), 2)
                         if E.e(i, j) is True or
                            (not isinstance(E.e(i, j), bool) and E.e(i, j) in model)]
                json.dump(edges, open(f"SOLUTION_{idx}.json", "w"))
                print("*** SOLUTION FOUND ***", flush=True)
                sys.exit(0)
    print(f"range [{lo},{hi}) done in {time.time()-T0:.0f}s", flush=True)

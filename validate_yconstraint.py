r"""
Unit test for the Case-B-specific machinery: the common-neighbour variables and the
"exactly t triangle-free edges at every vertex" constraint.

We run the identical code path on a graph whose answer we know: the Hoffman-Singleton
graph is triangle-free and 7-regular, so EVERY one of its 7 edges at a vertex lies in no
triangle. The encoder must therefore accept t = 7 and reject t = 1 and t = 6.

Also tested on a graph with triangles: the 6-regular C_4-free graph on 34 vertices found
earlier, whose per-vertex triangle-free-edge counts are computed directly.
"""
import itertools, json, sys
import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195
from caseB2 import Enc
from validate_encoding import hoffman_singleton


def encode_and_test(G, t_per_vertex):
    """Build common-neighbour vars + 'exactly t triangle-free edges' on a FIXED graph."""
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    E = Enc()
    for i, j in itertools.combinations(range(n), 2):
        E.setedge(i, j, G.has_edge(nodes[i], nodes[j]))
    common = {}
    ok = True
    for i, j in itertools.combinations(range(n), 2):
        lits = []
        for w in range(n):
            if w in (i, j):
                continue
            c = E.AND(E.e(i, w), E.e(j, w))
            if c is not False:
                lits.append(c)
        if sum(1 for l in lits if l is True) > 1:
            return None                      # not C_4-free
        common[(i, j)] = [True] if any(l is True for l in lits) else []
    for v in range(n):
        ys = []
        for u in range(n):
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
            E.cnf.append(([] if ev is True else [E.neg(ev)]) + [y])
            ys.append(y)
        want = t_per_vertex(v) if callable(t_per_vertex) else t_per_vertex
        if not ys:
            if want != 0:
                return False
            continue
        if want > len(ys):
            return False
        E.cnf.extend(CardEnc.equals(lits=ys, bound=want, vpool=E.pool,
                                    encoding=EncType.seqcounter).clauses)
    with Cadical195(bootstrap_with=E.cnf) as s:
        return s.solve()


def truth(G):
    """Direct computation: #edges at v lying in no triangle."""
    nodes = sorted(G.nodes())
    out = {}
    for i, v in enumerate(nodes):
        c = 0
        for u in G[v]:
            if not any(G.has_edge(w, u) for w in G[v] if w != u):
                c += 1
        out[i] = c
    return out


if __name__ == "__main__":
    HS = hoffman_singleton()
    tr = truth(HS)
    print("Hoffman-Singleton triangle-free-edge counts (direct):",
          sorted(set(tr.values())))
    for t in (7, 6, 1):
        r = encode_and_test(HS, t)
        expect = (t == 7)
        print(f"  encoder with 'exactly {t}' -> {r}   (expected {expect})   "
              f"{'OK' if r == expect else 'MISMATCH'}")

    E34 = json.load(open("reg_6_34.json"))
    G34 = nx.Graph(); G34.add_edges_from(map(tuple, E34))
    tr34 = truth(G34)
    print("\n34-vertex 6-regular C4-free graph, counts (direct):",
          sorted(set(tr34.values())))
    r = encode_and_test(G34, lambda v: tr34[v])
    print(f"  encoder with the true per-vertex counts -> {r} (expected True) "
          f"{'OK' if r else 'MISMATCH'}")
    r = encode_and_test(G34, lambda v: tr34[v] + 1 if v == 0 else tr34[v])
    print(f"  encoder with one count perturbed        -> {r} (expected False) "
          f"{'OK' if r is False else 'MISMATCH'}")

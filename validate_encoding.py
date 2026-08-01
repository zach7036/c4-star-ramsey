r"""
Soundness test of the SAT encoding at full scale.

The Hoffman-Singleton graph is 7-regular, girth 5 (so C_4-free), on 50 vertices, and
every vertex has m_v = 0, f_v = 0 -- exactly the (n,k,m) = (50,7,0) branch of the
encoding.  We relabel it into the layout the encoder fixes and check that the resulting
assignment satisfies EVERY clause of the generated CNF.  If it does, the encoding does
not exclude legitimate graphs.
"""
import itertools
import numpy as np
import networkx as nx
import kregular_c4free as KR


def hoffman_singleton():
    G = nx.Graph()
    P = lambda h, i: ('P', h, i)
    Q = lambda j, k: ('Q', j, k)
    for h in range(5):
        for i in range(5):
            G.add_edge(P(h, i), P(h, (i + 1) % 5))
    for j in range(5):
        for k in range(5):
            G.add_edge(Q(j, k), Q(j, (k + 2) % 5))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                G.add_edge(P(h, i), Q(j, (h * j + i) % 5))
    return G


def relabel_to_layout(G, n, k, m):
    """Relabel G so that it matches the fixed layout used by kregular_c4free.build."""
    assert m == 0
    nodes = list(G.nodes())
    v = nodes[0]
    nbrs = sorted(G[v], key=str)
    assert len(nbrs) == k
    lab = {v: 0}
    for idx, u in enumerate(nbrs, start=1):
        lab[u] = idx
    nxt = k + 1
    for idx, u in enumerate(nbrs, start=1):
        S = sorted([w for w in G[u] if w != v and w not in nbrs], key=str)
        assert len(S) == k - 1, (len(S), k - 1)
        for w in S:
            assert w not in lab, "blocks not disjoint"
            lab[w] = nxt; nxt += 1
    assert nxt == n, (nxt, n)
    return nx.relabel_nodes(G, lab)


def main():
    G = hoffman_singleton()
    n = G.number_of_nodes()
    degs = sorted(set(dict(G.degree()).values()))
    A = nx.to_numpy_array(G, dtype=np.int64); A2 = A @ A
    c4 = any(A2[i, j] > 1 for i in range(n) for j in range(i + 1, n))
    print(f"Hoffman-Singleton: n={n}, degrees={degs}, girth={nx.girth(G)}, C4-free={not c4}")

    H = relabel_to_layout(G, 50, 7, 0)
    E = set(frozenset(e) for e in H.edges())

    I = KR.build(50, 7, 0)
    print(f"encoding for (n,k,m)=(50,7,0): {I.cnf.nv} vars, {len(I.cnf.clauses)} clauses")

    # assignment: edge variables from H; all auxiliary (cardinality) vars are existentially
    # quantified, so use the SAT solver with the edge variables fixed as assumptions.
    from pysat.solvers import Cadical195
    assumptions = []
    bad_fixed = 0
    for i, j in itertools.combinations(range(50), 2):
        want = frozenset((i, j)) in E
        lit = I.lit(i, j)
        if isinstance(lit, bool):
            if lit != want:
                bad_fixed += 1
        else:
            assumptions.append(lit if want else -lit)
    print(f"hard-coded layout entries contradicting H: {bad_fixed}")
    with Cadical195(bootstrap_with=I.cnf) as s:
        ok = s.solve(assumptions=assumptions)
    print(f"CNF satisfied by the Hoffman-Singleton assignment: {ok}")
    if bad_fixed == 0 and ok:
        print("ENCODING SOUND at full scale: it accepts a genuine 7-regular C4-free "
              "graph on 50 vertices.")
    else:
        print("ENCODING PROBLEM -- investigate.")


if __name__ == "__main__":
    main()

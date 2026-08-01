"""
How small an induced subgraph of ER_7 can keep minimum degree >= 7?
(This is the standard construction route for lower bounds on f(n)=R(C_4,K_{1,n}).)

Recall: f(n) > N  iff  there is a C_4-free graph on N vertices with delta >= N-n.
So an induced subgraph of ER_7 on N vertices with delta >= 7 gives f(N-7) >= N+1.

Also: for N <= 48, delta >= 7 forces 7-regularity (shown separately), so the
'delta >= 7' and '7-regular' questions coincide there.
"""
import networkx as nx
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153


def er_polarity(q):
    pts = [(1, a, b) for a in range(q) for b in range(q)]
    pts += [(0, 1, b) for b in range(q)]
    pts += [(0, 0, 1)]
    G = nx.Graph(); G.add_nodes_from(range(len(pts)))
    for i, p in enumerate(pts):
        for j, r in enumerate(pts):
            if i < j and sum(x * y for x, y in zip(p, r)) % q == 0:
                G.add_edge(i, j)
    return G


def min_deg_subgraph(G, keep, mindeg):
    """Is there an induced subgraph on `keep` vertices with min degree >= mindeg?"""
    pool = IDPool()
    x = {v: pool.id(('x', v)) for v in G}          # x[v] = 1 <=> v is KEPT
    cnf = CNF()
    for v in G:
        nb = [x[u] for u in G[v]]
        # x[v] -> at least `mindeg` kept neighbours
        enc = CardEnc.atleast(lits=nb, bound=mindeg, vpool=pool, encoding=EncType.seqcounter)
        for cl in enc.clauses:
            cnf.append(cl + [-x[v]])
    cnf.extend(CardEnc.equals(lits=list(x.values()), bound=keep,
                              vpool=pool, encoding=EncType.seqcounter).clauses)
    with Cadical153(bootstrap_with=cnf) as s:
        if not s.solve():
            return None
        m = set(l for l in s.get_model() if l > 0)
        return [v for v in G if x[v] in m]


if __name__ == "__main__":
    G = er_polarity(7)
    print("ER_7:", G.number_of_nodes(), "vertices; degree-7 (absolute) points:",
          sum(1 for v in G if G.degree(v) == 7))
    print()
    print(" keep | delta>=7 induced subgraph of ER_7?")
    for keep in range(57, 43, -1):
        S = min_deg_subgraph(G, keep, 7)
        if S is None:
            print(f"  {keep:3d} | NO")
        else:
            H = G.subgraph(S)
            degs = sorted(set(dict(H.degree()).values()))
            print(f"  {keep:3d} | YES   degrees {degs}   =>  f({keep-7}) >= {keep+1}")

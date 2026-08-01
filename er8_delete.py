r"""
Independent lower-bound witness for f(51) >= 59: find a C_4-free graph on 58 vertices
with min degree >= 7 by deleting 15 vertices from the polarity graph ER_8 of PG(2,8).

GF(8) = GF(2)[t]/(t^3 + t + 1), elements encoded as bit-vectors 0..7.
ER_8: 73 points, edges u~v iff u.v = 0; degrees 9 (non-absolute) and 8 (absolute).
"""
import itertools, json
import networkx as nx


def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 8:
            a ^= 0b1011          # t^3 = t + 1
        b >>= 1
    return r


def er8():
    pts = [(1, a, b) for a in range(8) for b in range(8)]
    pts += [(0, 1, b) for b in range(8)]
    pts += [(0, 0, 1)]
    assert len(pts) == 73
    G = nx.Graph(); G.add_nodes_from(range(73))
    for i, p in enumerate(pts):
        for j, r in enumerate(pts):
            if i < j:
                dot = gf_mul(p[0], r[0]) ^ gf_mul(p[1], r[1]) ^ gf_mul(p[2], r[2])
                if dot == 0:
                    G.add_edge(i, j)
    return G


if __name__ == "__main__":
    import numpy as np
    from er7_mindeg import min_deg_subgraph
    G = er8()
    degs = sorted(set(dict(G.degree()).values()))
    A = nx.to_numpy_array(G, dtype=np.int64); A2 = A @ A
    c4 = any(A2[i, j] > 1 for i in range(73) for j in range(i + 1, 73))
    print(f"ER_8: 73 vertices, degrees {degs}, C4-free={not c4}", flush=True)
    for keep in (58, 59, 60):
        S = min_deg_subgraph(G, keep, 7)
        if S is None:
            print(f"keep {keep}: UNSAT", flush=True)
        else:
            H = G.subgraph(S).copy()
            A = nx.to_numpy_array(H, dtype=np.int64); A2 = A @ A
            n = len(S)
            c4 = any(A2[i, j] > 1 for i in range(n) for j in range(i + 1, n))
            md = min(dict(H.degree()).values())
            print(f"keep {keep}: SAT  delta={md}  C4-free={not c4}  "
                  f"=> f({keep-7}) >= {keep+1}", flush=True)
            if keep == 58:
                json.dump(sorted(map(list, H.edges())), open("lower_bound_58.json", "w"))
                print("   witness saved to lower_bound_58.json  (f(51) >= 59)", flush=True)

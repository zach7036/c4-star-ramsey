r"""
Verify the 5th-moment algebra on REAL k-regular C_4-free graphs.

General identity for k-regular C_4-free G on n vertices, D = deficiency graph
(z-regular, z = n-1-k(k-1)),  A^2 = (k-1)I + J - D,  P = (k-1)I - D,  PJ = (k-1-z)J:

    A^4 = P^2 + [2(k-1-z) + n] J
    A^5 = A P^2 + k[2(k-1-z) + n] J
    tr(A^5) = -2(k-1) tr(AD) + tr(AD^2) + k n [2(k-1-z) + n]
    sum_{i>=2} theta_i^5 = tr(A^5) - k^5

and  tr(AD)  = 2 * #(edges lying in no triangle)
     tr(AD^2)= 2 * sum_{uv in E} |N_D(u) cap N_D(v)|.

Specialised to n=46, k=7, z=3, T=46 (the branch Lemma 3 forces):
     sum theta^5 = tr(AD^2) - 615,
     N_D(u) cap N_D(v) = F_u cap F_v   for uv in E   (F_x = the 2 vertices at distance 3),
     sum_{uv in E} |F_u cap F_v| = #{w : the two vertices at distance 3 from w are adjacent}
                                 =: kappa  in [0, 46]
     =>  sum theta^5 = 2*kappa - 615  in [-615, -523].
"""
import itertools
import numpy as np
import networkx as nx


def deficiency(A):
    n = A.shape[0]
    A2 = A @ A
    D = ((A2 == 0).astype(np.int64))
    np.fill_diagonal(D, 0)
    return D


def check(G, name):
    n = G.number_of_nodes()
    A = nx.to_numpy_array(G, dtype=np.int64)
    k = int(A[0].sum())
    if any(int(A[i].sum()) != k for i in range(n)):
        return
    A2 = A @ A
    if any(A2[i, j] > 1 for i in range(n) for j in range(i + 1, n)):
        print(f"{name}: not C_4-free, skipped"); return
    D = deficiency(A)
    z = n - 1 - k * (k - 1)
    if sorted(set(D.sum(axis=1).tolist())) != [z]:
        print(f"{name}: deficiency graph not {z}-regular!"); return

    trA5 = int(round(np.trace(np.linalg.matrix_power(A, 5))))
    theta5 = trA5 - k ** 5
    trAD = int(np.trace(A @ D))
    trAD2 = int(np.trace(A @ D @ D))
    pred = -2 * (k - 1) * trAD + trAD2 + k * n * (2 * (k - 1 - z) + n) - k ** 5

    # combinatorial readings
    tri_free = sum(1 for u, v in G.edges()
                   if not any(A[u, w] and A[v, w] for w in range(n)))
    trAD_comb = 2 * tri_free
    cross = 2 * sum(int((D[u] * D[v]).sum()) for u, v in G.edges())

    okA = (theta5 == pred)
    okB = (trAD == trAD_comb)
    okC = (trAD2 == cross)
    print(f"{name}: n={n} k={k} z={z} | sum th^5 = {theta5:>8}  predicted {pred:>8}  "
          f"{'OK' if okA else 'MISMATCH'} | tr(AD) {'OK' if okB else 'BAD'} "
          f"| tr(AD^2) {'OK' if okC else 'BAD'}")
    return okA and okB and okC


def hoffman_singleton():
    G = nx.Graph()
    for h in range(5):
        for i in range(5):
            G.add_edge(('P', h, i), ('P', h, (i + 1) % 5))
    for j in range(5):
        for kk in range(5):
            G.add_edge(('Q', j, kk), ('Q', j, (kk + 2) % 5))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                G.add_edge(('P', h, i), ('Q', j, (h * j + i) % 5))
    return nx.convert_node_labels_to_integers(G)


if __name__ == "__main__":
    import json
    tests = [(nx.petersen_graph(), "Petersen (10,3)"),
             (nx.heawood_graph(), "Heawood (14,3)"),
             (hoffman_singleton(), "Hoffman-Singleton (50,7)")]
    for fn, nm in [("reg_4_15.json", "found (15,4)"), ("reg_5_26.json", "found (26,5)"),
                   ("reg_6_34.json", "found (34,6)")]:
        try:
            E = json.load(open(fn)); G = nx.Graph(); G.add_edges_from(map(tuple, E))
            tests.append((G, nm))
        except FileNotFoundError:
            pass
    allok = True
    for G, nm in tests:
        r = check(G, nm)
        allok = allok and (r is not False)
    print()
    print("Specialisation to n=46,k=7,z=3,T=46:")
    n, k, z = 46, 7, 3
    const = k * n * (2 * (k - 1 - z) + n) - k ** 5
    print(f"  k*n*[2(k-1-z)+n] - k^5 = {k}*{n}*[{2*(k-1-z)}+{n}] - {k**5} = {const}")
    print(f"  tr(AD) = 2*23 = 46  (M is a perfect matching of triangle-free edges)")
    print(f"  => sum theta^5 = -2*6*46 + tr(AD^2) + {const} = tr(AD^2) - 615"
          f"   [check: {-2*(k-1)*46 + const} ]")
    print(f"  tr(AD^2) = 2*kappa, kappa in [0,46]  =>  sum theta^5 in [-615, -523]")

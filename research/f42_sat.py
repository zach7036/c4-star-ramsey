#!/usr/bin/env python3
"""Exact SAT search for a 49-vertex C4-free graph with minimum degree 7.

A counterexample to R(C4,K1,42)=49 must have degrees 7/8. Choosing an
8-valent root fixes a radius-two partition into eight five-vertex blocks.
This script exhausts all canonical distributions of the remaining 8-valent
vertices and all graph completions compatible with that partition.

Each case is an exact CNF instance. SAT produces and independently verifies
an explicit graph. UNSAT eliminates the corresponding isomorphism class.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import time
from pathlib import Path
from typing import Iterable, Sequence

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

PAIR = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6}
N = 49


def sv(block: int, pos: int) -> int:
    return 9 + 5 * block + pos


def canonical_orbits() -> list[tuple[int, ...]]:
    """One high-vertex distribution per Aut(4K2)-orbit."""
    out: list[tuple[int, ...]] = []
    for total in (0, 2, 4, 6, 8):
        reps: set[tuple[tuple[int, int], ...]] = set()
        for vec in itertools.product(range(3), repeat=8):
            if sum(vec) != total:
                continue
            pairs = tuple(sorted(tuple(sorted(vec[2 * i : 2 * i + 2])) for i in range(4)))
            reps.add(pairs)
        for pairs in sorted(reps):
            out.append(tuple(x for p in pairs for x in p))
    assert len(out) == 44
    return out


class Instance:
    def __init__(self, hvec: Sequence[int]) -> None:
        self.hvec = tuple(hvec)
        self.pool = IDPool()
        self.cnf = CNF()
        self.fixed: dict[tuple[int, int], bool] = {}
        self.edge_var: dict[tuple[int, int], int] = {}
        self.zvars: dict[int, tuple[int, ...]] = {}
        self.high = {sv(i, a) for i, h in enumerate(hvec) for a in range(h)}
        self.stats: collections.Counter[str] = collections.Counter()
        self._init_variables_and_fixed_edges()

    @staticmethod
    def key(u: int, v: int) -> tuple[int, int]:
        if u == v:
            raise ValueError("loop")
        return (u, v) if u < v else (v, u)

    def set_fixed(self, u: int, v: int, value: bool) -> None:
        k = self.key(u, v)
        old = self.fixed.get(k)
        if old is not None and old != value:
            raise ValueError(f"conflicting fixed edge {k}")
        self.fixed[k] = value

    def _init_variables_and_fixed_edges(self) -> None:
        # Root and its eight neighbours.
        for i in range(8):
            self.set_fixed(0, 1 + i, True)
        for i, j in itertools.combinations(range(1, 9), 2):
            self.set_fixed(i, j, (i - 1) // 2 == (j - 1) // 2 and abs(i - j) == 1)

        # Radius-two blocks: u_i is adjacent to all five vertices of S_i and
        # to no other radius-two vertex.
        for i in range(8):
            for a in range(5):
                x = sv(i, a)
                self.set_fixed(0, x, False)
                for j in range(8):
                    self.set_fixed(1 + j, x, j == i)

        # Cross-block edge variables. Partner blocks have no edges.
        for i in range(8):
            for j in range(i + 1, 8):
                if PAIR[i] == j:
                    for a in range(5):
                        for b in range(5):
                            self.set_fixed(sv(i, a), sv(j, b), False)
                    continue
                for a in range(5):
                    for b in range(5):
                        e = self.key(sv(i, a), sv(j, b))
                        self.edge_var[e] = self.pool.id(("e",) + e)

        # Canonical internal matching in each block. This is a sound orbit
        # reduction under the within-block symmetric group.
        for i, h in enumerate(self.hvec):
            for a, b in itertools.combinations(range(5), 2):
                self.set_fixed(sv(i, a), sv(i, b), False)
            if h == 0:
                z1 = self.pool.id(("z1", i))
                z2 = self.pool.id(("z2", i))
                self.zvars[i] = (z1, z2)
                self.fixed.pop(self.key(sv(i, 0), sv(i, 1)))
                self.fixed.pop(self.key(sv(i, 2), sv(i, 3)))
                self.edge_var[self.key(sv(i, 0), sv(i, 1))] = z1
                self.edge_var[self.key(sv(i, 2), sv(i, 3))] = z2
                self.add_clause([-z2, z1])
            elif h == 1:
                z2 = self.pool.id(("z2", i))
                self.zvars[i] = (z2,)
                self.fixed.pop(self.key(sv(i, 0), sv(i, 1)))
                self.set_fixed(sv(i, 0), sv(i, 1), True)
                self.fixed.pop(self.key(sv(i, 2), sv(i, 3)))
                self.edge_var[self.key(sv(i, 2), sv(i, 3))] = z2
            elif h == 2:
                self.fixed.pop(self.key(sv(i, 0), sv(i, 2)))
                self.fixed.pop(self.key(sv(i, 1), sv(i, 3)))
                self.set_fixed(sv(i, 0), sv(i, 2), True)
                self.set_fixed(sv(i, 1), sv(i, 3), True)
            else:
                raise ValueError(h)

        # Any two degree-8 vertices are nonadjacent.
        for x, y in itertools.combinations(sorted(self.high), 2):
            lit = self.lit(x, y)
            if lit is True:
                raise ValueError("canonical pattern joined two high vertices")
            if isinstance(lit, int):
                self.add_clause([-lit])

    def lit(self, u: int, v: int) -> bool | int:
        k = self.key(u, v)
        if k in self.fixed:
            return self.fixed[k]
        return self.edge_var.get(k, False)

    @staticmethod
    def neg(lit: bool | int) -> bool | int:
        return (not lit) if isinstance(lit, bool) else -lit

    def add_clause(self, lits: Iterable[bool | int]) -> None:
        out: list[int] = []
        seen: set[int] = set()
        for lit in lits:
            if lit is True:
                return
            if lit is False:
                continue
            if -lit in seen:
                return
            if lit not in seen:
                seen.add(lit)
                out.append(lit)
        if not out:
            raise ValueError("CNF contradiction during construction")
        self.cnf.append(out)

    def add_exactly(self, lits: Iterable[bool | int], target: int) -> None:
        vars_: list[int] = []
        fixed_true = 0
        for lit in lits:
            if lit is True:
                fixed_true += 1
            elif lit is False:
                continue
            else:
                vars_.append(lit)
        target -= fixed_true
        if target < 0 or target > len(vars_):
            raise ValueError("impossible cardinality")
        if not vars_:
            if target:
                raise ValueError("impossible empty cardinality")
            return
        enc = CardEnc.equals(
            lits=vars_, bound=target, vpool=self.pool, encoding=EncType.seqcounter
        )
        self.cnf.extend(enc.clauses)

    def add_structure(self) -> None:
        # Every cross-block bipartite graph is a matching. These clauses are
        # implied by C4-freeness but substantially strengthen propagation.
        for i in range(8):
            for j in range(i + 1, 8):
                if PAIR[i] == j:
                    continue
                for a in range(5):
                    row = [self.lit(sv(i, a), sv(j, b)) for b in range(5)]
                    for x, y in itertools.combinations(row, 2):
                        self.add_clause([self.neg(x), self.neg(y)])
                for b in range(5):
                    col = [self.lit(sv(i, a), sv(j, b)) for a in range(5)]
                    for x, y in itertools.combinations(col, 2):
                        self.add_clause([self.neg(x), self.neg(y)])
        self.stats["matching_clauses"] = len(self.cnf.clauses)

        # Every S vertex has Q-degree 6 or 7 according to its fixed status.
        for i, h in enumerate(self.hvec):
            for a in range(5):
                x = sv(i, a)
                incident = [self.lit(x, y) for y in range(9, N) if y != x]
                self.add_exactly(incident, 6 + (a < h))
        self.stats["after_degree_clauses"] = len(self.cnf.clauses)

        # Exact C4 exclusion in the full 49-vertex graph.
        c4_candidates = 0
        for a, b, c, d in itertools.combinations(range(N), 4):
            for cyc in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                edges = [self.lit(cyc[t], cyc[(t + 1) % 4]) for t in range(4)]
                if any(e is False for e in edges):
                    continue
                c4_candidates += 1
                self.add_clause([self.neg(e) for e in edges])
        self.stats["c4_candidates"] = c4_candidates
        self.stats["total_clauses"] = len(self.cnf.clauses)
        self.stats["variables"] = self.pool.top

    def reconstruct(self, model: Sequence[int]) -> list[tuple[int, int]]:
        positive = {x for x in model if x > 0}
        edges: list[tuple[int, int]] = []
        for u, v in itertools.combinations(range(N), 2):
            lit = self.lit(u, v)
            if lit is True or (isinstance(lit, int) and lit in positive):
                edges.append((u, v))
        return edges


def verify(edges: Sequence[tuple[int, int]]) -> dict[str, object]:
    adj = [set() for _ in range(N)]
    for u, v in edges:
        if not (0 <= u < v < N):
            raise AssertionError((u, v))
        adj[u].add(v)
        adj[v].add(u)
    degrees = [len(x) for x in adj]
    bad_pairs = []
    for u, v in itertools.combinations(range(N), 2):
        common = adj[u] & adj[v]
        if len(common) > 1:
            bad_pairs.append((u, v, sorted(common)))
    if min(degrees) < 7 or bad_pairs:
        raise AssertionError({"degrees": degrees, "bad_pairs": bad_pairs[:5]})
    return {
        "n": N,
        "m": len(edges),
        "degree_counts": dict(sorted(collections.Counter(degrees).items())),
        "minimum_degree": min(degrees),
        "maximum_degree": max(degrees),
        "c4_free": True,
    }


def solve_case(case_index: int, solver_name: str | None = None) -> dict[str, object]:
    orbits = canonical_orbits()
    hvec = orbits[case_index]
    start = time.time()
    inst = Instance(hvec)
    inst.add_structure()
    build_seconds = time.time() - start

    candidates = [solver_name] if solver_name else ["cadical195", "cadical153", "glucose42"]
    last_error: Exception | None = None
    solver_used = ""
    result: bool | None = None
    model: list[int] | None = None
    solve_start = time.time()
    for name in candidates:
        if not name:
            continue
        try:
            with Solver(name=name, bootstrap_with=inst.cnf.clauses) as solver:
                solver_used = name
                result = solver.solve()
                if result:
                    model = solver.get_model()
            break
        except Exception as exc:  # pragma: no cover
            last_error = exc
    if result is None:
        raise RuntimeError(f"no requested SAT solver is available: {last_error}")
    solve_seconds = time.time() - solve_start

    payload: dict[str, object] = {
        "case": case_index,
        "case_count": len(orbits),
        "hvec": list(hvec),
        "remaining_degree8_vertices": sum(hvec),
        "status": "SAT" if result else "UNSAT",
        "solver": solver_used,
        "build_seconds": build_seconds,
        "solve_seconds": solve_seconds,
        "stats": dict(inst.stats),
    }
    if result:
        assert model is not None
        edges = inst.reconstruct(model)
        payload["verification"] = verify(edges)
        payload["edges"] = [list(e) for e in edges]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, required=True)
    parser.add_argument("--solver")
    parser.add_argument("--out-dir", default="f42-results")
    args = parser.parse_args()
    orbits = canonical_orbits()
    if not 0 <= args.case < len(orbits):
        parser.error(f"case must be in 0..{len(orbits)-1}")
    payload = solve_case(args.case, args.solver)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"case_{args.case:02d}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, sort_keys=True))
    print(f"RESULT_FILE={path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Exact SAT reduction for the open cycle--star Ramsey case R(C4,K1,42).

A counterexample to R(C4,K1,42)=49 would be a C4-free graph on 49
vertices with minimum degree at least 7. Elementary counting forces degrees
7/8 and at least one degree-8 vertex. Rooting at one such vertex reduces the
problem to 44 isomorphism classes; this program generates and solves one class.

The encoding is deliberately redundant: it contains the defining degree and
C4 constraints plus consequences for every degree-8 vertex. Redundancy is used
only to accelerate solving; it does not remove valid graphs.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterable

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

N = 49
PAIR = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6}


def sv(block: int, pos: int) -> int:
    return 9 + 5 * block + pos


def canonical_orbits() -> list[tuple[tuple[int, int], ...]]:
    """Return the 44 orbits of high-vertex counts under S2 wr S4."""
    out: set[tuple[tuple[int, int], ...]] = set()
    for h in itertools.product(range(3), repeat=8):
        if sum(h) not in (0, 2, 4, 6, 8):
            continue
        pairs = tuple(sorted(tuple(sorted(h[2 * i : 2 * i + 2])) for i in range(4)))
        out.add(pairs)
    ans = sorted(out, key=lambda x: (sum(sum(p) for p in x), x))
    assert len(ans) == 44
    return ans


def hvec_for_case(case: int) -> list[int]:
    orbits = canonical_orbits()
    if not 0 <= case < len(orbits):
        raise ValueError(f"case must be in [0,{len(orbits)-1}]")
    return [x for pair in orbits[case] for x in pair]


class Instance:
    def __init__(self, case: int):
        self.case = case
        self.hvec = hvec_for_case(case)
        self.pool = IDPool()
        self.cnf = CNF()
        self.cross: dict[tuple[int, int], int] = {}
        self.zvars: dict[int, tuple[int, ...]] = {}
        self.forced: set[tuple[int, int]] = set()
        self.high = {0}
        self._make_variables()
        self._make_forced_edges()
        self._encode()

    @staticmethod
    def _key(u: int, v: int) -> tuple[int, int]:
        if u == v:
            raise ValueError("loop")
        return (u, v) if u < v else (v, u)

    def _make_variables(self) -> None:
        for i in range(8):
            for a in range(self.hvec[i]):
                self.high.add(sv(i, a))
            for j in range(i + 1, 8):
                if PAIR[i] == j:
                    continue
                for a in range(5):
                    for b in range(5):
                        e = self._key(sv(i, a), sv(j, b))
                        self.cross[e] = self.pool.id(("e",) + e)
        for i, h in enumerate(self.hvec):
            if h == 0:
                self.zvars[i] = (
                    self.pool.id(("internal_first", i)),
                    self.pool.id(("internal_second", i)),
                )
            elif h == 1:
                self.zvars[i] = (self.pool.id(("internal_second", i)),)

    def _make_forced_edges(self) -> None:
        for i in range(8):
            self.forced.add(self._key(0, 1 + i))
            for a in range(5):
                self.forced.add(self._key(1 + i, sv(i, a)))
        for i in range(0, 8, 2):
            self.forced.add(self._key(1 + i, 1 + i + 1))

    def internal_lit(self, i: int, a: int, b: int) -> bool | int:
        if a > b:
            a, b = b, a
        h = self.hvec[i]
        if h == 0:
            z1, z2 = self.zvars[i]
            if (a, b) == (0, 1):
                return z1
            if (a, b) == (2, 3):
                return z2
            return False
        if h == 1:
            (z2,) = self.zvars[i]
            if (a, b) == (0, 1):
                return True
            if (a, b) == (2, 3):
                return z2
            return False
        return (a, b) in ((0, 2), (1, 3))

    def edge_lit(self, u: int, v: int) -> bool | int:
        e = self._key(u, v)
        if e in self.forced:
            return True
        if u >= 9 and v >= 9:
            i, a = divmod(u - 9, 5)
            j, b = divmod(v - 9, 5)
            if i == j:
                return self.internal_lit(i, a, b)
            if PAIR[i] == j:
                return False
            return self.cross[e]
        return False

    def add_clause(self, lits: Iterable[bool | int]) -> None:
        out: list[int] = []
        for lit in lits:
            if lit is True:
                return
            if lit is False:
                continue
            out.append(int(lit))
        if not out:
            raise RuntimeError("construction produced the empty clause")
        self.cnf.append(out)

    @staticmethod
    def neg(lit: bool | int) -> bool | int:
        if isinstance(lit, bool):
            return not lit
        return -lit

    def _exactly(self, lits: list[int], bound: int) -> None:
        if bound < 0 or bound > len(lits):
            raise RuntimeError("impossible degree bound")
        if not lits:
            if bound:
                raise RuntimeError("impossible empty cardinality constraint")
            return
        enc = CardEnc.equals(
            lits=lits,
            bound=bound,
            vpool=self.pool,
            encoding=EncType.seqcounter,
        )
        self.cnf.extend(enc.clauses)

    def _encode_internal_canonicalization(self) -> None:
        for i, h in enumerate(self.hvec):
            if h == 0:
                z1, z2 = self.zvars[i]
                self.cnf.append([-z2, z1])

    def _encode_high_independence(self) -> None:
        for e, lit in self.cross.items():
            if e[0] in self.high and e[1] in self.high:
                self.cnf.append([-lit])
        for i in range(8):
            for a in range(5):
                for b in range(a + 1, 5):
                    u, v = sv(i, a), sv(i, b)
                    if u in self.high and v in self.high:
                        lit = self.internal_lit(i, a, b)
                        if lit is True:
                            raise RuntimeError("canonical internal edge joins two high vertices")
                        if lit is not False:
                            self.cnf.append([-lit])

    def _encode_block_matchings(self) -> None:
        for i in range(8):
            for j in range(i + 1, 8):
                if PAIR[i] == j:
                    continue
                for a in range(5):
                    row = [self.cross[self._key(sv(i, a), sv(j, b))] for b in range(5)]
                    for x, y in itertools.combinations(row, 2):
                        self.cnf.append([-x, -y])
                for b in range(5):
                    col = [self.cross[self._key(sv(i, a), sv(j, b))] for a in range(5)]
                    for x, y in itertools.combinations(col, 2):
                        self.cnf.append([-x, -y])

    def _encode_degrees(self) -> None:
        for i, h in enumerate(self.hvec):
            for a in range(5):
                x = sv(i, a)
                fixed = 0
                vars_: list[int] = []
                for y in range(9, N):
                    if y == x:
                        continue
                    lit = self.edge_lit(x, y)
                    if lit is True:
                        fixed += 1
                    elif lit is not False:
                        vars_.append(lit)
                target_q = 6 + int(a < h)
                self._exactly(vars_, target_q - fixed)

    def _encode_c4_free(self) -> None:
        for a, b, c, d in itertools.combinations(range(N), 4):
            for cyc in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                edges = [self.edge_lit(cyc[t], cyc[(t + 1) % 4]) for t in range(4)]
                if any(e is False for e in edges):
                    continue
                self.add_clause(self.neg(e) for e in edges)

    def _and_indicator(self, left: bool | int, right: bool | int, tag: tuple) -> bool | int:
        if left is False or right is False:
            return False
        if left is True:
            return right
        if right is True:
            return left
        p = self.pool.id(tag)
        self.cnf.append([-p, left])
        self.cnf.append([-p, right])
        self.cnf.append([-left, -right, p])
        return p

    def _encode_high_radius_two(self) -> None:
        requirements: set[tuple[int, int]] = set()
        for x in self.high - {0}:
            for y in range(N):
                if y != x:
                    requirements.add(self._key(x, y))
        for x, y in sorted(requirements):
            witnesses: list[bool | int] = []
            for w in range(N):
                if w in (x, y):
                    continue
                witnesses.append(
                    self._and_indicator(
                        self.edge_lit(x, w),
                        self.edge_lit(y, w),
                        ("common", x, y, w),
                    )
                )
            self.add_clause(witnesses)

    def _encode(self) -> None:
        self._encode_internal_canonicalization()
        self._encode_high_independence()
        self._encode_block_matchings()
        self._encode_degrees()
        self._encode_c4_free()
        self._encode_high_radius_two()

    def write_dimacs(self, path: Path) -> str:
        self.cnf.to_file(str(path))
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def graph_from_model(self, model: list[int]) -> list[tuple[int, int]]:
        positive = {lit for lit in model if lit > 0}
        edges: list[tuple[int, int]] = []
        for u, v in itertools.combinations(range(N), 2):
            lit = self.edge_lit(u, v)
            if lit is True or (lit is not False and lit in positive):
                edges.append((u, v))
        return edges


def verify_graph(edges: list[tuple[int, int]]) -> dict:
    adj = [set() for _ in range(N)]
    for u, v in edges:
        if not (0 <= u < v < N):
            raise AssertionError(f"bad edge {(u, v)}")
        adj[u].add(v)
        adj[v].add(u)
    degrees = [len(a) for a in adj]
    bad = []
    for u in range(N):
        for v in range(u + 1, N):
            common = adj[u] & adj[v]
            if len(common) > 1:
                bad.append((u, v, sorted(common)))
    if min(degrees) < 7 or bad:
        raise AssertionError(f"invalid model: min degree={min(degrees)}, C4 witnesses={bad[:3]}")
    return {
        "vertices": N,
        "edges": len(edges),
        "degree_counts": dict(sorted(Counter(degrees).items())),
        "minimum_degree": min(degrees),
        "maximum_degree": max(degrees),
        "c4_witness_count": len(bad),
    }


def solve_case(case: int, solvers: list[str], outdir: Path, write_cnf: bool) -> dict:
    t0 = time.time()
    inst = Instance(case)
    outdir.mkdir(parents=True, exist_ok=True)
    cnf_path = outdir / f"case_{case:02d}.cnf"
    cnf_hash = inst.write_dimacs(cnf_path)
    if not write_cnf:
        cnf_path.unlink()
    results = []
    first_status = None
    sat_edges = None
    for name in solvers:
        start = time.time()
        with Solver(name=name, bootstrap_with=inst.cnf.clauses, use_timer=True) as solver:
            status = solver.solve()
            elapsed = time.time() - start
            stats = solver.accum_stats()
            row = {
                "solver": name,
                "status": "SAT" if status else "UNSAT",
                "elapsed_seconds": elapsed,
                "solver_time_seconds": solver.time_accum(),
                "stats": stats,
            }
            if status:
                edges = inst.graph_from_model(solver.get_model())
                row["model_verification"] = verify_graph(edges)
                sat_edges = edges
            results.append(row)
            if first_status is None:
                first_status = status
            elif status != first_status:
                raise RuntimeError(f"solver disagreement in case {case}: {results}")
    payload = {
        "case": case,
        "orbit": canonical_orbits()[case],
        "hvec": inst.hvec,
        "additional_degree8_vertices": sum(inst.hvec),
        "variables": inst.cnf.nv,
        "clauses": len(inst.cnf.clauses),
        "cnf_sha256": cnf_hash,
        "solvers": results,
        "python": sys.version,
        "platform": platform.platform(),
        "wall_seconds": time.time() - t0,
    }
    if sat_edges is not None:
        graph_path = outdir / f"case_{case:02d}_graph.json"
        graph_path.write_text(json.dumps(sat_edges, indent=2) + "\n")
        payload["graph_file"] = graph_path.name
    result_path = outdir / f"case_{case:02d}_result.json"
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, required=True)
    parser.add_argument("--solvers", default="cadical195,glucose42")
    parser.add_argument("--outdir", type=Path, default=Path("f42-results"))
    parser.add_argument("--write-cnf", action="store_true")
    parser.add_argument("--list-orbits", action="store_true")
    args = parser.parse_args()
    if args.list_orbits:
        for i, orbit in enumerate(canonical_orbits()):
            print(i, orbit)
        return
    solvers = [x.strip() for x in args.solvers.split(",") if x.strip()]
    if not solvers:
        raise SystemExit("no solvers selected")
    solve_case(args.case, solvers, args.outdir, args.write_cnf)


if __name__ == "__main__":
    main()

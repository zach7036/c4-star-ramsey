r"""Run all Case-B canonical subcases across cores, resuming from results.jsonl."""
import json, os, re, sys, time, glob
from multiprocessing import Pool

import caseB2
from pysat.solvers import Cadical195

RESULTS = "results.jsonl"
if "--fresh" in sys.argv:
    RESULTS = "results_fresh.jsonl"
    sys.argv = [a for a in sys.argv if a != "--fresh"]


def done_indices():
    done = set()
    if os.path.exists(RESULTS):
        for line in open(RESULTS):
            line = line.strip()
            if line:
                done.add(json.loads(line)["idx"])
    for f in glob.glob("cb2_*.log"):                    # salvage the killed run
        for line in open(f):
            m = re.match(r"\[(\d+)\].*?(UNSAT|build-contradiction)", line)
            if m:
                done.add(int(m.group(1)))
    return done


def work(idx):
    pq, ptypes, p7 = caseB2.subcases()[idx]
    t0 = time.time()
    try:
        E = caseB2.build(pq, ptypes, p7)
    except ValueError as err:
        return dict(idx=idx, result="build-contradiction", detail=str(err),
                    secs=round(time.time() - t0, 1))
    with Cadical195(bootstrap_with=E.cnf) as s:
        r = s.solve()
        rec = dict(idx=idx, pq=int(pq), types=[ptypes[i] for i in range(2, 7)],
                   s7=int(p7), result="SAT" if r else "UNSAT",
                   clauses=len(E.cnf.clauses), secs=round(time.time() - t0, 1))
        if r:
            model = {l for l in s.get_model() if l > 0}
            import itertools
            edges = [(i, j) for i, j in itertools.combinations(range(46), 2)
                     if E.e(i, j) is True or
                        (not isinstance(E.e(i, j), bool) and E.e(i, j) in model)]
            json.dump(edges, open(f"SOLUTION_{idx}.json", "w"))
        return rec


if __name__ == "__main__":
    total = len(caseB2.subcases())
    done = done_indices()
    todo = [i for i in range(total) if i not in done]
    print(f"{total} subcases, {len(done)} already done, {len(todo)} to run", flush=True)
    t0 = time.time()
    with Pool(processes=int(sys.argv[1]) if len(sys.argv) > 1 else 8) as pool:
        with open(RESULTS, "a") as out:
            for k, rec in enumerate(pool.imap_unordered(work, todo), 1):
                out.write(json.dumps(rec) + "\n"); out.flush()
                print(f"({k}/{len(todo)}) [{rec['idx']}] {rec['result']} "
                      f"{rec.get('secs')}s  elapsed {time.time()-t0:.0f}s", flush=True)
                if rec["result"] == "SAT":
                    print("*** SOLUTION FOUND -- a 7-regular C_4-free graph on 46 vertices "
                          "EXISTS, so R(C_4,K_{1,39}) = 47 ***", flush=True)
                    pool.terminate(); break
            else:
                print("ALL SUBCASES UNSAT: no 7-regular C_4-free graph on 46 vertices; "
                      "hence R(C_4,K_{1,39}) = 46", flush=True)
    print(f"finished in {time.time()-t0:.0f}s", flush=True)

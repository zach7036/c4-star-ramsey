# Two Ramsey numbers: R(C₄, K₁,₃₉) = 46 and R(C₄, K₁,₅₁) = 59

Candidate resolutions of two open cases in the C₄-versus-star Ramsey family,
with complete proofs and machine verification. **Status: not yet peer-reviewed.**
Posted for timestamping and to invite mathematical review — issues and
corrections are welcome and wanted.

## Claims

Write f(n) := R(C₄, K₁,ₙ). As of the current references (Radziszowski, *Small
Ramsey Numbers*, EJC Dynamic Survey DS1 rev. 18, 2026, Table IVa; Boza,
arXiv:2409.12770v2, June 2026), f(39) ∈ {46, 47} and f(51) ∈ {59, 60} were
undetermined.

1. **Theorem 1: f(39) = 46**, hence R(C₄, W₄₀) = 46.
2. **Theorem 2: f(51) = 59**, hence R(C₄, W₅₂) = 59.
3. **Proposition: there is no 10-regular C₄-free graph on 93 vertices**, hence
   f(83) ≤ 93 (improves Parsons' bound f(83) ≤ 94; upper bound only).

Both theorems reduce, via a short forced-regularity count, to the nonexistence
of a k-regular C₄-free graph on N vertices — (46, 7) and (59, 8) respectively —
plus explicit lower-bound witness graphs (included, machine-checked).

**Not claimed here:** anything about f(52) or beyond (work in progress,
deliberately excluded); priority (we searched the literature through July 2026
and found no prior resolution, but that is not a guarantee); human peer review
(none yet — that is what this repository requests).

## How to verify

Requirements: Python 3.11, `pip install -r requirements.txt` (exact pinned
versions; tested with Python 3.11.9).

One command:

```
python run_all_verifiers.py
```

Or individually:

```
python verify_51.py            # Theorem 2 + Proposition, ~2 minutes, no SAT
python check_certificates.py   # the exact certificate of Theorem 1, seconds
python verify.py               # Theorem 1 full check incl. SAT encoder audits, ~10 min
python verify_m5.py            # the fifth-moment identity on six known graphs
```

Every load-bearing computation is exact (integers, rationals, algebraic numbers
via real-root isolation). No floating-point result is load-bearing anywhere.

### Warning to verifiers (Theorem 1)

The certificate polynomials are **tight at √3**: p(√3) − 1 ≈ 3.7·10⁻⁵ but
p(1.73) − 1 < 0. Checking the inequalities on a rational super-interval such as
[1.73, 3] therefore *falsely rejects a correct proof*. Verify at the algebraic
endpoints ±√3 (as `check_certificates.py` does). Margins at two endpoints are
10⁻⁶, so only exact arithmetic is meaningful.

## Proof summaries

**Theorem 1** (details: `R_C4_K1_39.md`). A C₄-free graph on 46 vertices with
δ ≥ 7 must be 7-regular with every vertex in 2 or 3 triangles; a parity lemma
(for odd k, a vertex with no far vertices and a matched neighbour would force a
perfect matching on an odd set) eliminates 2, forcing rigid structure. The
non-principal spectrum then satisfies five exact moment identities — decisively
Σθ⁵ = 2κ − 615 with κ ∈ [0, 46] a combinatorial count — and two explicit
rational degree-5 polynomials pin the number of positive eigenvalues into
[21.170045, 21.808845], which contains no integer. Independently, a 144-subcase
exhaustive SAT analysis (`caseB2.py`, `driver.py`, log `results.jsonl`; encoder
audits in `validate_encoding.py`, `validate_yconstraint.py`) reaches the same
conclusion with no spectral input.

**Theorem 2** (details: `R_C4_K1_51.md`). A C₄-free graph on 59 vertices with
δ ≥ 8 must be 8-regular; its "deficiency graph" (pairs with no common
neighbour) is 2-regular — a disjoint union of cycles — so its spectrum is
explicitly cyclotomic. Galois stability of the characteristic polynomial forces
every irrational eigenvalue pair into sign balance unless 7 − 2cos(2πj/d) is a
square in its field; the relevant norms satisfy ψ_d(7)² = Π_{e|d}(5F₂ₑ²)^{μ(d/e)}
(Fibonacci numbers) and none is a perfect square for d ≤ 59. The only rational
eigenvalues are ±3, so the trace gives 3(a − b) = −8: impossible. The same
argument at k = 10 (3 ∤ 10; ψ_d(9) is never a perfect square for any relevant
irrational-μ order d ≤ 93 — note ψ₄(9) = 9 = 3² IS a square, but d = 4 is the
rational case μ = 0, handled separately as the very source of the ±3 eigenvalues)
yields the
Proposition, re-proves f(18) = 23, and is *correctly silent* on the known case
(45, 7), where genuine square cases occur (ψ₁₄(6) = 13², ψ₁₅(6) = 31²) — the
method never falsely closes a case.

**Witnesses** (lower bounds): `lower_bound_45.json` (45 vertices, δ = 6,
C₄-free ⟹ f(39) ≥ 46, from the polarity graph of PG(2,7));
`lower_bound_58.json` (58 vertices, δ = 7 ⟹ f(51) ≥ 59, from PG(2,8)).
Also included: k-regular C₄-free graphs on (10,3), (15,4), (26,5), (34,6)
(`reg_*.json`) used as ground-truth validation of every method in both
directions. `NOTES.md` contains the general structure theory.

## Methodology and disclosure

These results were obtained by AI systems (Claude, Anthropic; with one step —
the identification of the fifth moment as the decisive constraint in Theorem 1 —
arising in a parallel session using GPT-5.6, OpenAI) directed by the repository
owner, with adversarial cross-checking between independent sessions and a
strict verification protocol: every load-bearing claim requires two independent
derivations or one exact machine check, and every encoder is validated against
ground truth in both directions (known graphs must be accepted; known
impossibilities refuted; undecidable cases left open). Multiple errors were
made and caught by this protocol during development; the repository contains
only what survived it. Human mathematical review has not yet occurred and is
the purpose of this posting.

## References

Boza, arXiv:2409.12770v2 (2026) · Radziszowski, EJC DS1.18 (2026) · Parsons,
Trans. AMS 209 (1975) · Wu–Sun–Zhang–Radziszowski, Graphs Combin. 31 (2015) ·
Zhang–Broersma–Chen, EJGTA 2 (2014) · Zhang–Chen–Cheng, Discrete Math. 340
(2017) & FFA 45 (2017) · Goryainov et al., Deza survey, arXiv:2103.00228.

## Independent verifiers

`verification_independent_openai/` contains three verifier implementations
written independently by a different AI system (GPT-5.6, OpenAI) in a separate
workspace: an independently constructed f(39) certificate, an independent check
of the certificate published here, and an all-orders norm scan that builds
every minimal polynomial directly. All three pass against this repository's
claims and artifacts; agreement between independently written implementations
is part of the verification methodology.

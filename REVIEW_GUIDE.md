# Review guide — where the load-bearing steps are

A referee who checks the numbered items below has checked the theorems.

## Theorem 1: R(C₄, K₁,₃₉) = 46   (`R_C4_K1_39.md`)

1. **Forced 7-regularity** (§3, Lemma 1): the counting identity
   Σ_{u∈N(v)} d(u) = 45 + 2m_v − f_v and 7d ≤ 45 + d.
2. **Exclusion of m_v = 2** (§5, Lemma 3): the parity argument — a matched
   block would carry a perfect matching on k − 2 = 5 vertices. This forces
   every vertex into exactly 3 triangles and the triangle-free edges into a
   perfect matching.
3. **The five moment identities**, decisively
   Σθ⁵ = tr(AD²) − 615 = 2κ − 615, κ ∈ [0, 46] (§7b): check
   N_D(u) ∩ N_D(v) = F_u ∩ F_v for edges uv, and the trace algebra
   A⁵ = AP² + 364J. Independently re-derivable via `verify_m5.py`, which
   validates the general identity on six known graphs.
4. **The spectral support** |θ| ∈ [√3, 3] from θ² = 6 − μ, μ ∈ spec(cubic D).
5. **The certificate** (`check_certificates.py`): p, q of degree 5;
   inequalities on ±[√3, 3] (WARNING: tight at √3 — see README), and the
   resulting integer-free window [4234009/200000, 4361769/200000] for N₊.

Independent corroboration: the 144-subcase SAT analysis (`caseB2.py`,
`driver.py`, `results.jsonl`) — soundness of the case split is §7 of the proof
document; encoder audits are `validate_encoding.py` / `validate_yconstraint.py`.

## Theorem 2: R(C₄, K₁,₅₁) = 59   (`R_C4_K1_51.md`)

1. **Forced 8-regularity**: 8d ≤ 58 + d.
2. **D is 2-regular** (deg_D = f_v + (8 − 2m_v) = 2 identically), hence a
   disjoint union of cycles; A² = 7I + J − D; A and D commute because G is
   regular (D = 7I + J − A², and A commutes with J).
3. **Galois sign-balance**: char(A) ∈ ℤ[x]; for irrational μ with 7 − μ not a
   square in ℚ(μ) = ℚ(θ² …), the minimal polynomial of √(7−μ) is
   Π(x² − (7−μᵢ)), pairing ±; equal multiplicities, zero trace contribution.
   Note μ = 7 − θ² ∈ ℚ(θ), so ℚ(θ) ⊇ ℚ(μ) and [ℚ(θ):ℚ(μ)] ∈ {1, 2}.
4. **The norm-square implication**: 7 − μ = α² ⟹ ψ_d(7) = N(α)² a perfect
   square in ℤ; the closed form ψ_d(7) via V_d(7) − 2 = 5F₂d² and Möbius
   inversion; the scan d ≤ 59 (`psi_squares.py`, cross-checked against sympy
   minimal polynomials for d ≤ 12 and against the product identity).
5. **The trace contradiction**: only ±3 rational (θ² ∈ {5,…,9} must be a
   square), so Σθ = −8 = 3(a − b), impossible.

Ground-truth behaviour of the same argument (§4 of the proof document): closes
the known case (23,5); correctly silent on the known case (45,7) (square cases
ψ₁₄(6) = 13², ψ₁₅(6) = 31²); correctly permits (15,4), whose witness realizes
the predicted sign-balance exactly.

## Proposition: f(83) ≤ 93

Same five steps at k = 10, N = 93; the only rational eigenvalues are ±3 from
the **rational** case μ = 0 (note ψ₄(9) = 9 is a square, but d = 4 is handled
in the rational branch, not the norm test); 3 ∤ 10.

## Reporting a gap

Open a GitHub issue quoting the numbered step above that you believe fails,
ideally with the smallest computation exhibiting the problem.

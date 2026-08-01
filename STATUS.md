# Status

- **Status:** preprint / seeking independent review
- **Peer reviewed:** no
- **Formally verified (proof assistant):** no
- **Exact-arithmetic verification of all load-bearing computations:** yes (run `python run_all_verifiers.py`)
- **Last literature / prior-art search:** 2026-07-31 (Radziszowski DS1.18; Boza arXiv:2409.12770v2; no prior resolution of f(39) or f(51) located — not a guarantee)
- **Known subtleties, handled and documented:**
  - the Theorem 1 certificate is tight at √3; rational super-interval checks falsely reject it (see README warning; `check_certificates.py` uses all-rational Sturm/bracketing arguments)
  - ψ₄(9) = 9 = 3² is a perfect square, but d = 4 is the rational case μ = 0, handled separately as the source of the ±3 eigenvalues in the k = 10 argument; the square-norm test applies only to irrational μ
- **SAT corroboration of Theorem 1:** complete encoder, all 144 canonical subcases, result log, and validation harness included; re-runnable (~3.5 CPU-hours, CaDiCaL 1.9.5). DRAT proof certificates NOT included. The spectral proof of Theorem 1 does not depend on the SAT computation.
- **Scope:** nothing is claimed here about R(C₄, K₁,₅₂) or any case not listed in the README.

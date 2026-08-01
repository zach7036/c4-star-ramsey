# AI assistance disclosure

These results were developed by AI systems directed by the repository owner:

- **Claude (Anthropic)** — structure theory, both proofs, the z = 2 Galois
  sign-balance argument and Fibonacci norm identity, the SAT campaign and its
  validation harness, the all-rational certificate verifier, witness
  constructions, prior-art searches, and this repository.
- **GPT-5.6 (OpenAI)**, in parallel sessions — identified the fifth spectral
  moment as the decisive constraint for Theorem 1 and produced the original
  numeric window; independently derived the Σθ⁵ identity (two independent
  derivations exist); produced independent verifier implementations; flagged
  the ψ₄(9) subtlety independently.

**Process:** adversarial cross-checking between independent AI sessions, with
every disagreement settled by exact recomputation. Multiple substantive errors
were made by both systems during development — including an invalid moment
bound, a wrong triangle-count bound for cubic graphs, an invalid constructed
"witness", and a verifier that falsely rejected a correct certificate — and
every one was caught by the verification protocol (two independent derivations
or one exact machine check for every load-bearing claim; validation of every
encoder against ground truth in both directions). Only what survived is
published here.

**Responsibility:** the human repository owner is the author of record and
accepts responsibility for the content. No AI system is listed as an author.
Independent human mathematical review has not yet occurred; obtaining it is the
purpose of this repository.

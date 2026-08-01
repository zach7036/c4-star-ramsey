> **Historical development notes.** This file records the structure theory as it
> was derived, before the spectral certificate existed; some framing (e.g. the
> finite computation as the decisive step) reflects that stage. The final proofs
> are `R_C4_K1_39.md` and `R_C4_K1_51.md`; where they differ from this file,
> they take precedence.

# R(C₄, K₁,₃₉): structure theory and the decisive finite case

## 0. Status of the problem

`f(n) := R(C₄, K₁,ₙ)`. Boza, *Exact values and bounds for Ramsey numbers of C₄ versus a
star graph*, arXiv:2409.12770v2 (12 June 2026), Table for 25 ≤ n ≤ 45, lists

* f(38) = 45, f(40) = 47 — known exactly;
* **f(39) ∈ {46, 47} — open.**

(Remark 12 of that paper asserts f(n) ≥ n + ⌈√n⌉ for n ≤ 82, giving f(39) ≥ 46;
Corollary 3 gives f(39) ≤ 39 + ⌈√38⌉ + 1 = 47. The paper's Remark 12 stops the
chain "f(n) ≥ f(n−1)+1" exactly at n = 39, which is only consistent with f(39)
being undetermined.)

**Lower bound, verified here independently.** Deleting 12 vertices from the
Erdős–Rényi polarity graph ER₇ (57 vertices, degrees 7 and 8) leaves a C₄-free graph
on 45 vertices with δ = 6 = 45 − 39. Hence **f(39) ≥ 46**. (`lower_bound_45.json`)

## 1. Reduction

f(n) is the least N such that **no** C₄-free graph on N vertices has δ ≥ N − n.
So

> f(39) = 47 ⟺ there is a C₄-free graph on 46 vertices with δ ≥ 7,
> f(39) = 46 otherwise.

Throughout, G is C₄-free on 46 vertices with δ(G) ≥ 7. For a vertex v write
m_v for the number of edges inside N(v) (= number of triangles through v) and
f_v for the number of vertices at distance ≥ 3 from v.

Two facts used constantly, both immediate from C₄-freeness:

* each u ∈ N(v) has **at most one** neighbour inside N(v) — so N(v) induces a matching;
* for u ≠ u′ in N(v) the sets N(u)∖N[v] and N(u′)∖N[v] are **disjoint**.

Counting V by distance from v therefore gives the basic identity

  **Σ_{u ∈ N(v)} d(u) = |V| − 1 + 2m_v − f_v.  (★)**

## 2. Lemma 1 — G is 7-regular

Let d = d(v). By (★), Σ_{u∈N(v)} d(u) = 45 + 2m_v − f_v ≤ 45 + d (as 2m_v ≤ d, f_v ≥ 0).
Every neighbour has degree ≥ 7, so 7d ≤ 45 + d, i.e. d ≤ 7.5, so d = 7. ∎

## 3. Lemma 2 — local structure

With all degrees 7, (★) reads 49 = 45 + 2m_v − f_v, i.e.

  **f_v = 2m_v − 4,  and since f_v ≥ 0 and m_v ≤ ⌊7/2⌋ = 3:  m_v ∈ {2,3}.**

Consequently the "no common neighbour" graph D on V (u ~_D w iff u ≠ w have no common
neighbour) is **3-regular**: each v sees exactly 7·6 = 42 distinct vertices at distance ≤ 2
other than itself, so deg_D(v) = 45 − 42 = 3. Writing A for the adjacency matrix,

  **A² = 6I + J − D**,  AD = DA,  so every non-principal eigenvalue satisfies θ² = 6 − μ
with μ an eigenvalue of a cubic graph; in particular |θ| ∈ [√3, 3].

## 4. Lemma 3 (the key step) — no vertex has m_v = 2

**Lemma.** Let k be odd and let G be k-regular and C₄-free. If a vertex v has f_v = 0
and m_v ≥ 1, then G does not exist.

*Proof.* Let u₁ ∈ N(v) be matched inside N(v), say to u₂, and let
S_i = N(u_i)∖N[v]. Since f_v = 0 the sets S₁,…,S_k partition the distance-2 set, and
|S_i| = k − 2 for a matched u_i, k − 1 otherwise. Take x ∈ S₁. Then

1. x has exactly one neighbour in N(v), namely u₁ (two would give a C₄ through v),
   and x ≁ v; hence x has exactly k − 1 neighbours at distance 2 from v;
2. x has at most one neighbour in each S_j — two, say y,y′, would have the two
   common neighbours u_j and x;
3. x has **no** neighbour in S₂: y ∈ S₂ with x ~ y gives the 4-cycle u₁ x y u₂.

So the k − 1 neighbours of x lie in the k − 1 blocks S₁, S₃, S₄, …, S_k, one in each.
In particular **every** x ∈ S₁ has exactly one neighbour in S₁, i.e. G[S₁] is a perfect
matching on |S₁| = k − 2 vertices — impossible for k odd. ∎

**Corollaries for k = 7.** Here f_v = 0 means n = 50 − 2m_v.

* n = 44 forces m_v = 3 for every v, so Lemma 3 applies: **no 7-regular C₄-free graph on
  44 vertices** (this re-proves f(37) = 44 by a purely elementary argument, replacing
  the parity/edge-count arguments in the literature);
* n = 46: **no vertex has m_v = 2**;
* n = 48: no vertex has m_v = 1.

## 5. Structure theorem for the surviving case

Combining Lemmas 2 and 3: if G exists then **m_v = 3 and f_v = 2 for every vertex**.
Hence:

* G contains exactly 46 triangles, they are pairwise edge-disjoint, and every vertex
  lies in exactly 3 of them;
* every vertex is incident with exactly 7 − 2·3 = 1 edge lying in no triangle, so the
  triangle-free edges form a **perfect matching M**;
* **G = (46 edge-disjoint triangles) ⊔ M**;
* the "distance exactly 3" relation is a **2-regular** graph (each vertex has exactly
  two vertices at distance 3), and D = M ⊔ D_far is the cubic deficiency graph;
* fixing a root v: N(v) = {u₁,…,u₇} with u₁u₂, u₃u₄, u₅u₆ ∈ E and u₇ unmatched;
  M(v) = u₇; blocks S₁,…,S₆ have 5 vertices and induce a 2-matching (unmatched vertex
  z_i = M(u_i)); S₇ has 6 vertices and induces a perfect matching; F = {p,q} are the two
  vertices at distance 3 from v;
* there are **no edges between partner blocks** S₁–S₂, S₃–S₄, S₅–S₆ (same 4-cycle as in
  Lemma 3 step 3), and every vertex has at most one neighbour in each block;
* z_i has no neighbour in S_i and none in the partner block, so its 6 non-u_i neighbours
  must fit into 5 blocks: **z_i is adjacent to p or to q**;
* p and q have all their neighbours inside the blocks, at most one per block, so
  p has one neighbour in each of 7 − [p~q] blocks.

## 6. The finite computation

The structure above is encoded exactly (CaDiCaL via PySAT), with:

* the whole distance partition around a root fixed (sound relabelling);
* the induced matchings inside every block fixed (sound relabelling);
* C₄-freeness via common-neighbour indicator variables (at-most-one per pair);
* degrees exactly 7;
* the global constraint "exactly one triangle-free edge at every vertex" (Section 5).

Symmetry of the *labelling* is then used to canonicalise N(p):

* swapping p, q — legitimate because z₁ is adjacent to at least one of them — gives
  WLOG p ~ z₁;
* Aut(S_i) for i = 2..6 (order 8, orbits {4 matched vertices} and {z_i}) gives WLOG
  p's neighbour in S_i, if any, is S_i[0] or z_i;
* Aut(S₇) (order 48, transitive) gives WLOG p's neighbour in S₇, if any, is a fixed vertex.

These groups act on pairwise disjoint vertex sets and fix everything already pinned down,
so the reduction is sound. It leaves **144 canonical subcases**.

## 7. Validation of the machinery

The same general encoding (`kregular_c4free.py`) reproduces every neighbouring value
that is already known:

| n, k | encoding says | literature |
|---|---|---|
| 10, 3 | exists | Petersen graph |
| 14, 4 | does not exist | f(10) = 14 |
| 15, 4 | exists | f(11) = 16 |
| 26, 5 | exists | f(21) = 27 |
| 34, 6 | exists (2.3 s) | f(28) = 35 |
| 44, 7 | does not exist | f(37) = 44 |
| 46, 7 | m = 2 branch UNSAT (4.8 s) | matches Lemma 3 |
| 48, 7 | m = 1 branch UNSAT (5.7 s) | matches Lemma 3 |

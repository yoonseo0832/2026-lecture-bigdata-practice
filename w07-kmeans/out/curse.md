# Task 2 · The Curse of Dimensionality — Contrast Curve

## A7 · Machine

- **OS**: Windows 11 (10.0.26200)
- **CPU**: Intel64 Family 6 Model 183 (Intel Core i7-13700H)
- **Python**: 3.12.8
- **Largest run**: dim 1000, 2000 points, 20,000 pairs → **1.64 s**. Every run
  finished in under two seconds; cost is roughly linear in dimension (each extra
  dimension is one more subtract-square-add per coordinate).

---

## A2 · Contrast vs Dimension

`contrast = (max − min) / min`, 20,000 random pairs, 1,000 uniform points in the
unit cube (500/1000 use 2,000 points).

| dim | mean dist | min | max | **contrast** | rel.sd (sd/mean) |
|-----|-----------|-----|-----|--------------|------------------|
| 2   | 0.521 | 0.003 | 1.326 | **488.58** | 0.476 |
| 5   | 0.884 | 0.111 | 1.687 | **14.26**  | 0.282 |
| 10  | 1.274 | 0.438 | 2.159 | **3.93**   | 0.193 |
| 20  | 1.815 | 0.821 | 2.670 | **2.25**   | 0.135 |
| 50  | 2.867 | 1.909 | 3.785 | **0.98**   | 0.083 |
| 100 | 4.068 | 3.206 | 4.954 | **0.55**   | 0.060 |
| 200 | 5.776 | 4.871 | 6.682 | **0.37**   | 0.041 |
| 500 | 9.126 | 8.099 | 10.176 | **0.26**  | 0.026 |
| 1000| 12.909| 11.970| 13.806 | **0.15**  | 0.019 |

---

## A3 · What happens to contrast

Contrast collapses, fast. From 488 in 2-D it is already down to ~2 by 20-D and
keeps shrinking.

- **Drops below 1** between dim 20 (2.25) and dim 50 (0.98) — so at my data size
  it crosses 1 at roughly **dim ≈ 50**.
- **Drops below 0.5** between dim 100 (0.55) and dim 200 (0.37) — crossing at
  roughly **dim ≈ 120**.

Below contrast ≈ 1 the furthest point is less than twice as far as the nearest;
by dim 1000 the furthest is only 15% further than the nearest. "Nearest" has
almost no room left to be meaningfully nearer than anything else.

---

## A4 · How the mean grows — it's √d, not linear

For two uniform points in the unit cube the expected squared distance per
coordinate is 1/6, so over d independent coordinates
E[dist²] = d/6 and **mean distance ≈ √(d/6)**.

| dim | measured mean | √(d/6) predicted |
|-----|---------------|------------------|
| 2   | 0.521 | 0.577 |
| 20  | 1.815 | 1.826 |
| 50  | 2.867 | 2.887 |
| 200 | 5.776 | 5.774 |
| 1000| 12.909| 12.910|

The fit is near-exact from dim 20 onward (0.03% at dim 200/1000). So the mean
grows as **√d, not linearly in d** — quadrupling the dimension only doubles the
typical distance. At small d the measured mean sits slightly *below* √(d/6)
because E[√X] ≤ √E[X] (Jensen); the gap vanishes as the distribution tightens.

---

## A5 · Relative standard deviation, and which measure is better

Relative standard deviation (sd ÷ mean) falls monotonically: 0.476 (d2) →
0.135 (d20) → 0.041 (d200) → 0.019 (d1000). The distance distribution
concentrates into an ever-thinner shell around its mean.

**Which better captures "distance stopped meaning anything"?** Contrast (A3).
Rel.sd is the *cause* — as the distribution concentrates, nearest and furthest
are squeezed together — but contrast is the *operational* quantity: it is
literally the ratio k-NN, k-means and LSH live or die on, "how much nearer is
the nearest than the furthest." When contrast → 0, "nearest neighbour" is no
longer distinguishable from "a random neighbour," which is the failure those
methods actually suffer. Rel.sd explains why it happens; contrast is the thing
that breaks.

---

## A6 · Does contrast depend on n as well as d?

Fixed dim = 20, fixed 20,000 sampled pairs, varying point count:

| points | contrast | rel.sd | mean |
|--------|----------|--------|------|
| 200    | 1.79 | 0.131 | 1.816 |
| 1,000  | 2.25 | 0.135 | 1.815 |
| 5,000  | 2.40 | 0.135 | 1.810 |
| 20,000 | 1.91 | 0.133 | 1.810 |

Contrast **wanders between 1.79 and 2.40 with no trend** — mean and rel.sd are
flat. At my data size, with the number of sampled *pairs* held fixed, n barely
matters: what sets the observed min and max is how many pairs you draw from the
pairwise-distance distribution, not how many points exist. (The dip at n=200 is
a sampling artefact — only ~20,000 distinct pairs exist among 200 points, so the
sample nearly exhausts them.)

The subtlety A6 is pointing at: *in principle* contrast does depend on n,
because the true nearest of n points keeps getting closer as n grows while the
furthest barely moves — so more points makes contrast worse, independent of d.
That n-dependence only shows up if you measure the true nearest/furthest over
all n points; a fixed random sample of pairs hides it. So the curse has **two
knobs**: higher d shrinks contrast (measured here clearly), and larger n also
shrinks the true nearest-vs-furthest gap (masked by fixed-pair sampling here).

---

## A8 · Does this threaten Week 3's LSH on Jaccard?

**No — the curse as measured here does not apply to Jaccard-LSH on documents,
for three reasons:**

1. **The data is not uniform in a cube.** This experiment fills a dense cube
   uniformly, which is exactly the worst case: every coordinate is independent
   noise, so distances concentrate. Shingle sets of real documents are sparse
   and highly structured — most document pairs share *zero* shingles (Jaccard
   similarity 0), while near-duplicates share most. That is a bimodal,
   high-contrast distribution, the opposite of a concentrated shell.

2. **Jaccard is not Euclidean.** The √(d/6) concentration argument is about
   summing many independent squared coordinate gaps. Jaccard is a set-overlap
   ratio bounded in [0,1]; adding more possible shingles (higher nominal
   dimension) does not force every pair toward the same similarity, because real
   documents only occupy a tiny, clustered corner of shingle space.

3. **LSH never relies on a meaningful global "nearest."** It hashes similar
   items into shared buckets and only compares within a bucket. It needs the
   *similar* pairs to stand out from the rest — which they do, precisely because
   the similarity distribution stays high-contrast. The curse kills brute-force
   nearest-neighbour in uniform high-dim space; LSH on sparse, clustered
   Jaccard data is a different regime and stays effective.

In short: the curse threatens "nearest" when points are dense and uniform in
high dimension. Document shingle sets are sparse, non-uniform, and clustered, so
the premise fails and LSH is safe.

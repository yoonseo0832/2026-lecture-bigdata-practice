# w07-kmeans · Observations

## Task 1 · k-means and its initialisation

- **R3 (empty cluster)**: I re-seed an empty cluster onto the point currently
  *worst served* — the one furthest from its own centroid (the "split the worst
  cluster" repair). This guarantees the dead centroid gets a point next round
  and lowers SSE. The alternative, keeping the old centroid, is also defensible
  but leaves a centroid that can stay empty forever, wasting one of your k.
- **40 seeds**: random initialisation found the three blobs **27/40 times**
  (mean SSE 31.3); it lands badly whenever two of its three starts fall in the
  same blob. **k-means++ found them 40/40** (mean SSE 0.12) — perfect, because
  the D²-weighting makes picking two seeds from the same tight blob very
  unlikely.
- **What ++ buys / when not to pay**: ++ spends ~(k−1)·n distance computations
  up front to spread the seeds, and buys far fewer wasted restarts and a
  reliably good local optimum. I'd skip it when k is tiny and I'm already doing
  many random restarts (cheap to just retry), or when n is enormous and the seed
  pass itself is the bottleneck.
- **Why not pick k by minimising SSE**: SSE falls monotonically as k rises and
  hits 0 when k = n (every point its own cluster), so minimising it always says
  "more clusters." It measures fit, not structure. You need the *elbow* (where
  SSE stops dropping sharply), a penalised criterion (BIC/gap statistic), or
  silhouette — something that charges for extra clusters.

## Task 2 · The curse of dimensionality

- **Contrast below 1**: at my data size (1,000 points, 20,000 pairs), contrast
  (max−min)/min crosses 1 at roughly **dim ≈ 50** (2.25 at dim 20 → 0.98 at dim
  50) and below 0.5 around dim ≈ 120. Mean distance tracks **√(d/6)** almost
  exactly from dim 20 on (5.776 measured vs 5.774 predicted at dim 200).
- **A6 — does n matter?** With the number of sampled *pairs* held fixed at
  20,000, varying points (200 → 20,000) at dim 20 left contrast wandering 1.79–
  2.40 with **no trend** — at this sampling, n barely matters; the observed
  min/max is set by how many pairs you draw, not how many points exist. In
  principle n *does* feed the curse (the true nearest of n points keeps shrinking
  as n grows), but that only shows if you measure true nearest/furthest over all
  n, not a fixed random sample. So the curse has two knobs: d (measured clearly)
  and n (masked here by fixed-pair sampling).
- **A8 — LSH on Jaccard**: not threatened. This experiment is dense, uniform
  points in a cube — the worst case that forces concentration. Document shingle
  sets are *sparse and clustered*: most pairs share zero shingles (Jaccard 0)
  while near-duplicates share most, a high-contrast bimodal distribution. Jaccard
  is a bounded overlap ratio, not a sum of d independent squared gaps, so adding
  nominal dimensions doesn't concentrate it. And LSH never relies on a global
  "nearest" — it buckets similar items by hashing. The premise of the curse
  fails, so LSH stays effective.

## Task 3 · The same clustering, with far fewer distances

- **Algorithm**: Elkan (ICML 2003), exact Lloyd's k-means. Result: **96.7% cut**
  (338,813 vs 10,320,000 distance computations), **SSE identical to the last
  decimal** (10,737,882.94), grade **strong**.
- **What I store per point**: one upper bound `upper[i]` on the distance to its
  own centroid, and k lower bounds `lower[i][j]`, one per centroid. That is
  **k + 1 = 13 extra numbers per point** (plus the label). Both bounds are
  repaired each iteration purely from how far each centroid moved — **k distance
  computations per iteration**, never the n·k scan.
- **R5 — which bound does the work**: the **upper bound + s(c) outer test** does
  the most. "If `upper[i] ≤ s(c(i))` (half the distance to the nearest *other*
  centroid), the point cannot have changed cluster" skips the entire point with
  **zero** distance computations, and once the centroids settle it fires for
  almost every point. Its cost is maintaining `upper` (loosen by the move of the
  own centroid) and computing the k(k−1)/2 centroid–centroid distances each
  iteration to get s(c). The per-centroid lower bounds are the finer net that
  prunes the few points the outer test lets through.
- **Why SSE is exactly zero off**: Elkan never approximates — it only skips a
  distance when the triangle inequality *proves* that centroid cannot be the
  nearest. Every assignment it makes is the same one Lloyd's would make, so the
  centroids, labels and SSE are bit-identical, not merely close.
- **First-iteration fraction**: the initial assignment cannot use the
  moved-centroid bounds (nothing has moved yet), so it is the single most
  expensive pass: **171,717 of 338,813 distances = 50.7%** of all the work
  happens there. After it, 41 more iterations together cost less than that one
  un-prunable pass.

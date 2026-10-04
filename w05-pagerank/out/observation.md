# Task 1

- Without the fix, a dead end's rank is simply dropped — `nr[w] += share`
  is never called for anything downstream of a node with no out-links, so
  that mass vanishes from the sum every iteration. The fix redistributes
  it to every node equally (`beta * r[v] / n` added to each), the same
  move as teleporting, instead of letting it leak out of the graph.
- The same fix works for both because a dead end and a spider trap are
  the same failure from the surfer's point of view: probability mass gets
  stuck somewhere it can't leave (nowhere, or a closed loop) with no way
  back out. Teleporting gives the surfer a way out of *any* dead-end-like
  state, whether that state is "no links at all" or "links that only loop
  back in," so one mechanism repairs both.
- `beta` is the probability the surfer follows an actual link on the page
  they're on. With probability `1 - beta`, they get bored and teleport to
  a uniformly random node instead of clicking anything — that's what
  guarantees every node keeps getting a little bit of rank no matter what
  the graph's structure does to the surfer.

# Task 2

- As beta → 1, iterations needed grows because the convergence rate scales
  like `log(tol)/log(beta)`, and `log(beta) → 0` in that limit — so
  convergence can be made arbitrarily slow by pushing beta close enough
  to 1, even though the measured range here (14 to 24 iterations) looks
  mild.
- A4: iteration count barely changed between n=1,200 and n=20,000 (within
  1 at every beta) — it's a property of beta and the graph's eigenvalue
  gap, not of size. Wall time changed a lot (~20x for a 16.7x larger
  graph) because every iteration still touches every node and edge once,
  so more nodes means strictly more work per iteration regardless of how
  many iterations run.
- A6: the top 6 of the top-10 ranking is identical at every beta tested,
  but positions 7-8 swap between beta=0.50 and beta=0.70 and stay swapped
  from there on. So a published "top 10" is not fully beta-independent —
  anyone trusting it should check whether the specific positions they
  care about sit in the stable part of the list or the part that moves.

# Task 3

- Instead of M, I store the adjacency list already given (`graph`) plus
  out-degrees, and keep two rank vectors of size n during each iteration —
  `2n + edge_count` floats total, vs. the dense version's `n^2`. For this
  graph that's 8,277 floats vs. 1,440,000 — 174x less, measured by
  `bench.py --yours` (also in `out/bench.txt`).
- R5: the teleport term adds `(1-beta)/n` to every node, and the dead-end
  term redistributes `beta * r[v] / n` to every node too — both look like
  they touch an n x n structure because every node gets updated, but
  touching every node once per iteration is O(n) work on an n-length
  vector, not O(n^2). The dense version's n^2 cost comes from M having a
  nonzero entry for every (node, node) pair when a column is spread
  across all n rows; a scalar added to every entry of a length-n vector
  never needs that pair structure at all.
- Worst per-node difference from the dense answer was 1.12e-15 — that's
  floating-point rounding noise from accumulating sums in a different
  order (vector-of-sums vs matrix-row-dot-product), not a bug; it's far
  below the 1e-9 tolerance the harness checks.

# Task 1

- One pass over the rows, not one pass per column, because a real dataset
  doesn't fit in memory — you can only afford to stream through it once.
  Re-scanning per column means re-reading the whole matrix once per
  document, which is fine for 4 columns but impossible once the matrix is
  bigger than memory (or coming from a stream/disk). Walking each row once
  and updating every column with a 1 in it keeps the whole thing to a
  single pass.
- R5 decision: rows_per_band = n // bands (integer division), and any
  leftover rows at the tail are dropped — they never join any band, so
  they can never cause a collision. This keeps every band the same size,
  which keeps the collision-probability formula 1-(1-s^r)^b accurate (an
  uneven last band would need its own formula).
- To narrow the S1/S4 gap (estimated 1.0, actual 2/3), use more hash
  functions in the signature. With only 2 hashes, agreeing in both is
  common by chance; with more hashes, two documents need to agree in a
  much higher fraction of positions before the estimate approaches 1.0,
  so the estimate converges to the true Jaccard similarity. The cost is
  more computation per document (one pass through the document's elements
  per extra hash function) and a longer signature to store for every
  document.

# Task 2

- Crossover was around n≈4,600 on my machine (i7-13650HX, 32GB RAM).
  Brute force was faster below that, LSH faster above it.
- The A4 quadratic check held cleanly (ratios ~4.0x for every doubling)
  once I closed background apps. An earlier run with other programs
  running gave inconsistent, non-monotonic timings, which was measurement
  noise rather than an algorithm issue.
- It became unpleasant around n=6000-8000 (89s-157s per brute run). Time
  ran out before memory did — brute force's memory stayed flat at ~6.6KB
  the whole time; LSH's memory grew to ~92MB at n=8000 but was never close
  to a problem on a 32GB machine.

# Task 3

- n=120, b=30 (r=4 rows/band). At threshold 0.6, this puts the S-curve's
  step at (1/b)^(1/r) = (1/30)^(1/4) ≈ 0.43 — well below the 0.6
  threshold. I chose it deliberately generous (step below the threshold)
  so that pairs sitting right at 0.6 still have a high chance of becoming
  candidates, favoring recall over raw comparison count.
- Moved the step the wrong way to check: with b=10, r=12, the step moves
  up to (1/10)^(1/12) ≈ 0.83 — above the 0.6 threshold. Measured recall
  dropped from 100.0% to 33.1% (comparisons also dropped, from 122 to 40,
  but that's meaningless once real pairs are being missed). This confirms
  the step needs to sit at or below the threshold, not above it — above
  it, a pair right at the threshold is unlikely to ever land in the same
  bucket.
- The harness doesn't charge for hashing, which is fair as long as hashing
  stays cheap relative to a comparison — true here because each
  similarity() call does a full set intersection/union over ~60-element
  shingle sets, while each hash is one multiply-mod. That stops being fair
  once documents get big enough that computing 120 hashes per document
  (each touching every shingle) costs comparably to a direct comparison,
  or once the corpus is so large that just storing/moving n × 120
  signature values becomes the actual bottleneck (e.g. across a cluster,
  where hashing is embarrassingly parallel but still isn't free bandwidth
  and disk I/O).
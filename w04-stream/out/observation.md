# w04-stream · Observations

---

## Task 1 · Sketches

**Bloom filter — no false negatives**: A Bloom filter only sets bits, never clears them. If an item was inserted, every one of its k bit positions was set to 1; looking them up later always finds 1s, so the filter can never return "not seen" for something it did see.

**Predicted vs measured false-positive rate**: With m=8192 bits, k=5, and n=800 items, the §4.4.2 formula gives (1 − e^(−5·800/8192))^5 = (1 − e^(−0.488))^5 ≈ **0.86%**. The measured rate on 20,000 absent items was **0.79%** — within 0.07 pp of the prediction, confirming the model is accurate.

**Flajolet-Martin combining rule**: The `geometric` rule (average the raw trailing-zero counts R, then return 2^(mean(R)) · 0.79) gave a ratio of ~1.0–1.2× true distinct. The plain `mean` of 2^R values was dominated by outliers (huge overestimate), and the pure `median` snapped to exact powers of two (coarse). The `geometric` rule is the best single-pass compromise.

**Reservoir sampling — where unknown length is handled**: Line 111 — `j = rng.randrange(i + 1)` — is the critical step. At position i (0-indexed), we draw j uniformly from [0, i], and replace sample[j] if j < k. This gives each item seen so far exactly probability k/(i+1) of being in the sample, without ever knowing the final stream length.

---

## Task 2 · Limits

**Where exact became unbearable**: The exact `set` reached 47 MB at n=1,600,000 in 3.9 s — heavy but not crashed. The FM implementation hit 348 seconds at that same size due to 64 blake2b hashes per element (CPU bottleneck). Memory gave out first in theory (the set would need ~700 MB around n=25M); in practice, time ran out first for FM.

**Growth rates**: Exact set memory grows O(n) — log-log slope 0.92 over a 64× size range (1 MB → 47 MB). FM memory is O(1) — fixed at 4.5 KB regardless of n, because it stores only 64 integers (the trailing-zero registers), not the elements.

**Is a factor of two good enough for "distinct users today"?** Yes, for capacity planning — knowing you had between 5M and 20M unique visitors is enough to size tomorrow's servers. No, for billing or fraud detection — a 2× error on paid API calls or flagged accounts is unacceptable; those require exact counts or at most a few percent error (HyperLogLog gets to ~1%).

---

## Task 3 · Fewer Mistakes

**Parameter changed**: k, the number of hash functions. The §4.4.2 false-positive rate is f(k) = (1 − e^(−kn/m))^k. Setting df/dk = 0 gives the optimal p = e^(−kn/m) = 1/2, hence k\* = (m/n)·ln 2. With m/n = 10: k\* = 10·ln 2 ≈ 6.93 → **k = 7**. The NaiveFilter uses k=1 (and wastes 8× the memory by storing one byte per "bit"); YourFilter uses true bit-packing (m=80,000 actual bits) and k=7 hashes.

**Floor and how close we got**: The theoretical minimum FP rate at m/n=10 is (1/2)^(10·ln 2) = 2^(−6.93) ≈ **0.82%**. With k=7 and proper bit-packing the measured rate is approximately 0.85–0.88%, which is ≤ 0.9% (the "strong" threshold) and within a fraction of a percent of the floor.

**If n were unknown**: Guessing too low sets k too high and wastes bits on extra hash functions, pushing the FP rate up once items overflow the expected density. Guessing too high sets k too low (closer to the NaiveFilter's k=1) and leaves performance on the table. In practice you would either over-provision m by a safety factor, use a scalable Bloom filter (which chains a sequence of fixed-size filters and grows as needed), or estimate n from a small pilot pass and then reinitialize.

# Task 2 — Crossover Curve

## A3 · Timing table

| n     | brute (s) | brute cmp  | LSH (s) | LSH cmp |
|-------|-----------|------------|---------|---------|
| 250   | 0.15      | 31,125     | 3.08    | 0       |
| 500   | 0.62      | 124,750    | 5.90    | 0       |
| 1000  | 2.44      | 499,500    | 11.60   | 0       |
| 2000  | 9.84      | 1,999,000  | 22.91   | 0       |
| 4000  | 39.56     | 7,998,000  | 46.21   | 4       |
| 5000  | 61.74     | 12,497,500 | 57.33   | 5       |
| 6000  | 89.00     | 17,997,000 | 69.41   | 8       |
| 8000  | 156.94    | 31,996,000 | 93.98   | 21      |

## A4 · Is brute force actually quadratic?

Doubling n and checking the time ratio:

| n doubled     | time ratio |
|---------------|-----------|
| 250 → 500     | 4.13x     |
| 500 → 1000    | 3.94x     |
| 1000 → 2000   | 4.03x     |
| 2000 → 4000   | 4.02x     |

All within ~3% of the expected 4x. The quadratic check holds cleanly once
background load was reduced (see A6) — an earlier run with browser/other
apps running showed non-monotonic times (e.g. time *decreasing* as n grew),
which was measurement noise, not the algorithm. LSH's own doubling ratios
(1.92x, 1.97x, 1.98x, 2.02x) confirm it scales linearly, as expected.

## A5 · Peak memory at n = 8000

| method | peak memory |
|--------|-------------|
| brute  | 6,736 bytes (~6.6 KB) |
| LSH    | 96,907,540 bytes (~92.4 MB) |

Brute force's memory is flat regardless of n — it only ever holds one pair
at a time. LSH's memory grows roughly linearly with n, because it keeps
every document's 120-number minhash signature (plus the LSH buckets) in
memory at once, rather than throwing work away as it goes.

## A7 · Crossover

At n=4000, brute (39.56s) is still faster than LSH (46.21s). At n=5000,
brute (61.74s) is slower than LSH (57.33s). Linear interpolation between
those two points puts the crossover at **n ≈ 4,600**.

## A8 · Why LSH loses at small n

LSH pays a fixed, per-document cost up front: hashing every document with
120 hash functions to build its minhash signature, regardless of how many
other documents exist. At n=250 that cost alone makes LSH ~20x slower than
brute force (3.08s vs 0.15s), because there are only 31,125 pairs to check
directly — cheap enough that skipping comparisons isn't worth the hashing
overhead yet. As n grows, the number of pairs grows quadratically while the
hashing cost only grows linearly, so the fixed cost eventually pays for
itself — that's the crossover at n≈4,600.

## A6 · Machine

- CPU: Intel Core i7-13650HX
- RAM: 32GB
- GPU: RTX 4060 (unused — this is pure CPU work)
- OS: Windows-11-10.0.26200-SP0, Python 3.12.8
- Background apps closed for this run; an earlier run with apps open
  produced inconsistent, non-monotonic timings (see A4)
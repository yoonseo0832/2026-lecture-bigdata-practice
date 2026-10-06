# Task 2 · Limits Measurement

## A6 · Machine

- **OS**: Windows 11 Education 10.0.26200
- **CPU**: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel (Intel Core i7-13700H)
- **Python**: 3.12.8
- **Other processes running**: normal background Windows processes + browser

---

## A3 · Measurements Table

| n | true distinct | exact time (s) | exact peak (MB) | FM time (s) | FM peak (KB) | FM ratio |
|---|---|---|---|---|---|---|
| 25,000 | 9,189 | 0.06 | 1.0 | 4.70 | 4.5 | 1.12x |
| 100,000 | 36,702 | 0.27 | 3.9 | 31.60 | 4.5 | 0.87x |
| 400,000 | 146,970 | 3.06 | 11.6 | 154.35 | 4.5 | 1.20x |
| 1,600,000 | 587,625 | 3.90 | 46.7 | 348.29 | 4.5 | 1.06x |

---

## A2 · Where Exact Became Unbearable

The exact `set` approach did not become unbearable in memory on this machine (47 MB at n=1.6M is manageable). However, **the FM implementation became unbearable at n=1,600,000: it took 348 seconds** (≈6 minutes) due to 64 × blake2b hash computations per element — a CPU bottleneck, not a memory limit.

If pushed further, the exact `set` would hit a memory wall around n=25,000,000 (estimated ~700 MB), while FM would simply take even longer but stay flat in memory.

---

## A4 · Growth Rates

Over the 64× range (n=25,000 → n=1,600,000):

- **Exact `set` memory**: 1.0 MB → 46.7 MB = **46.7× increase**  
  Log-log slope: log(46.7)/log(64) ≈ **0.92** — nearly linear O(n)
- **FM memory**: 4.5 KB → 4.5 KB = **0× increase**  
  FM memory is **O(1)** — fixed by the number of hash registers (64 integers), completely independent of n

FM uses ≈4.5 KB regardless of stream size. The exact set needs ~80 bytes per distinct element.

---

## A5 · FM Accuracy vs n

| n | FM ratio |
|---|---|
| 25,000 | 1.12× |
| 100,000 | 0.87× |
| 400,000 | 1.20× |
| 1,600,000 | 1.06× |

FM accuracy does **not systematically improve or worsen** as n grows — it wanders between 0.87× and 1.20× at all scales. This is expected: the error is determined by the randomness of the hash functions and the number of registers, not by n. With 64 hashes and the geometric mean rule, the estimate stays within a factor of 2 across all sizes.

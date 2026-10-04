# Task 2 · Explosion

Machine: Windows-11-10.0.26200-SP0, AMD64 Family 26 Model 68 Stepping 0 (AuthenticAMD), Python 3.14.0

## A3 · peak counters vs support (PlainApriori, 20,000 baskets, 2,000 items)

| support | frequent pairs | peak counters | seconds | peak memory |
|---|---|---|---|---|
| 400 | 249 | 10,585 | 0.31s | 1.1 MB |
| 200 | 776 | 58,626 | 0.54s | 6.7 MB |
| 100 | 2,244 | 273,701 | 1.13s | 28.6 MB |
| 50 | 6,397 | 820,259 | 2.28s | 107.7 MB |
| 25 | 17,045 | 893,456 | 2.37s | 107.7 MB |
| 12 | 43,116 | 893,456 | 2.43s | 110.0 MB |
| 6 | 101,938 | 893,456 | 2.33s | 126.5 MB |
| 3 | 250,054 | 893,456 | 2.62s | 163.9 MB |
| 2 | 424,620 | 893,456 | 2.48s | 211.9 MB |
| 1 | 893,456 | 893,456 | 3.30s | 334.3 MB |

## A2 · where it became unbearable

It never did, even at support = 1 (every item automatically frequent, the
absolute floor). Peak memory topped out at 334 MB and peak time at 3.3s —
comfortable on this machine (32 GB RAM). The reason is specific to this
dataset size: `peak_counters` caps at 893,456 starting around support ≈ 25
and never grows past it, because that number is the count of **distinct
pairs that ever co-occur in any of the 20,000 baskets** — once nearly all
2,000 items are already frequent, lowering the threshold further doesn't
expose any new pair, it just reclassifies already-tracked pairs as
"frequent." The explosion this task is built to find would need either a
much larger basket count (more distinct co-occurring pairs to discover) or
more items (more of the n² space to search before pass one prunes it).

## A4 · counter growth rate

Above the saturation point, counters grow much faster than halving the
support: 10,585 → 58,626 → 273,701 → 820,259 for support 400 → 200 → 100 →
50, i.e. **~5.5x, ~4.7x, ~3.0x per halving** — worse than doubling, not
just doubling. Below support ≈ 25 the growth rate drops to 1.0x (flat),
because of the saturation effect described in A2.

## A5 · frequent pairs vs counters — the gap

In the growth phase (support 400 → 50), frequent pairs grow ~3x per
halving while counters grow 3-5.5x per halving — the **search cost
(counters) grows faster than the answer count**, which is exactly the
problem §6.3 exists to fix: you pay for a much bigger haystack than the
needle count would suggest.

Below support ≈ 25 the relationship flips: counters are flat at 893,456
while frequent pairs keep climbing smoothly all the way to the floor
(17,045 → 893,456, support 25 → 1). Once the full set of observed pairs is
already being tracked, lowering the threshold costs nothing extra in
exploration — it only costs more in output size. The gap that matters for
"just lower the threshold a bit" is the first phase: that is where a small
drop in support buys a disproportionate jump in memory, before the
pair space is exhausted.

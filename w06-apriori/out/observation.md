# Task 1

- diaper -> beer has confidence 0.8 (support{diaper,beer}=4 /
  support{diaper}=5); beer -> diaper is also 0.8 here, because diaper and
  beer both appear in exactly 5 of the 7 example baskets — confidence is
  only symmetric when the two singleton supports happen to match. In
  general confidence(i->j) = support{i,j}/support{i} and
  confidence(j->i) = support{i,j}/support{j}, so whichever item is rarer
  on its own gets the higher confidence; the useful claim is the direction
  where the antecedent is the less common item.
- Highest-confidence rules found were diaper->beer and bread->milk, both
  0.8, lift 1.12. I believe them cautiously: lift just above 1 means beer
  and milk were already common on their own (beer and bread/milk/diaper
  all appear in 5 of 7 baskets), so the rule is barely more informative
  than "most baskets have beer anyway" — not a strong signal, just a
  real one.
- With 2,000 items, brute force needs C(2000,2) = 1,999,000 pair counters
  before reading a single basket. On the bench.py dataset at support 50,
  1,849 of the 2,000 items survive pass one, so A-Priori's pass two only
  needs C(1849,2) = 1,708,476 candidate counters. That is a smaller cut
  than I expected going in — this Zipf-weighted dataset makes most items
  common enough to be frequent at support 50, so the real saving from
  A-Priori here is modest; it would be much larger on a dataset with a
  longer tail of genuinely rare items.

# Task 2

- The support/counter explosion this task is built to find never actually
  arrived on this dataset, even at support = 1 (the absolute floor, every
  item trivially frequent) — peak counters plateaued at 893,456 starting
  around support ≈ 25, and peak memory only reached 334 MB. That plateau
  is the number of distinct pairs that ever co-occur across all 20,000
  baskets; once nearly every item is already frequent, lowering the
  threshold further can't expose new pairs, it only reclassifies ones
  already being tracked.
- A4: above that plateau, counters grew much faster than the support
  halved — about 5.5x, 4.7x, then 3.0x per halving from support 400 down
  to 50 — clearly worse than doubling, before flattening to 1.0x once
  saturation hit.
- A5: frequent pairs (the answers) kept growing smoothly the whole way
  down (249 at support 400 to 893,456 at support 1), while counters (the
  search cost) stopped growing after support ≈ 25. So the "just lower the
  threshold a bit" danger is concentrated in the early, high-support
  range, where a small drop in support buys a disproportionate jump in
  memory — exactly the gap §6.3 exists to close.

# Task 3

- Bucket count: 1,000,003 (a prime near 1 million). Large enough that
  most of the ~1.7M candidate pairs from pass one hash to distinct
  buckets rather than colliding into a false "frequent" bucket, but still
  a fixed, bounded array rather than one counter per possible pair.
- R5: pass one's bucket array holds 1,000,003 integers — bigger than the
  baseline's peak of 820,259 pair counters, so on *this* data PCY's pass
  one alone costs more than PlainApriori's total. The honest accounting:
  the array is temporary (collapsed to a 1-bit-per-bucket bitmap before
  pass two) and PCY still wins overall, cutting peak counters 97.2%
  (23,356 vs 820,259), because what's actually scored is peak counters
  held *at once*, and the bucket array is gone before pass two's counters
  exist. PCY starts winning once the number of truly frequent pairs is
  small relative to the number of candidate pairs pass one would
  otherwise have to track — i.e. once the filter actually filters. On a
  tiny dataset where almost every candidate pair turns out frequent, the
  bucket array would be pure overhead with nothing to prune.
- Measured the effect of shrinking the bucket array directly: 1,000,003
  buckets gives 23,356 peak counters (the 97.2% cut above); at 100,003 it
  is 197,627 (weaker, but still filtering); at 10,007 and at 1,009 it is
  **exactly** 820,259 — identical to the baseline's peak, meaning every
  bucket collects enough hash collisions to clear the support threshold
  on its own, so pass two filters out nothing at all. A bucket array
  below some size for this data is not a weak filter, it is no filter.

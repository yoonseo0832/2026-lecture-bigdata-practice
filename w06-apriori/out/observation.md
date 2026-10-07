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

# Task 4 (optional)

- A6: 전역적으로 빈발한 쌍이 모든 청크에서 누락될 수 없는 이유 — 귀류법.
  어떤 쌍 {a,b}가 전체 N개 바스켓 중 support s 이상 등장한다고 하자.
  모든 청크에서 빈발하지 않다고 가정하면, 각 청크 i에서 {a,b}의 등장
  횟수 < s·|chunk_i|/N이다. 전체 합산하면 Σ < s·Σ|chunk_i|/N = s,
  이는 전체 등장 횟수 ≥ s와 모순. 따라서 최소 한 청크에서 빈발.
- A5: chunks를 바꿨을 때의 결과:
  - 4 chunks → candidates 9,876, pairs 6,397
  - 8 chunks → candidates 14,201, pairs 6,397
  - 16 chunks → candidates 24,418, pairs 6,397
  candidates(후보 수)는 chunk가 많아질수록 증가하고, pairs(최종 답)는
  변하지 않는다. 청크가 작아지면 scaled threshold가 낮아져 각 청크에서
  더 많은 쌍이 "지역 빈발"로 잡히지만, pass two가 전역 support로
  걸러내므로 최종 답은 동일하다.
- SON이 여기서 21× 느리지만 올바른 알고리즘인 이유: 이 데이터는 한
  머신에 들어가지만 현실의 바스켓 데이터(수십억 거래)는 그렇지 않다.
  PlainApriori/PCY는 전체 데이터가 메모리에 있어야 하지만 SON은 각
  청크를 독립적으로 처리할 수 있어 MapReduce로 병렬화 가능하다.
  데이터가 한 머신에 안 들어가면 빠른 단일머신 알고리즘은 아예
  실행 불가능하므로, 느려도 돌아가는 SON이 유일한 선택이다.

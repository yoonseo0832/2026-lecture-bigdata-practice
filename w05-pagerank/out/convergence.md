# Task 2 · Convergence

Machine: Windows-11-10.0.26200-SP0, AMD64 Family 26 Model 68 Stepping 0 (AuthenticAMD), Python 3.14.0

## A2 · iterations vs beta (n = 1,200, tol = 1e-10)

| beta | iterations | seconds |
|---|---|---|
| 0.50 | 14 | 0.011 |
| 0.70 | 17 | 0.014 |
| 0.85 | 20 | 0.016 |
| 0.95 | 23 | 0.018 |
| 0.99 | 24 | 0.019 |

## A3 · the shape

Iterations climb with beta: 14 → 17 → 20 → 23 → 24 for beta 0.50 → 0.99. Each
iteration of power iteration shrinks the error by a factor of about beta, so
the number of iterations needed to reach a fixed tolerance scales like
`log(tol) / log(beta)`. As beta → 1, `log(beta) → 0`, so that ratio grows
without bound — convergence gets arbitrarily slow near beta = 1, even though
the increase looks mild over this particular range (0.95 → 0.99 only adds 1
iteration because `log(0.99)` is still far from 0; the blow-up would show up
testing betas closer to 0.999+).

## A4 · two graph sizes (n = 1,200 vs n = 20,000, 16.7x apart)

| beta | iters @ 1,200 | iters @ 20,000 | sec @ 1,200 | sec @ 20,000 |
|---|---|---|---|---|
| 0.50 | 14 | 14 | 0.011 | 0.217 |
| 0.70 | 17 | 18 | 0.014 | 0.289 |
| 0.85 | 20 | 21 | 0.016 | 0.340 |
| 0.95 | 23 | 24 | 0.018 | 0.396 |
| 0.99 | 24 | 25 | 0.019 | 0.394 |

**Iteration count barely moves** (within 1 of the small graph at every beta) —
convergence speed depends on beta, not on how many nodes there are. **Wall
time moves a lot**, about 19-20x for a 16.7x increase in n, because each
iteration still has to touch every node and edge once; more nodes means more
work per iteration even though the number of iterations stays the same.

## A5 · two tolerances (beta = 0.85, n = 1,200)

| tol | iterations | seconds |
|---|---|---|
| 1e-6 | 12 | 0.010 |
| 1e-10 | 20 | 0.016 |

Going from 1e-6 to 1e-10 (4 extra digits of precision) cost 8 more
iterations — 2 iterations per extra digit measured. The naive estimate from
a flat per-step shrink of beta = 0.85 (`log10(0.85) ≈ -0.07`, so ~14
iterations per digit) overstates it a lot, because the L1 delta the code
checks is already shrinking faster than beta alone once the vector is close
to the fixed point — the graph's actual second eigenvalue, not beta, sets
the real late-stage convergence rate.

## A6 · does the top-10 change with beta?

Yes, but only slightly. Positions 1-6 are identical at every beta tested
(p00009, p00001, p00006, p00005, p00003, p00002). Positions 7 and 8 swap:
at beta = 0.50 the order is [..., p00000, p00004, ...], and from beta = 0.70
onward it is [..., p00004, p00000, ...]. So the ranking **first changes
between 0.50 and 0.70**, not at 0.85. The top-6 is stable across the whole
range, but a ranking that reports positions 7-8 exactly would already depend
on which beta was chosen — meaning a "top 10" published with beta = 0.85 is
not entirely beta-free, even if the choice of 0.85 vs 0.99 barely matters
for the top few.

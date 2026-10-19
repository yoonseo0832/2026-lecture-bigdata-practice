#!/usr/bin/env python3
"""Week 7 · Task 1 — k-means, and the thing that decides the answer.

Textbook §7.1 (clustering, the curse of dimensionality), §7.3 (k-means).

k-means is four lines: pick centroids, assign every point to the nearest one,
move each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote - it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

    python3 task1_kmeans.py --verify
"""
import argparse, math, random

# Three obvious blobs of three points each. Any sensible clustering finds them.
BLOBS = [(0.0, 0.0), (0.2, 0.1), (0.1, 0.2),
         (8.0, 8.0), (8.2, 8.1), (8.1, 8.2),
         (0.0, 8.0), (0.2, 8.1), (0.1, 8.2)]


def euclidean(a, b):
    """Distance between two points of any dimension."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign(points, centroids):
    """Nearest centroid for each point. Return a list of centroid indices.

    Ties go to the lower index, so that everybody's answer is the same.
    """
    labels = []
    for p in points:
        best, bi = None, 0
        for j, c in enumerate(centroids):
            d = euclidean(p, c)
            # strict `<` keeps the first (lowest-index) centroid on a tie
            if best is None or d < best:
                best, bi = d, j
        labels.append(bi)
    return labels


def update(points, labels, k):
    """Move each centroid to the mean of its points.

    An empty cluster has no mean. R3 choice: re-seed an empty cluster onto the
    point that is currently worst served (furthest from its own centroid). This
    is the standard "split the worst cluster" repair - it guarantees the empty
    cluster gets a point next round and tends to lower SSE. The alternative,
    keeping the old centroid, is also valid but leaves a dead centroid that may
    stay empty forever.
    """
    dim = len(points[0])
    sums = [[0.0] * dim for _ in range(k)]
    counts = [0] * k
    for p, l in zip(points, labels):
        counts[l] += 1
        row = sums[l]
        for d in range(dim):
            row[d] += p[d]

    centroids = [None] * k
    for j in range(k):
        if counts[j]:
            centroids[j] = tuple(s / counts[j] for s in sums[j])

    for j in range(k):
        if centroids[j] is None:
            worst, wp = -1.0, points[0]
            for p, l in zip(points, labels):
                if centroids[l] is None:
                    continue
                d = euclidean(p, centroids[l])
                if d > worst:
                    worst, wp = d, p
            centroids[j] = tuple(wp)
    return centroids


def _kmeans_pp(points, k, rng):
    """k-means++ seeding (§7.3.2): first centre random, each next chosen with
    probability proportional to D(x)^2, the squared distance to the nearest
    centre already chosen."""
    centroids = [tuple(rng.choice(points))]
    while len(centroids) < k:
        weights = []
        for p in points:
            dmin = min(euclidean(p, c) for c in centroids)
            weights.append(dmin * dmin)
        total = sum(weights)
        if total == 0:               # all remaining points coincide with a centre
            centroids.append(tuple(rng.choice(points)))
            continue
        r = rng.random() * total
        acc = 0.0
        for p, w in zip(points, weights):
            acc += w
            if acc >= r:
                centroids.append(tuple(p))
                break
    return centroids


def kmeans(points, k, init="random", seed=246, max_iter=100):
    """Run to convergence. Return (labels, centroids, sse).

    `sse` is the sum over points of the squared distance to their own centroid.
    It is what k-means minimises, and it is how you compare two runs.

    `init` is either:
        "random"   pick k points at random as the starting centroids
        "++"       k-means++ (§7.3.2): pick the first at random, then pick each
                   next one with probability proportional to the squared distance
                   to the nearest centroid already chosen

    Set `kmeans.iterations` to how many passes you used.
    """
    rng = random.Random(seed)
    if init == "random":
        centroids = [tuple(p) for p in rng.sample(points, k)]
    elif init == "++":
        centroids = _kmeans_pp(points, k, rng)
    else:
        raise ValueError(f"unknown init {init!r}")

    labels = None
    kmeans.iterations = max_iter
    for it in range(1, max_iter + 1):
        new_labels = assign(points, centroids)
        if new_labels == labels:      # no point moved -> converged
            kmeans.iterations = it
            break
        labels = new_labels
        centroids = update(points, labels, k)

    sse = sse_of(points, labels, centroids)
    return labels, centroids, sse


def sse_of(points, labels, centroids):
    """Sum of squared distances from each point to its assigned centroid."""
    return sum(euclidean(points[i], centroids[labels[i]]) ** 2
               for i in range(len(points)))


# ------------------------------------------------------------------- harness
def verify():
    fails = 0

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
        fails += not ok

    try:
        check("distance in 2d", abs(euclidean((0, 0), (3, 4)) - 5) < 1e-9)
        check("distance in 5d",
              abs(euclidean((0,) * 5, (1,) * 5) - math.sqrt(5)) < 1e-9)
    except NotImplementedError:
        print("  euclidean is still a stub"); return 1

    try:
        labels, cents, sse = kmeans(BLOBS, 3, init="++", seed=1)
    except NotImplementedError:
        print("  kmeans is still a stub"); return 1

    groups = {}
    for p, l in zip(BLOBS, labels):
        groups.setdefault(l, []).append(p)
    check("three clusters of three", sorted(len(g) for g in groups.values()) == [3, 3, 3],
          sorted(len(g) for g in groups.values()))
    check("the three blobs were recovered",
          all(max(q[0] for q in g) - min(q[0] for q in g) < 1 and
              max(q[1] for q in g) - min(q[1] for q in g) < 1
              for g in groups.values()))
    check("sse is small when clusters are right", sse < 1.0, f"sse {sse:.4f}")

    # Bad luck with random starts should sometimes be visibly worse.
    randoms = [kmeans(BLOBS, 3, init="random", seed=s)[2] for s in range(40)]
    plusplus = [kmeans(BLOBS, 3, init="++", seed=s)[2] for s in range(40)]
    check("random init sometimes lands badly", max(randoms) > min(randoms) * 5,
          f"sse from {min(randoms):.3f} to {max(randoms):.3f}")
    check("k-means++ is more reliable than random",
          sum(plusplus) / len(plusplus) <= sum(randoms) / len(randoms),
          f"mean sse: ++ {sum(plusplus) / len(plusplus):.3f} vs "
          f"random {sum(randoms) / len(randoms):.3f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())

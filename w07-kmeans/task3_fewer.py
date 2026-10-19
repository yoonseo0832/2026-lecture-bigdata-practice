#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        # Elkan's algorithm (ICML 2003). Exact Lloyd's k-means: same labels,
        # same centroids, same SSE - it just refuses to compute a distance it
        # can already bound away with the triangle inequality.
        #
        # Per point we keep:
        #   label        its current centroid index
        #   upper[i]     an UPPER bound on d(point, its own centroid)
        #   lower[i][j]  a LOWER bound on d(point, centroid j)
        # Both bounds are repaired from how far each centroid moved (k distance
        # computations per iteration), never by re-scanning all n*k pairs.
        n, k = len(points), self.k
        centroids = [tuple(c) for c in initial_centroids]

        lower = [[0.0] * k for _ in range(n)]
        upper = [0.0] * n
        label = [0] * n

        # --- initial assignment: the one pass we cannot avoid ---
        # Use centroid-centroid distances to skip far centroids even here.
        cc = self._centroid_dists(centroids, distance)
        sc = self._half_nearest(cc, k)
        for i, p in enumerate(points):
            best = distance(p, centroids[0])
            lower[i][0] = best
            bi = 0
            for j in range(1, k):
                # if the current best is within half the gap to centroid j,
                # j cannot be closer (triangle inequality) - skip it.
                if best <= 0.5 * cc[bi][j]:
                    continue
                d = distance(p, centroids[j])
                lower[i][j] = d
                if d < best:
                    best, bi = d, j
            label[i] = bi
            upper[i] = best

        for self.iterations in range(1, self.max_iter + 1):
            # (1) move each centroid to the mean of its current points, and
            #     measure how far it moved - k distance computations total.
            new_centroids = _means(points, label, k, centroids)
            delta = [distance(centroids[j], new_centroids[j]) for j in range(k)]
            centroids = new_centroids

            # (2) repair bounds from the moves (no point scan, no n*k work):
            #     own centroid may be up to delta further -> loosen upper;
            #     any centroid may be up to delta closer   -> loosen lower.
            for i in range(n):
                upper[i] += delta[label[i]]
                li = lower[i]
                for j in range(k):
                    v = li[j] - delta[j]
                    li[j] = v if v > 0.0 else 0.0

            # (3) reassign, pruning with the triangle inequality.
            cc = self._centroid_dists(centroids, distance)
            sc = self._half_nearest(cc, k)

            changed = False
            for i, p in enumerate(points):
                ci = label[i]
                # Elkan's outer test: within s(c) of its own centroid, no other
                # centroid can be closer. Skip the point - zero distances.
                if upper[i] <= sc[ci]:
                    continue

                u = upper[i]
                tight = False  # has upper[i] been recomputed exactly this round?
                li = lower[i]
                for j in range(k):
                    if j == ci:
                        continue
                    # all three must hold for j to possibly beat the current centroid
                    if u <= li[j] or u <= 0.5 * cc[ci][j]:
                        continue
                    if not tight:
                        u = distance(p, centroids[ci])  # tighten upper bound once
                        li[ci] = u
                        upper[i] = u
                        tight = True
                        if u <= li[j] or u <= 0.5 * cc[ci][j]:
                            continue
                    d = distance(p, centroids[j])
                    li[j] = d
                    if d < u:
                        u = d
                        ci = j
                        upper[i] = u
                        changed = True
                label[i] = ci

            if not changed:
                break

        return label, centroids

    @staticmethod
    def _centroid_dists(centroids, distance):
        k = len(centroids)
        cc = [[0.0] * k for _ in range(k)]
        for a in range(k):
            for b in range(a + 1, k):
                d = distance(centroids[a], centroids[b])
                cc[a][b] = cc[b][a] = d
        return cc

    @staticmethod
    def _half_nearest(cc, k):
        sc = [0.0] * k
        for a in range(k):
            m = min(cc[a][b] for b in range(k) if b != a)
            sc[a] = 0.5 * m
        return sc

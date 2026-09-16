#!/usr/bin/env python3
import random

_P = (1 << 61) - 1
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


class YourFinder:
    N_HASHES = 120   # 시그니처 길이
    BANDS = 30       # 밴드 수 -> 밴드당 4개 행 (r = n/b = 4)

    def __init__(self, threshold, n_hashes=None, bands=None, seed=1234):
        self.threshold = threshold
        self.n_hashes = n_hashes or self.N_HASHES
        self.bands = bands or self.BANDS
        if self.n_hashes % self.bands != 0:
            raise ValueError("n_hashes must divide evenly by bands")
        self.rows_per_band = self.n_hashes // self.bands

        # 매번 같은 해시 함수를 쓰도록 시드 고정 (재현 가능하게)
        rng = random.Random(seed)
        self._coeffs = [(rng.randrange(1, _P), rng.randrange(0, _P))
                         for _ in range(self.n_hashes)]

    def _signature(self, doc):
        """문서 하나의 minhash 시그니처. 이 문서의 shingle만 한 번씩 훑는다."""
        sig = [_P] * self.n_hashes
        for x in doc:
            for hi, (a, b) in enumerate(self._coeffs):
                v = (a * x + b) % _P
                if v < sig[hi]:
                    sig[hi] = v
        return sig

    def _candidates(self, docs):
        """LSH 밴딩: 같은 (밴드, 밴드 구간 값)을 가진 문서끼리 버킷에 모은다.
        similarity()를 전혀 호출하지 않으므로 harness가 비용을 안 매긴다."""
        buckets = {}
        for idx, doc in enumerate(docs):
            sig = self._signature(doc)
            for band in range(self.bands):
                start = band * self.rows_per_band
                end = start + self.rows_per_band
                key = (band, tuple(sig[start:end]))
                buckets.setdefault(key, []).append(idx)

        cands = set()
        for members in buckets.values():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    cands.add((a, b) if a < b else (b, a))
        return cands

    def find(self, docs, similarity):
        """LSH로 후보만 추리고, 후보만 실제 similarity()로 확인한다."""
        out = set()
        for i, j in self._candidates(docs):
            if similarity(docs[i], docs[j]) >= self.threshold:
                out.add((i, j))
        return out

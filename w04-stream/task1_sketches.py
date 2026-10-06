#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse, random, hashlib, math


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        self.m, self.k, self.seed = m, k, seed
        self.bits = bytearray((m + 7) // 8)

    def _indexes(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=16,
                            key=str(self.seed).encode()).digest()
        h1 = int.from_bytes(d[:8], "big")
        h2 = int.from_bytes(d[8:], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]
    
    def add(self, item):
        for i in self._indexes(item):
            self.bits[i >> 3] |= 1 << (i & 7)

    def __contains__(self, item):
        return all(self.bits[i >> 3] & (1 << (i & 7)) for i in self._indexes(item))

    def expected_fp_rate(self, n_inserted):
        """The textbook's predicted false-positive rate after n insertions.

        §4.4.2 derives it. Return the number, do not measure it - the harness
        measures separately and compares the two.
        """
        return (1.0 - math.exp(-self.k * n_inserted / self.m)) ** self.k


_PHI = 0.79   # R=최대 trailing zeros → 2^R이 n의 ~1.26배 → 0.79를 "곱한다"


def flajolet_martin(stream, n_hashes=64, seed=246):
    """구별 원소 수 추정. 상태 = 정수 n_hashes개 (스트림 길이와 무관)."""
    R = fm_registers(stream, n_hashes, seed)
    return fm_combine(R, "geometric")


def fm_registers(stream, n_hashes=64, seed=246):
    key = str(seed).encode()
    n_digest = (n_hashes + 15) // 16          # 64바이트 digest 1개 = 32비트 해시 16개
    R = [0] * n_hashes
    for item in stream:
        b = str(item).encode()
        for j in range(n_digest):
            d = hashlib.blake2b(b, digest_size=64, key=key,
                                salt=bytes([j])).digest()
            base = j * 16
            for t in range(min(16, n_hashes - base)):
                x = int.from_bytes(d[4 * t:4 * t + 4], "little")
                if x:
                    tz = (x & -x).bit_length() - 1     # trailing zeros
                    if tz > R[base + t]:
                        R[base + t] = tz
    return R


def fm_combine(R, rule="geometric", groups=8):
    est = [2.0 ** r for r in R]
    if rule == "mean":
        return sum(est) / len(est) * _PHI
    if rule == "median":
        s = sorted(est); mid = len(s) // 2
        return (s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2) * _PHI
    if rule == "group_median":                 # §4.5.3: 그룹 평균 → 중앙값
        size = len(est) // groups
        avgs = sorted(sum(est[g * size:(g + 1) * size]) / size for g in range(groups))
        mid = groups // 2
        med = avgs[mid] if groups % 2 else (avgs[mid - 1] + avgs[mid]) / 2
        return med * _PHI
    if rule == "geometric":                    # 지수 R을 평균한 뒤 2^평균
        return 2.0 ** (sum(R) / len(R)) * _PHI
    raise ValueError(rule)


def reservoir_sample(stream, k, seed=246):
    """길이를 모르는 스트림에서 k개를 균등하게 뽑는다."""
    rng = random.Random(seed)
    sample = []
    for i, item in enumerate(stream):          # i = 이 항목 이전에 본 개수
        if i < k:
            sample.append(item)                # 앞 k개는 그냥 채운다
        else:
            j = rng.randrange(i + 1)           # ← 길이를 몰라도 되는 부분
            if j < k:
                sample[j] = item               # 확률 k/(i+1)로 무작위 슬롯 교체
    return sample
# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())

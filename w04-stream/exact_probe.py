import sys
from task2_limits import exact_distinct

for n in [int(x) for x in sys.argv[1:]]:
    try:
        d, s, peak = exact_distinct(n)
        print(f"n={n:>11,}  distinct {d:>10,}  {s:6.1f}s  {peak/1e9:5.2f} GB")
    except MemoryError:
        print(f"n={n:>11,}  MemoryError")
        break
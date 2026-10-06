import json, math

d = json.load(open("out/limits.json"))
by_n = {}
for r in d["runs"]:
    by_n[r["n"]] = r                      # 같은 n은 마지막 측정만
runs = [by_n[n] for n in sorted(by_n)]

print("| n | distinct | exact 시간(s) | exact 피크(MB) | FM 시간(s) | FM 피크(KB) | FM 추정/진짜 |")
print("|---|---|---|---|---|---|---|")
for r in runs:
    print(f"| {r['n']:,} | {r['true_distinct']:,} | {r['exact_s']:.2f} | "
          f"{r['exact_peak_bytes']/1e6:.1f} | {r.get('fm_s', float('nan')):.2f} | "
          f"{r.get('fm_peak_bytes', 0)/1e3:.1f} | {r.get('fm_ratio', float('nan')):.2f}x |")

a, b = runs[0], runs[-1]
nx = b["n"] / a["n"]
print(f"\n크기 {nx:.0f}배 증가 구간 ({a['n']:,} → {b['n']:,})")
for key, name in [("exact_peak_bytes", "exact 메모리"), ("fm_peak_bytes", "FM 메모리"),
                  ("exact_s", "exact 시간"), ("fm_s", "FM 시간")]:
    if a.get(key) and b.get(key):
        g = b[key] / a[key]
        print(f"  {name}: {g:.2f}배  (log-log 기울기 {math.log(g)/math.log(nx):.2f})")
print(f"  exact 바이트/고유원소: {a['exact_peak_bytes']/a['true_distinct']:.0f} → "
      f"{b['exact_peak_bytes']/b['true_distinct']:.0f}")
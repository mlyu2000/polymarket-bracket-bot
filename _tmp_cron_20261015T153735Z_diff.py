import json

prev = json.load(open('runs/_tmp_cron_20261015T1521Z_supp_data.json'))
cur = json.load(open('runs/_tmp_cron_20261015T153735Z_supp_data.json'))

def idx(d):
    return {r['q']: r for r in d['top25']}

p, c = idx(prev), idx(cur)
print("=== TIERS ===")
for k in ['<=1.050', '<=1.020', '<=1.010', '<=1.005', '<1.000']:
    print(f"  {k}: {prev['tiers'][k]} -> {cur['tiers'][k]}")
print(f"  two_sided: {prev['two_sided']} -> {cur['two_sided']}")
print(f"  markets: {prev['markets']} -> {cur['markets']}  scan_time: {prev['scan_time']}s -> {cur['scan_time']}s")

print("\n=== NEW in top25 (not present before) ===")
for q, r in c.items():
    if q not in p:
        print(f"  {r['total']} | {q} | liq {r['liq']}")

print("\n=== DROPPED from top25 ===")
for q, r in p.items():
    if q not in c:
        print(f"  {r['total']} | {q} | liq {r['liq']}")

print("\n=== CHANGED (total or liq) ===")
for q in c:
    if q in p:
        a, b = p[q], c[q]
        if abs(a['total'] - b['total']) > 1e-9 or abs(a['liq'] - b['liq']) > 1.0:
            dt = b['total'] - a['total']
            dl = b['liq'] - a['liq']
            print(f"  {q[:52]}: total {a['total']} -> {b['total']} ({dt:+.3f}) | liq {a['liq']:.1f} -> {b['liq']:.1f} ({dl:+.1f})")

print("\n=== FLOOR ===")
pf, cf = prev['top25'][0], cur['top25'][0]
print(f"  prev floor: {pf['total']} {pf['q']} (liq {pf['liq']:.1f})")
print(f"  cur  floor: {cf['total']} {cf['q']} (liq {cf['liq']:.1f})")
print(f"  LEADER SAME: {pf['q'] == cf['q']}")
print(f"  liq delta: {cf['liq'] - pf['liq']:+.1f}")

print("\n=== TOP12 ORDER ===")
for i, r in enumerate(cur['top25'][:12], 1):
    print(f"  {i}. {r['total']} | {r['q'][:50]} | liq {r['liq']:.1f}")

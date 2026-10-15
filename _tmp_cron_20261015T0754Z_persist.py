"""Persist this cron run: dedupe the transient pagination duplicate (Jablonec
-2.5 appeared twice in the supp scan due to a live-liquidity shift mid-
pagination), compute stats from the deduped rows, and append to history.
"""
import json

d = json.load(open('runs/_tmp_cron_20261015T0754Z_supp_data.json'))

# Dedupe: same question+yes+no captured twice (transient pagination artifact).
# Keep the higher-liquidity (fresher) copy.
seen = {}
dup_removed = 0
for r in d['rows_all']:
    key = (r['q'], r['yes'], r['no'])
    if key in seen:
        dup_removed += 1
        if r['liq'] > seen[key]['liq']:
            seen[key] = r
    else:
        seen[key] = r
rows = sorted(seen.values(), key=lambda r: r['total'])

tiers = {'le1.050': 0, 'le1.020': 0, 'le1.010': 0, 'le1.005': 0, 'lt1.000': 0}
for r in rows:
    t = r['total']
    if t <= 1.050:
        tiers['le1.050'] += 1
    if t <= 1.020:
        tiers['le1.020'] += 1
    if t <= 1.010:
        tiers['le1.010'] += 1
    if t <= 1.005:
        tiers['le1.005'] += 1
    if t < 1.000:
        tiers['lt1.000'] += 1

with_both_asks = d['with_both_asks'] - dup_removed
two_sided = d['two_sided'] - dup_removed

entry = {
    "ts_utc": "20261015T0754Z",
    "markets": d['markets'],
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "with_both_asks": with_both_asks,
    "two_sided": two_sided,
    "not_bracketable": d['markets'] - two_sided,
    "best_ask_floor": round(rows[0]['total'], 4),
    "floor_q": rows[0]['q'],
    "tiers": tiers,
    "scan_time_s": d['scan_time'],
    "note": f"raw supp scan showed {dup_removed} transient pagination duplicate(s) (Jablonec -2.5 at liq 5474.93+5670.96; fresh fetches show single market id 5198327 liq 5670.96) - stats deduped",
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)
print()
print("Deduped floor leaders (top 8):")
for r in rows[:8]:
    print(f"  {r['total']:.3f} | Y{r['yes']:.3f}+N{r['no']:.3f} | liq {r['liq']:.0f} | {r['q']}")

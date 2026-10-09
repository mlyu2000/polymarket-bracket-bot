import json

TS = "2026-10-09T19:48Z"
supp = json.load(open('_tmp_cron_20261009T1948Z_supp_data.json'))
scan = json.load(open('_tmp_cron_20261009T1948Z_scan_data.json'))
scan.setdefault('paper_trades', 0)  # no detector opps -> paper.execute never called

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

near = supp['near']
band = [r for r in near if 1.0 <= r[0] <= 1.005]
seen = set()
band_u = []
for total, q, yp, np, liq in band:
    key = (round(total, 3), q[:50])
    if key not in seen:
        seen.add(key)
        band_u.append((total, q[:50], yp, np, liq))
cur_set = {t[:2] for t in band_u}
prev_set = {(round(x[0], 3), x[1]) for x in prev_band}
adds = sorted(cur_set - prev_set, key=lambda x: x[0])
drops = sorted(prev_set - cur_set, key=lambda x: x[0])
cur_map = {t[:2]: (t[2], t[3]) for t in band_u}
prev_map = {(round(x[0], 3), x[1]): (x[2], x[3]) for x in prev_band}
shifts = [(q, prev_map[k], cur_map[k]) for k in (cur_set & prev_set) for _, q in [k] if prev_map[k] != cur_map[k]]
brackets = [r for r in near if r[0] < 1.0]

floor = round(near[0][0], 3) if near else None
prev_floor = prev['best_ask_floor']
trend = "held" if floor == prev_floor else ("fell" if floor < prev_floor else "rose")

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(supp['t'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": scan['near_misses_asks0'],
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": [[round(t, 3), q, yp, np, liq] for t, q, yp, np, liq in band_u],
    "detector_opps": len(scan['opps']),
    "paper_trades": scan['paper_trades'],
    "note": (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        "FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
        "Band " + str(len(prev_band)) + "->" + str(len(band_u)) + ": adds " + (str([a[1] for a in adds]) if adds else "[]")
        + ", drops " + (str([d[1] for d in drops]) if drops else "[]") + ". "
        "Intra-band shifts: " + (str(shifts) if shifts else "none") + ". "
        "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
        "Detector opportunities: " + str(len(scan['opps'])) + ". True brackets (min-ask sum<1.00): " + str(len(brackets)) + " — no actionable arb. "
        "Paper trades " + str(scan['paper_trades']) + "."
    ),
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")
print("appended:", json.dumps(rec, indent=2))

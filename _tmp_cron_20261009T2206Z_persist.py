import json

TS = "2026-10-09T22:06Z"
supp = json.load(open('_tmp_cron_20261009T2206Z_supp_data.json'))
scan = {'markets': 500, 'scan_time': 48.6, 'opps': [], 'near_misses': []}
near_misses_asks0 = len(scan['near_misses'])

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

near = [(r['total'], r['q'][:50], r['yes'], r['no'], r['liq']) for r in supp]
band = [t for t in near if 1.0 <= t[0] <= 1.005]
seen = set()
band_u = []
for total, q, yp, np_, liq in band:
    key = (round(total, 3), q)
    if key not in seen:
        seen.add(key)
        band_u.append((total, q, yp, np_, liq))
cur_set = {(round(t, 3), q) for t, q, _, _, _ in band_u}
prev_set = {(round(x[0], 3), x[1]) for x in prev_band}
adds = sorted(cur_set - prev_set, key=lambda x: x[0])
drops = sorted(prev_set - cur_set, key=lambda x: x[0])
cur_map = {(round(t, 3), q): (yp, np_) for t, q, yp, np_, _ in band_u}
prev_map = {(round(x[0], 3), x[1]): (x[2], x[3]) for x in prev_band}
shifts = [(k[1], prev_map[k], cur_map[k]) for k in (cur_set & prev_set) if prev_map[k] != cur_map[k]]
brackets = [t for t in near if t[0] < 1.0]

floor = round(near[0][0], 3) if near else None
prev_floor = prev['best_ask_floor']
trend = "held" if floor == prev_floor else ("fell" if floor < prev_floor else "rose")

tier2 = sorted({round(r['total'], 3) for r in supp if r['total'] > 1.005})
tier2_top = tier2[0] if tier2 else None
tier2_names = [r['q'][:40] for r in supp if tier2_top is not None and round(r['total'], 3) == tier2_top][:5]

rec = {
    "ts_utc": TS,
    "markets": scan['markets'],
    "scan_time_s": round(scan['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": near_misses_asks0,
    "priced_minask": len(near),
    "best_ask_floor": floor,
    "near_1.000_1.005": [[round(t, 3), q, yp, np_, liq] for t, q, yp, np_, liq in band_u],
    "detector_opps": len(scan['opps']),
    "paper_trades": 0,
    "note": (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        "FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
        "Band " + str(len(prev_band)) + "->" + str(len(band_u)) + ": adds " + (str([a[1] for a in adds]) if adds else "[]")
        + ", drops " + (str([d[1] for d in drops]) if drops else "[]") + ". "
        "Intra-band price shifts: " + (str(shifts) if shifts else "none") + ". "
        "Next tier " + str(tier2_top) + " (" + ", ".join(tier2_names) + "). "
        "Priced " + str(prev['priced_minask']) + "->" + str(len(near)) + ". "
        "Detector opportunities: " + str(len(scan['opps'])) + ". True brackets (min-ask sum<1.00): " + str(len(brackets)) + " - no actionable arb. "
        "Paper trades 0."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")
print("appended:", json.dumps(rec, indent=1))

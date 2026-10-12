import json

TS = "2026-10-09T15:35Z"
supp = json.load(open('_tmp_cron_20261009T1520Z_supp_data.json'))
verbatim = {'scan_time': 49.2, 'opps': 0, 'near_misses_asks0': 0}

lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
assert lines[-1].startswith('{"ts_utc": "2026-10-09T15:35Z"'), "unexpected tail"
lines.pop()  # remove the entry with truncation-mismatched note
prev = json.loads(lines[-2])
prev_band = [tuple(x) for x in prev['near_1.000_1.005']]

near = supp['near']
band = [r for r in near if 1.0 <= r[0] <= 1.005]
seen = set()
band_u = []
for total, q, yp, np, liq in band:
    key = (round(total, 3), q)
    if key not in seen:
        seen.add(key)
        band_u.append((total, q, yp, np, liq))

# match prev band by prefix (prev used [:60], supp used [:50])
def prev_key(t):
    return t[1][:50]
cur_by_q = {t[1]: t for t in band_u}
prev_by_q = {prev_key(t): t for t in prev_band}
adds = [q for q in cur_by_q if q not in prev_by_q]
drops = [t[1] for k, t in prev_by_q.items() if k not in cur_by_q]
shifts = []
for q, t in cur_by_q.items():
    if q in prev_by_q:
        p = prev_by_q[q]
        if (p[2], p[3]) != (t[2], t[3]):
            shifts.append((q, (p[2], p[3]), (t[2], t[3])))

floor = round(near[0][0], 3)
prev_floor = prev['best_ask_floor']
trend = "held" if floor == prev_floor else ("fell" if floor < prev_floor else "rose")

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(supp['t'], 1),
    "brackets_verbatim": verbatim['opps'],
    "near_misses_verbatim_asks0": verbatim['near_misses_asks0'],
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": [[round(t, 3), q, yp, np, liq] for t, q, yp, np, liq in band_u],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        "FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
        "Band " + str(len(prev_band)) + "->" + str(len(band_u)) + " (names truncated [:50] this run): adds "
        + (str(adds) if adds else "[]") + ", drops " + (str(drops) if drops else "[]") + ". "
        "Intra-band shifts: " + (str(shifts) if shifts else "none") + ". "
        "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
        "Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 — no actionable arb. Paper trades 0."
    ),
}

with open('results/cron_scan_history.jsonl', 'w') as f:
    for l in lines:
        f.write(l if l.endswith("\n") else l + "\n")
    f.write(json.dumps(rec) + "\n")
print("rewrote history with corrected entry")
print("adds:", adds, "drops:", drops, "shifts:", shifts)

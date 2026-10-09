import json

TS = "2026-10-09T12:01Z"

scan = {'scan_time': 47.0, 'markets': 500, 'opps': [], 'near_misses': []}
with open('_tmp_cron_20261009T1201Z_supp_data.json') as f:
    supp = json.load(f)

rows = supp['band']
floor = rows[0]['sum'] if rows else None
near = [[r['sum'], r['q'][:50], r['yes'], r['no'], r['liq']] for r in rows if 1.0 <= r['sum'] <= 1.005]
brackets = [r for r in rows if r['sum'] < 1.0]

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
prev_floor = prev['best_ask_floor']
prev_band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
cur_band = sorted({q for _, q, *_ in near})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]

if floor is None:
    trend = "no-priced"
elif floor < prev_floor:
    trend = "fell"
elif floor > prev_floor:
    trend = "rose"
else:
    trend = "held"

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    "min-ask floor authoritative. FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
    "Band " + str(len(prev_band)) + "->" + str(len(cur_band)) + ": adds " + (str(adds) if adds else "none")
    + ", drops " + (str(drops) if drops else "none") + ". "
    + "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
    + "Detector opportunities: " + str(supp['detector_opps']) + ". "
    + "True brackets (min-ask sum<1.00): " + str(len(brackets)) + " — no actionable arb. "
    + "Paper trades " + str(len(scan['opps'])) + "."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(supp['elapsed'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "detector_opps": supp['detector_opps'],
    "paper_trades": 0,
    "note": note,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")

print("prev_ts:", prev['ts_utc'], "prev_floor:", prev_floor)
print("appended:", json.dumps(rec, indent=2)[:2500])

import json

TS = "2026-10-09T11:15Z"

# Verbatim scan results (stdout): 500 markets in 46.5s, 0 brackets, 0 asks0 near-misses
scan = {'scan_time': 46.5, 'markets': 500, 'opps': [], 'near_misses': []}
with open('_tmp_cron_20261009T1115Z_supp_data.json') as f:
    supp = json.load(f)

rows = supp['rows']
floor = rows[0]['sum'] if rows else None
near = [[r['sum'], r['q'][:50], r['yes'], r['no'], r['liq']] for r in rows if 1.0 <= r['sum'] <= 1.005]
brackets = [r for r in supp['all_rows'] if r[0] < 1.0]

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
prev_floor = prev['best_ask_floor']
prev_band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
cur_band = sorted({q for _, q, *_ in near})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]

if floor < prev_floor:
    trend = "fell back"
elif floor > prev_floor:
    trend = "rose"
else:
    trend = "held"
adds_s = str(adds) if adds else "none"
drops_s = str(drops) if drops else "none"

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    "min-ask floor authoritative. FLOOR " + str(prev_floor) + "->" + str(floor) + " " + trend + ". "
    "Band " + str(len(prev_band)) + "->" + str(len(near)) + ": adds " + adds_s + ", drops " + drops_s + ". "
    "Priced " + str(prev['priced_minask']) + "->" + str(supp['priced']) + ". "
    "Detector (true min-ask, sum<1.00): " + str(len(brackets)) + " brackets — no actionable arb. "
    "Paper trades " + str(len(scan['opps'])) + "."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(scan['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": floor,
    "near_1.000_1.005": near,
    "paper_trades": 0,
    "note": note,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")

print("appended:", json.dumps(rec, indent=2)[:2000])

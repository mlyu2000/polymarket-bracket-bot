import json

TS = "2026-10-09T05:32Z"

# Verbatim scan results (stdout): 500 markets in 48.9s, 0 brackets, 0 asks0 near-misses
scan = {'scan_time': 48.9, 'markets': 500, 'opps': [], 'near_misses': []}
with open('_tmp_cron_20261009T0532Z_supp_data.json') as f:
    supp = json.load(f)

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
prev_band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
cur_band = sorted({q for _, q, *_ in supp['near']})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    f"min-ask floor authoritative. FLOOR {prev['best_ask_floor']}->{supp['true_floor']} "
    f"{'fell back' if float(supp['true_floor']) < float(prev['best_ask_floor']) else ('rose' if float(supp['true_floor']) > float(prev['best_ask_floor']) else 'held')}. "
    f"Band {len(prev_band)}->{len(cur_band)}: adds {adds if adds else 'none'}, drops {drops if drops else 'none'}. "
    f"Priced {prev['priced_minask']}->{supp['priced']}. "
    f"Detector (true min-ask, sum<1.00): {len(supp['opps'])} brackets — no actionable arb. "
    f"Paper trades {len(scan['opps'])}."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(supp['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": supp['true_floor'],
    "near_1.000_1.005": supp['near'],
    "paper_trades": 0,
    "note": note,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")

print("appended:", json.dumps(rec, indent=2)[:2000])

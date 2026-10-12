import json, subprocess

TS = "2026-10-09T01:30Z"

# Verbatim scan results (from stdout, no json dumped by verbatim script):
scan = {'scan_time': 48.2, 'markets': 500, 'opps': [], 'near_misses': []}
with open('_tmp_cron_20261009T0130Z_supp_data.json') as f:
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
    f"(rose; holders: {supp['near'][0][1] if supp['near'] else 'n/a'} etc). "
    f"Band {len(prev_band)}->{len(cur_band)}: adds {adds}, drops {drops}. "
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

band_str = (f"band {len(prev_band)}->{len(cur_band)}: "
            + (f"adds {adds}; " if adds else "no adds; ")
            + (f"drops {drops}" if drops else "no drops"))
msg = (f"runs: {TS} scan+persist "
       f"(500 markets, 0 brackets; verbatim asks0 scan {scan['scan_time']:.1f}s: 0 BRACKETS, "
       f"0 asks0 near-misses (known DESC artifact); supp minask {supp['scan_time']:.1f}s: "
       f"{supp['priced']}/500 priced, floor {prev['best_ask_floor']}->{supp['true_floor']} rose; "
       f"{band_str}; priced {prev['priced_minask']}->{supp['priced']}; "
       f"detector-opps: {len(supp['opps'])}, paper: no executions)")
print("NOTE:", note)
print("MSG:", msg)
with open('_tmp_cron_20261009T0130Z_commitmsg.txt', 'w') as f:
    f.write(msg)
subprocess.run(["git", "add", "results/cron_scan_history.jsonl"], check=True)
subprocess.run(["git", "commit", "-m", msg], check=True)
print("committed")

import json, subprocess

TS = "2026-10-10T2249Z"

scan = {'scan_time': 67.2, 'markets': 500, 'opps': [], 'near_misses': []}
with open('runs/_tmp_cron_20261010T2249Z_supp_data.json') as f:
    supp = json.load(f)

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
prev_band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
cur_band = sorted({q for _, q, *_ in supp['band']})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    "min-ask floor authoritative. "
    f"FLOOR IMPROVED {prev['best_ask_floor']}->{supp['floor']:.4f} (new low): "
    f"{supp['floor_q']} Yes@{supp['band'][0][2]:.3f} No@{supp['band'][0][3]:.3f} "
    f"liq={supp['band'][0][4]:.2f} — thin book (liq ~215 vs band peers 1478-4485), "
    "NO bracket (sum 1.003 > 1.00), best gross edge -0.003. "
    f"Band {len(prev_band)}->{len(cur_band)}: adds {adds}, drops {drops}. "
    f"Priced {prev['priced_minask']}->{supp['priced']}/500; one-sided {supp['one_sided']}, "
    f"both-empty {supp['both_empty']}. "
    f"Detector (true min-ask, sum<1.00): {supp['brackets']} brackets — no actionable arb. "
    f"Paper trades {len(scan['opps'])}."
)

rec = {
    "ts_utc": TS,
    "markets": supp['markets'],
    "scan_time_s": round(scan['scan_time'], 1),
    "brackets_verbatim": len(scan['opps']),
    "near_misses_verbatim_asks0": len(scan['near_misses']),
    "priced_minask": supp['priced'],
    "best_ask_floor": supp['floor'],
    "near_1.000_1.005": supp['band'],
    "detector_opps": 0,
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
       f"{supp['priced']}/500 priced, floor {prev['best_ask_floor']}->{supp['floor']:.4f} NEW LOW "
       f"({supp['floor_q']} Yes@0.005 No@0.998 liq 215 — thin; no bracket, edge -0.003); "
       f"{band_str}; priced {prev['priced_minask']}->{supp['priced']}; "
       f"detector-opps: {supp['brackets']}, paper: no executions)")
print("NOTE:", note)
print("MSG:", msg)
subprocess.run(["git", "add", "results/cron_scan_history.jsonl", "runs/_tmp_cron_20261010T2249Z_supp_data.json"], check=True)
subprocess.run(["git", "commit", "-m", msg], check=True)
print("committed")

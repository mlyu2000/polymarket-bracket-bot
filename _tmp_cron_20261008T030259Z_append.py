import json

with open('runs/scan_20261008T030521Z.json') as f:
    d = json.load(f)

band = [[r['sum'], r['q'][:50], r['yes'], r['no'], r['liq']] for r in d['band_rows']]
row = {
    "ts_utc": "2026-10-08T03:05Z",
    "markets": d['markets'],
    "scan_time_s": 48.2,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": d['priced'],
    "best_ask_floor": d['floor'],
    "near_1.000_1.005": band,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. Floor unchanged vs 20261008T024922Z (6th consecutive).",
}
line = json.dumps(row, ensure_ascii=False)
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(line + "\n")
print(line)

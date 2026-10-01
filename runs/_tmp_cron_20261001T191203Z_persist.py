import json

d = json.load(open('runs/_tmp_cron_20261001T191203Z_data.json'))
best = d['best_all_top']
entry = {
    "scan_utc": "2026-10-01T19:12Z",
    "markets": d["markets"],
    "scan_time_s": round(d["scan_time"], 1),
    "brackets_verbatim": len(d["opps"]),
    "near_misses_verbatim_asks0": 0,
    "brackets_true_minask": sum(1 for t, *_ in best if t < 1.0),
    "near_misses_true_minask": sum(1 for t, *_ in best if 1.0 <= t <= 1.005),
    "best_ask_floor": d["floor"],
    "priced_markets": 84,
    "top_true_sums": [
        {"sum": t, "yes": y, "no": n, "liq": l, "q": q}
        for (t, q, y, n, l) in best[:3]
    ],
}
with open('runs/scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
json.dump(entry, open('runs/scan_latest.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(entry, ensure_ascii=False, indent=1))

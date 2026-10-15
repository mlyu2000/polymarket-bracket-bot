import json

entry = {
    "ts_utc": "2026-10-15T0424Z",
    "markets": 500,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "with_both_asks": 65,
    "two_sided": 65,
    "not_bracketable": 435,
    "best_ask_floor": 1.004,
    "floor_q": "Exact Score: Brentford FC 0 - 5 Liverpool FC?",
    "tiers": {"le1.005": 8, "le1.010": 15, "le1.020": 27, "le1.050": 48, "lt1.000": 0},
    "scan_time_s": 80.9,
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)

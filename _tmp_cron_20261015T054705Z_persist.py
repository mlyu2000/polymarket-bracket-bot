import json

entry = {
    "ts_utc": "2026-10-15T054705Z",
    "markets": 500,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "with_both_asks": 64,
    "two_sided": 64,
    "not_bracketable": 436,
    "best_ask_floor": 1.003,
    "floor_q": "Spread: FK Jablonec (-2.5)",
    "tiers": {"le1.005": 8, "le1.010": 17, "le1.020": 30, "le1.050": 53, "lt1.000": 0},
    "scan_time_s": 57.8,
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)

import json

entry = {
    "ts_utc": "2026-10-15T0532Z",
    "markets": 500,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "with_both_asks": 62,
    "two_sided": 62,
    "not_bracketable": 438,
    "best_ask_floor": 1.003,
    "floor_q": "Spread: FK Jablonec (-2.5)",
    "tiers": {"le1.005": 9, "le1.010": 18, "le1.020": 28, "le1.050": 51, "lt1.000": 0},
    "scan_time_s": 60.6,
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)

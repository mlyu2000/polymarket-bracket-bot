import json

entry = {
    "ts_utc": "2026-10-12T2222Z",
    "markets": 500,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "two_sided": 66,
    "yes_only": 425,
    "no_only": 0,
    "empty": 9,
    "best_ask_floor": 1.001,
    "floor_q": "Will the highest temperature in Atlanta be between 80-81\u00b0F on October 14?",
    "band_le_1005": 3,
    "tiers": {"1.005": 3, "1.01": 14, "1.02": 27, "1.03": 30, "1.05": 45},
    "best_gross_edge": 0.001,
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)

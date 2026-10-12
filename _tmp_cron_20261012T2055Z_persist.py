import json

entry = {
    "ts_utc": "2026-10-12T2055Z",
    "markets": 500,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "two_sided": 69,
    "yes_only": 422,
    "no_only": 0,
    "empty": 9,
    "best_ask_floor": 1.001,
    "floor_q": "Will the highest temperature in Atlanta be between 80-81\u00b0F on October 14?",
    "band_le_1005": 2,
    "tiers": {"1.005": 2, "1.01": 13, "1.02": 28, "1.03": 32, "1.05": 44},
    "best_gross_edge": 0.001,
}

line = json.dumps(entry, ensure_ascii=False)
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED:", line)

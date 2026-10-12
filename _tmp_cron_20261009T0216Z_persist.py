import json, datetime

rec = {
    "ts_utc": "2026-10-09T02:16Z",
    "markets": 500,
    "scan_time_s": 49.9,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 81,
    "best_ask_floor": 1.002,
    "near_1.000_1.005": [
        [1.002, "Exact Score: BV Borussia 09 Dortmund 0 - 3 SV Werd", 0.005, 0.997, 35458.96527],
        [1.003, "FC Nordsj\u00e6lland vs. Odense BK: O/U 8.5", 0.013, 0.99, 3394.69282],
        [1.004, "Exact Score: Montpellier HSC 0 - 3 Grenoble Foot 3", 0.008, 0.996, 7037.32833],
        [1.005, "Exact Score: West Ham United FC 0 - 3 Queens Park ", 0.008, 0.997, 26114.85696],
        [1.005, "Kashiwa Reysol vs. Vissel K\u014dbe: O/U 7.5", 0.01, 0.995, 11536.48279],
    ],
    "supp_scan_note": "min-ask floor scan; verbatim asks0 near-miss block is known DESC-sort artifact",
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print("appended:", rec["ts_utc"])

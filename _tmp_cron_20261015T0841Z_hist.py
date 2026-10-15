import json

entry = {
    "run_ts_utc": "20261015T0841Z",
    "markets": 500,
    "scan_time_s": 62.7,
    "brackets": [],
    "near_miss_count": 11,
    "near_misses_top": [
        {"sum": 1.001, "q": "Bank of Japan decreases interest rates by 50+ bps af", "yes": 0.002, "no": 0.999, "liq": 824.30607},
        {"sum": 1.002, "q": "Spread: Lincoln Red Imps FC (-2.5)", "yes": 0.003, "no": 0.999, "liq": 4011.97279},
        {"sum": 1.003, "q": "Spread: FK Jablonec (-2.5)", "yes": 0.005, "no": 0.998, "liq": 5795.06545},
        {"sum": 1.003, "q": "Spread: MH Hapoel Be'er Sheva (-2.5)", "yes": 0.009, "no": 0.994, "liq": 6207.574},
        {"sum": 1.004, "q": "Exact Score: Venezia FC 4 - 3 SSC Napoli?", "yes": 0.006, "no": 0.998, "liq": 21547.37289},
    ],
    "floor": 1.001,
}
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("APPENDED run_ts_utc", entry["run_ts_utc"])

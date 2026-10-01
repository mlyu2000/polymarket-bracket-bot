import json

entry = {
    "scan_utc": "2026-10-01T19:52Z",
    "markets": 500,
    "scan_time_s": 48.6,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "brackets_true_minask": 0,
    "near_misses_true_minask": 1,
    "best_ask_floor": 1.001,
    "priced_markets": 82,
    "top_true_sums": [
        {"sum": 1.001, "yes": 0.003, "no": 0.998, "liq": 17892, "sz": 449,
         "q": "Will Elon Musk post 80-99 tweets from October 2 to October 9"},
        {"sum": 1.009, "yes": 0.010, "no": 0.999, "liq": 5234, "sz": 960,
         "q": "Spread: CA Platense (-3.5)"},
        {"sum": 1.009, "yes": 0.010, "no": 0.999, "liq": 5760, "sz": 1055,
         "q": "Spread: Sporting Kansas City (-3.5)"},
    ],
}
with open('runs/scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
json.dump(entry, open('runs/scan_latest.json', 'w'), indent=1, ensure_ascii=False)
print("persisted")

import json, time

TS = "20261015T132321Z"
with open(f"runs/_tmp_cron_{TS}_tiers.json", encoding="utf-8") as f:
    d = json.load(f)

top = d["top12"]
entry = {
    "run_ts_utc": TS,
    "markets": d["markets"],
    "scan_time_s": d["scan_time"],
    "brackets": 0,
    "near_miss_count": d["tiers"]["1.005"],
    "near_misses_top": [
        {"sum": r[0], "q": r[1], "yes": r[2], "no": r[3], "liq": r[4]}
        for r in top[:5]
    ],
    "floor": top[0][0] if top else None,
    "tiers": d["tiers"],
    "bracketable": d["one_sided"]["both"],
}
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("APPENDED:", entry["run_ts_utc"], "| floor:", entry["floor"], "| near_misses:", entry["near_miss_count"], "| tiers:", entry["tiers"])

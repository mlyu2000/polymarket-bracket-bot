import json

TS = "20261015T1305Z"
with open(f"runs/_tmp_cron_{TS}_supp_data.json", encoding="utf-8") as f:
    d = json.load(f)

entry = {
    "run_ts_utc": TS,
    "markets": d["markets"],
    "scan_time_s": round(d["scan_time"], 1),
    "brackets": d["brackets_below_098"],
    "near_miss_count": d["tiers"]["le1.005"],
    "near_misses_top": [
        {"sum": r["sum"], "q": r["q"], "yes": r["yes"], "no": r["no"], "liq": r["liq"]}
        for r in d["floor_top10"][:5]
    ],
    "floor": d["floor_top10"][0]["sum"] if d["floor_top10"] else None,
}
with open("results/cron_scan_history.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("APPENDED:", entry["run_ts_utc"], "| floor:", entry["floor"], "| near_misses:", entry["near_miss_count"])

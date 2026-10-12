import json

TS = "20261008T081804Z"
with open('_tmp_cron_20261008T0817Z_supp_data.json') as f:
    d = json.load(f)

snap = {
    "run": TS,
    "ts": "2026-10-08T08:18:04Z",
    "markets": d["markets"],
    "priced": d["priced"],
    "floor": d["floor"],
    "brackets_minask": sum(1 for r in d["top8"] if r["sum"] < 1.0),
    "detector_opps": 0,
    "band": d["band"],
    "top8": d["top8"],
    "band_rows": d["band_rows"],
    "scan_time_s": d["scan_time_s"],
}
# true_brackets from printed run = 0 across all 90 priced rows
with open(f"runs/scan_{TS}.json", "w") as f:
    json.dump(snap, f, indent=1)
with open("runs/scan_latest.json", "w") as f:
    json.dump(snap, f, indent=1)
print("persisted", TS, "floor", snap["floor"], "band", snap["band"], "priced", snap["priced"])

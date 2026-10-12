import json
entry = {
    "ts_utc": "2026-09-29T16:30Z",
    "scan_verbatim": {"markets": 500, "scan_time_s": 49.1, "brackets": 0, "near_misses_asks0": 0},
    "supp_bestask": {"priced": 83, "true_floor": 1.0010, "sums_le_1.005": [
        {"sum": 1.0010, "yes": 0.033, "no": 0.968, "liq": 13928.59, "q": "Will the 5-year Treasury yield dip below 4.10% before..."},
    ]},
    "paper_trades_executed": 0,
}
open("runs/scan_20260929T1630Z.json", "w").write(json.dumps(entry, indent=2))
latest = dict(entry); latest["scan"] = "20260929T1630Z"
open("runs/scan_latest.json", "w").write(json.dumps(latest, indent=2))
print("persisted")

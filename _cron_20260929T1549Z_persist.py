import json, time
entry = {
    "ts_utc": "2026-09-29T15:49Z",
    "scan_verbatim": {"markets": 500, "scan_time_s": 49.1, "brackets": 0, "near_misses_asks0": 0},
    "supp_minask": {"priced": 97, "true_floor": 1.0010, "sums_le_1.005": [
        {"sum": 1.0010, "yes": 0.033, "no": 0.968, "liq": 14005.80, "q": "Will the 5-year Treasury yield dip below 4.10% before..."},
        {"sum": 1.0030, "yes": 0.010, "no": 0.993, "liq": 843.86, "q": "Moldova vs. Faroe Islands: Faroe Islands 1st Half..."}
    ]},
    "paper_trades_executed": 0
}
open("runs/scan_20260929T1549Z.json","w").write(json.dumps(entry, indent=2))
latest = dict(entry); latest["scan"]="20260929T1549Z"
open("runs/scan_latest.json","w").write(json.dumps(latest, indent=2))
print("persisted")

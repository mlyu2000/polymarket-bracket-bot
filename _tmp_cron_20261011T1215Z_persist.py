import json, datetime
result = {
    "timestamp_utc": datetime.datetime.now(datetime.UTC).isoformat(),
    "markets": 500,
    "scan_time_s": 57.3,
    "brackets": 0,
    "near_misses": 0,
    "notes": "verbatim cron script; asks[0] near-miss known-invalid (DESC sort) per memory"
}
with open("runs/_tmp_cron_20261011T1215Z_scan_data.json", "w") as f:
    json.dump(result, f, indent=2)
print("persisted")

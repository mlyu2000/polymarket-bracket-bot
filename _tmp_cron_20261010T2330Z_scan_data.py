import json
data = {
    "ts": "2026-10-10T2330Z",
    "markets": 500,
    "scan_time": 48.7,
    "opps": 0,
    "near_misses_asks0": 0,
    "note": "verbatim script asks[0] near-miss check: 0 (known DESC artifact); true floor from supp minask: 1.0040"
}
with open('runs/_tmp_cron_20261010T2330Z_scan_data.json', 'w') as f:
    json.dump(data, f, indent=1)
print("scan data written")

import json

rec = {
    "ts_utc": "2026-10-10T0127Z",
    "markets": 500,
    "scan_time_s": 49.5,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 57,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2072.56055],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.010, 0.995, 12151.60476]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 1->2: Clermont/Red Star re-enters band (back at 1.005 after >1.005 excursion at 0109Z — 0109Z band was 1, now 2). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 58->57. Liq drift: Clermont 2072.6 (re-entry), Kyoto 12158.6->12151.6 (-0.06%), Chornomorets 1887.7->1889. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# verify
with open("results/cron_scan_history.jsonl") as f:
    lines = f.readlines()
print("total lines:", len(lines))
last = json.loads(lines[-1])
print("last ts:", last["ts_utc"], "floor:", last["best_ask_floor"], "band:", len(last["near_1.000_1.005"]))

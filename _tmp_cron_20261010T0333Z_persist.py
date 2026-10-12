import json

rec = {
    "ts_utc": "2026-10-10T0333Z",
    "markets": 500,
    "scan_time_s": 50.3,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 59,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1721.40335],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 4438.16886],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 8118.5811]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR recovered 1.004->1.005: Tigres UANL O/U 5.5 (1.004 last run) exited top-20 band. Band n=3 steady (Clermont, Kyoto, South Melbourne all 1.005; South Melbourne 4th consecutive). Next tier 1.006: CA Tigre/Banfield O/U 6.5 ENTERS (Yes@0.013 No@0.993, liq 1605.7); Chornomorets/Kharkiv O/U 7.5 (Yes@0.010 No@0.996, liq 1903.0); Falkirk/Dundee dropped out. Liq drift: Clermont 1721.4->1721.4 (flat), Kyoto 12562.9->4438.2 (-64.7% big drop), South Melbourne 8067.2->8118.6 (+0.6%). Priced 62->59. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

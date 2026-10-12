import json

rec = {
    "ts_utc": "2026-10-10T0348Z",
    "markets": 500,
    "scan_time_s": 53.0,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 62,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1721.40335],
        [1.005, "FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5", 0.01, 0.995, 1914.74793],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12202.51246],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 8137.15493]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR HELD at 1.005. Band grew n=3->n=4: FK Chornomorets/Kharkiv PROMOTED 1.006->1.005 (Yes@0.010 No@0.995, liq 1903.0->1914.7). Liq drift: Clermont 1721.4->1721.4 (flat), Kyoto 4438.2->12202.5 (+175%, recovers from last-run -64.7% crash), South Melbourne 8118.6->8137.2 (+0.2%, 5th consecutive). Next tier 1.006: CA Tigre/Banfield (1605.7->1633.0) + Falkirk/Dundee RETURNS at 1.006 (liq 1997.2). Priced 59->62. 1.010 tier now n=7 incl. high-liq FC Seoul/Jeju 83779 + Kent State/WMU 114130. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

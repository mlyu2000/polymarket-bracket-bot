import json

entry = {
    "ts_utc": "2026-10-10T0022Z",
    "markets": 500,
    "scan_time_s": 49.7,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 64,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1964.90155],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12133.75732],
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->2 identical composition (Clermont/Red Star, Kyoto/Machida both at 1.005). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 65->64. Liquidity drift: Clermont 1869.1->1964.9, Kyoto 3871.3->12133.8 (3.1x jump). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(entry) + "\n")

print("persisted:", entry["ts_utc"])

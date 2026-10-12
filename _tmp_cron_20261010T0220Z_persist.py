import json

rec = {
    "ts_utc": "2026-10-10T0220Z",
    "markets": 500,
    "scan_time_s": 48.0,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 57,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2074.0],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.010, 0.995, 12342.0]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 3->2: CA Uni\u00f3n vs. Defensa y Justicia EXITED band (dropped from 1.005 last run). Clermont + Kyoto steady at 1.005. Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 59->57. Liq drift: Clermont 2073.6->2074 (+0.02%), Kyoto 12113.7->12342 (+1.9%). 1.010 tier n=5 composition unchanged from prior run. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted")

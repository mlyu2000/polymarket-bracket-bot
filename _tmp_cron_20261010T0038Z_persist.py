import json

entry = {
    "ts_utc": "2026-10-10T0038Z",
    "markets": 500,
    "scan_time_s": 49.5,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 58,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2063.40045],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12133.75762],
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->2 identical composition (Clermont/Red Star, Kyoto/Machida both at 1.005). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 64->58 (-6). Liq drift: Clermont 1964.9->2063.4, Kyoto flat 12133.8. 1.010 tier: Fernando Mendoza dropped out, Dplus KIA Worlds (0.998+0.012) entered top 8. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(entry) + "\n")

print("persisted:", entry["ts_utc"])

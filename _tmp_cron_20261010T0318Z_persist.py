import json

rec = {
    "ts_utc": "2026-10-10T0318Z",
    "markets": 500,
    "scan_time_s": 50.6,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 62,
    "best_ask_floor": 1.004,
    "near_1.000_1.005": [
        [1.004, "Tigres de la UANL vs. Deportivo Toluca FC: Tigres de la UANL O/U 5.5", 0.009, 0.995, 3329.1051],
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1721.40335],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12562.88866],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 8067.2271]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.004 BROKEN - Tigres UANL O/U 5.5 (live match) at 1.004 Yes@0.009 No@0.995 liq=3329.1. During supp runs Tigres family re-priced rapidly (saw 1.002 Toluca O/U 5.5 liq=89.76 - below MIN_LIQUIDITY guard; 1.004 1st-Half O/U 4.5 liq=0.0 - dead book). Even at 1.004 the gross edge is -0.004 (still ABOVE parity, not actionable). 1.005 band n=3 steady: Clermont (liq 1809.6->1721.4 -4.9%), Kyoto 12505.6->12562.9 (+0.46%), South Melbourne 8017.5->8067.2 (+0.62%). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 56->62 (live Liga MX match influx). 1.010 tier n=7->8. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

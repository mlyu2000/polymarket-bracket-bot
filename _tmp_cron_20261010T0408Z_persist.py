import json

rec = {
    "ts_utc": "2026-10-10T0408Z",
    "markets": 500,
    "scan_time_s": 48.2,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 61,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2405.17995],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 14368.81898],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 8137.16535]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 HELD. Band n=4->3: Chornomorets/Kharkiv DEMOTED 1.005->1.006 (Yes@0.010 No@0.996, liq 2436.3). Band members: Clermont 1721.4->2405.2 (+39.7%), Kyoto 12202.5->14368.8 (+17.8%), South Melbourne 8137.2->8137.2 (+0.0%, 6th consecutive). Next tier 1.006: Chornomorets returns + Falkirk/Dundee (CA Tigre/Banfield exited). Priced 62->61. 1.010 tier n=7->10: BG Pathum United, Hapoel Be'er Sheva, Persija Jakarta entered. FC Seoul liq 83779->89927.4 (+7.3%), Kent State/WMU 114130->146092.1 (+28.0%). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

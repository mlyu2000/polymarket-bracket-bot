import json

rec = {
    "ts_utc": "2026-10-10T0436Z",
    "markets": 500,
    "scan_time_s": 51.5,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 63,
    "best_ask_floor": 1.001,
    "near_1.000_1.005": [
        [1.001, "Feyenoord Rotterdam vs. AZ: O/U 8.5", 0.011, 0.99, 5183.27593],
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2390.58843],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 26270.69152],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 5992.68555]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR BROKEN 1.005->1.001 - Feyenoord Rotterdam vs. AZ O/U 8.5 ENTERS band (Yes@0.011 No@0.990, liq 5183.3; gross edge still -0.001 ABOVE parity, NOT actionable). 1.005 band n=3 steady members (Clermont 2405.2->2390.6 -0.6%, Kyoto 14368.8->26270.7 +82.8%, South Melbourne 8137.2->5992.7 -26.4% streak broken). Chornomorets/Kharkiv absent from <=1.005 (demoted 0408Z, still out). Priced 61->63. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no positive gross edge anywhere, no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

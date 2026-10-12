import json

rec = {
    "ts_utc": "2026-10-10T0258Z",
    "markets": 500,
    "scan_time_s": 58.1,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 56,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1809.58635],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12505.59694],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 8017.5391]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band steady n=3: Clermont, Kyoto, South Melbourne all at 1.005 (South Melbourne confirmed on 2nd consecutive run after entering at 2200Z). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 57->56. Liq drift: Clermont 1747.2->1809.6 (+3.6%), Kyoto 12364.7->12505.6 (+1.14%), South Melbourne 6341->8017.5 (+26.4%). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

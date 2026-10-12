import json

rec = {
    "ts_utc": "2026-10-10T2200Z",
    "markets": 500,
    "scan_time_s": 47.5,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 57,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1747.24269],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12364.71796],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 6341.02501]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->3: South Melbourne vs Melbourne Victory ENTERS band at 1.005 (Yes@0.012 No@0.993, liq 6341) - first band appearance in recent history. Clermont + Kyoto steady at 1.005. Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 57->57. Liq drift: Clermont 2074->1747.2 (-15.8%), Kyoto 12342->12364.7 (+0.18%). 1.010 tier n=5->7: Mendoza passing yards + Iran 2027 AFC Asian Cup re-entered (FC Seoul, Kent State/Western Michigan, Nomme Kalju spread, Real Madrid spread, Lokomotiv Sofia/Plovdiv unchanged). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

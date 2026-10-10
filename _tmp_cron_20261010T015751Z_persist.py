import json

rec = {
    "ts_utc": "2026-10-10T0157Z",
    "markets": 500,
    "scan_time_s": 48.8,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 59,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "CA Unión vs. CSyD Defensa y Justicia: CSyD Defensa", 0.015, 0.99, 3757.05886],
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2073.64255],
        [1.005, "Kyōto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.010, 0.995, 12113.69543]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->3: CA Unión vs. Defensa y Justicia ENTERS band at 1.005 (Yes@0.015 No@0.990, liq 3757). Clermont + Kyoto steady at 1.005. Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 58->59. Liq drift: Clermont 2051.6->2073.6 (+1.1%), Kyoto 12127.7->12113.7 (-0.11%). 1.010 tier n=5: composition shift - Mendoza passing yards dropped out, Lokomotiv 1929 Sofia vs Lokomotiv Plovdiv entered (FC Seoul, Kent State/Western Michigan, Nomme Kalju spread, Real Madrid spread unchanged). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

with open("results/cron_scan_history.jsonl") as f:
    lines = f.readlines()
print("total lines:", len(lines))
last = json.loads(lines[-1])
print("last ts:", last["ts_utc"], "floor:", last["best_ask_floor"], "band:", len(last["near_1.000_1.005"]))

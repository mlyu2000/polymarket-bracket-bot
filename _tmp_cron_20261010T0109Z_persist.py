import json

rec = {
    "ts_utc": "2026-10-10T0109Z",
    "markets": 500,
    "scan_time_s": 57.3,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 58,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [[1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 12158.60407]],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->1: drops Clermont/Red Star (sum 1.005->>=1.006). Kyoto/Machida sole band member at 1.005. Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 58->58 (tier pass; supp pass saw 57 - intra-scan book churn). Liq drift: Kyoto 12133.8->12158.6 (+0.2%), Chornomorets 1820.8->1887.7. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# verify
with open("results/cron_scan_history.jsonl") as f:
    lines = f.readlines()
print("total lines:", len(lines))
last = json.loads(lines[-1])
print("last ts:", last["ts_utc"], "floor:", last["best_ask_floor"], "band:", len(last["near_1.000_1.005"]))

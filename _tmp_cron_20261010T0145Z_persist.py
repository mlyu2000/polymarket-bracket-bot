import json

rec = {
    "ts_utc": "2026-10-10T0145Z",
    "markets": 500,
    "scan_time_s": 45.3,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 58,
    "best_ask_floor": 1.005,
    "near_1.000_1.005": [
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2051.56139],
        ["1.005", "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.010, 0.995, 12127.69518]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR 1.005->1.005 held. Band 2->2 identical composition (Clermont/Red Star + Kyoto/Machida both at 1.005). Next tier 1.006 unchanged (Chornomorets/Kharkiv, Falkirk/Dundee). Priced 57->58. Liq drift: Clermont 2072.6->2051.6 (-1.0%), Kyoto 12151.6->12127.7 (-0.20%), Chornomorets 1889->1881.9. 1.010 tier n=5 unchanged (FC Seoul, Kent State/Western Michigan, Nomme Kalju spread, Real Madrid spread, Mendoza passing yards). Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
}
# fix accidental string key in tuple
rec["near_1.000_1.005"][1][0] = 1.005

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# verify
with open("results/cron_scan_history.jsonl") as f:
    lines = f.readlines()
print("total lines:", len(lines))
last = json.loads(lines[-1])
print("last ts:", last["ts_utc"], "floor:", last["best_ask_floor"], "band:", len(last["near_1.000_1.005"]))

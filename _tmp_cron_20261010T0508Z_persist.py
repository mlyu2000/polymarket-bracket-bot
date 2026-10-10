import json

rec = {
    "ts_utc": "2026-10-10T0508Z",
    "markets": 500,
    "scan_time_s": 50.5,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 66,
    "best_ask_floor": 1.001,
    "near_1.000_1.005": [
        [1.001, "Feyenoord Rotterdam vs. AZ: O/U 8.5", 0.011, 0.99, 5183.27593],
        [1.002, "Exact Score: Manchester United FC 0 - 0 Tottenham Hotspur FC", 0.042, 0.96, 88493.75363],
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2536.15349],
        [1.005, "FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5", 0.01, 0.995, 2521.43234],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 6943.24806],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 5761.2]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR HELD 1.001 (Feyenoord/AZ O/U 8.5 liq 5183.3 flat, gross edge -0.001 ABOVE parity, NOT actionable). Band grew n=4->6: Exact Score Man Utd 0-0 Tottenham ENTERS at 1.002 (Yes@0.042 No@0.960, liq 88493.8 - highest-liquidity sub-1.005 member ever seen, still no positive gross edge); Chornomorets/Kharkiv PROMOTED back 1.006->1.005 (liq 2436.3->2521.4). Band movers: Clermont 2390.6->2536.2 (+6.1%), Kyoto 26270.7->6943.2 (-73.6%), South Melbourne 5992.7->5761.2 (-3.9%). Next tier 1.006: Falkirk/Dundee RETURNS (liq 3220.5). Priced 63->66. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no positive gross edge anywhere, no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("persisted:", rec["ts_utc"])

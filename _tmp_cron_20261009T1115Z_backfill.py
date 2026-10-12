import json

# Backfill the 2026-10-09T11:00Z jsonl record (that run persisted runs/ but skipped jsonl).
# Source: runs/20261009T1100Z_scan.md + runs/_tmp_cron_20261009T1100Z_supp_out.txt
rec = {
    "ts_utc": "2026-10-09T11:00Z",
    "markets": 500,
    "scan_time_s": 50.7,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 92,
    "best_ask_floor": 1.002,
    "near_1.000_1.005": [
        [1.002, "Exact Score: BV Borussia 09 Dortmund 0 - 3 SV Werd", 0.005, 0.997, 65824.22269],
        [1.003, "Exact Score: BV Borussia 09 Dortmund 2 - 4 SV Werd", 0.005, 0.998, 5716.93897],
        [1.004, "Exact Score: Montpellier HSC 0 - 3 Grenoble Foot 3", 0.008, 0.996, 8333.38579],
        [1.004, "Exact Score: Racing Club de Lens 0 - 4 Olympique L", 0.011, 0.993, 39465.13279],
        [1.004, "Exact Score: West Ham United FC 0 - 3 Queens Park ", 0.008, 0.996, 29424.1428],
        [1.005, "Exact Score: BV Borussia 09 Dortmund 3 - 4 SV Werd", 0.007, 0.998, 5652.05749],
        [1.005, "FC Nordsj\u00e6lland vs. Odense BK: O/U 8.5", 0.015, 0.990, 7208.60868],
        [1.005, "Kashiwa Reysol vs. Vissel K\u014dbe: O/U 7.5", 0.010, 0.995, 32090.55573],
    ],
    "paper_trades": 0,
    "note": "backfilled from runs/20261009T1100Z_scan.md (jsonl append was skipped at the time). floor held 1.002; band 5->8; priced 85->92; detector-opps: 0; paper: no executions.",
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec) + "\n")
print("backfilled 11:00Z")

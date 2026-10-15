"""Append 1937Z cron scan to results/cron_scan_history.jsonl (local, unpushed)."""
import json

row = {
    "ts": "20261015T1937Z",
    "method": "provided(asks[0]) + detector + minask floor",
    "markets": 500,
    "scan_time_verbatim": 53.3,
    "brackets": 0,
    "near_miss_verbatim": 0,
    "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth",
    "floor_min_ask": 1.001,
    "leader": "Bank of Japan decreases interest rates by 50+ bps after the ",
    "leader_liq": 1308.8,
    "two_sided": 57,
    "not_bracketable": 443,
    "tiers": {
        "<1.000": 0,
        "<=1.005": 2,
        "<=1.010": 4,
        "<=1.020": 10,
        "<=1.050": 36,
    },
    "top12": [
        {"total": 1.001, "q": "Bank of Japan decreases interest rates by 50+ bps after the ", "liq": 1308.8},
        {"total": 1.004, "q": "Bitcoin more valuable than any company before 2027?", "liq": 3928.9},
        {"total": 1.008, "q": "Will Democrats win 12 or more House seats in Penns", "liq": 14339.8},
        {"total": 1.010, "q": "Will the highest temperature in Miami be between 8", "liq": 4011.2},
        {"total": 1.012, "q": "Exact Score: Manchester City FC 0 - 2 Ipswich Town", "liq": 11110.4},
        {"total": 1.017, "q": "Z.ai #3 AI Lab", "liq": 392.0},
        {"total": 1.020, "q": "Odisha FC", "liq": 7270.8},
        {"total": 1.020, "q": "Nyiregyhaza O/U 2.5", "liq": 2235.0},
        {"total": 1.020, "q": "Washington State O/U 51.5", "liq": 15990.5},
        {"total": 1.030, "q": "Aston Villa vs Viking BTTS", "liq": 27411.0},
    ],
    "notes": "floor 1.001 HELD (33rd consecutive scan); BoJ leader liq 1240.2->1308.8 (+5.5%, zigzag rebound continues — pair low 1060.8 -> high 1308.8 across 56 min, sum unchanged 1.001); two_sided 53->57 (+4 — first re-expansion after 1900Z hard decrowd); tier bands marginally re-crowded: le1.005 2->2 flat, le1.010 4->4 flat, le1.020 9->10 (+1), le1.050 34->36 (+2) — early ask-side return; Bitcoin>any-co liq 3928.94623 byte-identical (12th consecutive scan, sum 1.004, sole surviving frozen book); not_bracketable 447->443 (88.6%)",
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(row) + "\n")
print("appended history row: ts=20261015T1937Z")

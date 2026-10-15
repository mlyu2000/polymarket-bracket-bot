"""Append this run's min-ask diagnostic to results/cron_scan_history.jsonl (local, unpushed)."""
import json

entry = {
    "ts": "2026-10-15T16:10Z",
    "markets": 500,
    "scan_time_verbatim": 55.9,
    "scan_time_minask": 56.8,
    "brackets": 0,
    "near_miss_verbatim": 0,
    "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth",
    "floor_min_ask": 1.001,
    "leader": "Bank of Japan decreases interest rates by 50+ bps after",
    "leader_liq": 1335.4,
    "tiers": {"<=1.050": 68, "<=1.020": 39, "<=1.010": 28, "<=1.005": 14, "<1.000": 0},
    "two_sided": 97,
    "not_bracketable": 403,
    "top12": [
        {"total": 1.001, "q": "Bank of Japan decreases interest rates by 50+ bps after", "liq": 1335.4},
        {"total": 1.002, "q": "Spread: Lincoln Red Imps FC (-2.5)", "liq": 15582.7},
        {"total": 1.002, "q": "Spread: FK Jablonec (-2.5)", "liq": 12507.1},
        {"total": 1.004, "q": "Bitcoin more valuable than any company before 2027?", "liq": 3928.9},
        {"total": 1.004, "q": "Spread: FC Thun (-2.5)", "liq": 9862.2},
        {"total": 1.004, "q": "Spread: FC Thun (-3.5)", "liq": 5305.7},
        {"total": 1.004, "q": "Spread: FK Jablonec (-3.5)", "liq": 13209.8},
        {"total": 1.004, "q": "Spread: FK Kauno Žalgiris (-1.5)", "liq": 16986.3},
        {"total": 1.005, "q": "Spread: Lillestrøm SK (-2.5)", "liq": 42211.9},
        {"total": 1.005, "q": "Spread: Páfos FC (-2.5)", "liq": 17089.8},
        {"total": 1.005, "q": "Spread: Inter Club d'Escaldes (-2.5)", "liq": 17460.7},
        {"total": 1.005, "q": "Spread: KF Egnatia Rrogozhinë (-2.5)", "liq": 19242.5},
    ],
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended history entry")

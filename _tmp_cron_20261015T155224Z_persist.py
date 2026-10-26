"""Append this run's min-ask diagnostic to results/cron_scan_history.jsonl (local, unpushed)."""
import json

entry = {
    "ts": "2026-10-15T15:56Z",
    "markets": 500,
    "scan_time_verbatim": 74.7,
    "scan_time_minask": 60.5,
    "brackets": 0,
    "near_miss_verbatim": 0,
    "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth",
    "floor_min_ask": 1.001,
    "leader": "Bank of Japan decreases interest rates by 50+ bps after",
    "leader_liq": 1425.8,
    "tiers": {"<=1.050": 68, "<=1.020": 34, "<=1.010": 27, "<=1.005": 15, "<1.000": 0},
    "two_sided": 87,
    "not_bracketable": 413,
    "top12": [
        {"total": 1.001, "q": "Bank of Japan decreases interest rates by 50+ bps after", "liq": 1425.8},
        {"total": 1.002, "q": "Spread: Lincoln Red Imps FC (-2.5)", "liq": 17942.0},
        {"total": 1.002, "q": "Spread: FK Jablonec (-2.5)", "liq": 11524.4},
        {"total": 1.003, "q": "Spread: Lillestrøm SK (-2.5)", "liq": 32314.0},
        {"total": 1.004, "q": "Bitcoin more valuable than any company before 2027?", "liq": 3928.9},
        {"total": 1.004, "q": "Spread: FC Thun (-2.5)", "liq": 17242.1},
        {"total": 1.004, "q": "Spread: FC Thun (-3.5)", "liq": 3697.7},
        {"total": 1.004, "q": "Spread: FK Jablonec (-3.5)", "liq": 1527.9},
        {"total": 1.004, "q": "Spread: Páfos FC (-3.5)", "liq": 4453.2},
        {"total": 1.004, "q": "Spread: FK Kauno Žalgiris (-1.5)", "liq": 22944.6},
        {"total": 1.004, "q": "Spread: Inter Club d'Escaldes (-2.5)", "liq": 28500.9},
        {"total": 1.004, "q": "Spread: Kuopion PS (-3.5)", "liq": 8322.0},
    ],
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended history entry")

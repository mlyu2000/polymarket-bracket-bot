"""Append this run's min-ask diagnostic to results/cron_scan_history.jsonl (local, unpushed)."""
import json

entry = {
    "ts": "2026-10-15T17:08Z",
    "markets": 500,
    "scan_time_verbatim": 54.4,
    "scan_time_minask": 56.2,
    "brackets": 0,
    "near_miss_verbatim": 0,
    "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth",
    "floor_min_ask": 1.001,
    "leader": "Bank of Japan decreases interest rates by 50+ bps after",
    "leader_liq": 1145.5,
    "tiers": {"<=1.050": 46, "<=1.020": 22, "<=1.010": 18, "<=1.005": 9, "<1.000": 0},
    "two_sided": 73,
    "not_bracketable": 427,
    "structural_event": "ALL 24 exact-score markets (Bologna-Inter, Brentford-Liverpool, Venezia-Napoli, Strasbourg-PSG) lost NO-side asks in 16 min (kickoff window, Serie A/Ligue 1 tonight CET): NO books now bid-only (mirror neg-risk posts 0.001-0.01 vs YES asks 0.007-0.015), YES asks still present but NO leg unpurchasable -> 14 previously-two-sided exact-score markets dropped out of two-sided set (81->73); frozen-book era ENDS (byte-identical liq 4+ scans broken)",
    "top12": [
        {"total": 1.001, "q": "Bank of Japan decreases interest rates by 50+ bps after", "liq": 1145.5},
        {"total": 1.002, "q": "Spread: FK Jablonec (-2.5)", "liq": 17239.9},
        {"total": 1.002, "q": "Spread: Lincoln Red Imps FC (-2.5)", "liq": 15135.5},
        {"total": 1.004, "q": "Bitcoin more valuable than any company before 2027?", "liq": 3928.9},
        {"total": 1.004, "q": "Spread: FC Thun (-2.5)", "liq": 14309.7},
        {"total": 1.004, "q": "Spread: FC Thun (-3.5)", "liq": 1229.2},
        {"total": 1.004, "q": "Spread: FK Jablonec (-3.5)", "liq": 642.3},
        {"total": 1.004, "q": "Spread: Páfos FC (-2.5)", "liq": 16847.9},
        {"total": 1.004, "q": "Spread: Páfos FC (-3.5)", "liq": 1593.9},
        {"total": 1.008, "q": "Spread: HNK Hajduk Split (-3.5)", "liq": 109.8},
        {"total": 1.008, "q": "Will Democrats win 12 or more House seats in Pennsylvania?", "liq": 14692.4},
        {"total": 1.009, "q": "Spread: FC Viktoria Plzeň (-3.5)", "liq": 2308.7},
    ],
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended history entry")

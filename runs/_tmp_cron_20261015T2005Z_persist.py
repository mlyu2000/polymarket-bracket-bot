import json, subprocess, datetime

TS = "20261015T2005Z"
out = subprocess.run(["cat", f"runs/_tmp_cron_{TS}_supp_out.txt"], capture_output=True, text=True).stdout

data = {
    "ts": "2026-10-15T20:05Z",
    "markets": 500,
    "brackets": 0,
    "near_misses_verbatim": 0,
    "floor": 1.001,
    "floor_market": "Bank of Japan decreases interest rates by 50+ bps after the December 2026 meeting",
    "floor_legs": "Y0.002 N0.999",
    "floor_liq": 1298.50034,
    "scan_time_s": 55.8,
    "floor_scan_time_s": 53.6,
    "two_sided": 59,
    "not_bracketable": 441,
    "tiers": {"le1.050": 39, "le1.020": 13, "le1.010": 8, "le1.005": 3, "lt1.000": 0},
    "top_floor": [
        [1.0010, "Bank of Japan decreases interest rates by 50+ bps after the December 2026 meeting", 0.002, 0.999, 1298.50034],
        [1.0020, "Will the highest temperature in Sao Paulo be 31C or higher on October 15", 0.003, 0.999, 4824.47855],
        [1.0040, "Bitcoin more valuable than any company before 2027?", 0.018, 0.986, 3928.94623],
        [1.0070, "Exact Score: Manchester City FC 0 - 2 Ipswich Town FC?", 0.012, 0.995, 11332.6595],
        [1.0080, "Spread: FC Thun (-2.5)", 0.009, 0.999, 21735.21801],
        [1.0080, "Will Democrats win 12 or more House seats in Pennsylvania in the 2026 House elections", 0.029, 0.979, 14708.45961],
        [1.0090, "Spread: FK Kauno Zalgiris (-4.5)", 0.010, 0.999, 8607.23419],
        [1.0090, "Spread: FK Kauno Zalgiris (-5.5)", 0.010, 0.999, 8632.14316],
        [1.0170, "Will Z.ai be the #3 AI Lab at the end of October 2026", 0.019, 0.998, 409.76002],
        [1.0200, "Aston Villa FC vs. Viking FK: Both Teams to Score", 0.570, 0.450, 27584.0537],
    ],
    "verbatim_scan_out": out,
}
with open(f"runs/_tmp_cron_{TS}_supp_data.json", "w") as f:
    json.dump(data, f, indent=2)

hist = {
    "ts": "2026-10-15T20:05Z",
    "markets": 500,
    "brackets": 0,
    "floor": 1.001,
    "two_sided": 59,
    "tiers": data["tiers"],
}
with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(hist) + "\n")

print("persisted:", f"runs/_tmp_cron_{TS}_supp_data.json", "+ history line")

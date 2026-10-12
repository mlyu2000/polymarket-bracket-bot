import json, shutil, os

rec = {
    "ts_utc": "2026-10-10T0540Z",
    "markets": 500,
    "scan_time_s": 49.3,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 70,
    "best_ask_floor": 1.001,
    "near_1.000_1.005": [
        [1.001, "Exact Score: Manchester United FC 0 - 0 Tottenham Hotspur FC", 0.041, 0.96, 86376.72363],
        [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 2541.02249],
        [1.005, "FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5", 0.01, 0.995, 5094.26738],
        [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.01, 0.995, 6754.95159],
        [1.005, "South Melbourne FC vs. Melbourne Victory FC: O/U 7.5", 0.012, 0.993, 7600.41479]
    ],
    "detector_opps": 0,
    "paper_trades": 0,
    "note": "verbatim asks0 near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. FLOOR HELD 1.001 (Man Utd 0-0 Spurs Yes@0.041 No@0.960, liq 86376.7 from 89150.8 -3.1%, gross edge -0.001 ABOVE parity, NOT actionable, best sum in market). Band n=4->5: South Melbourne RE-ENTERS at 1.005 (demoted last run, liq 5772.8->7600.4 +31.7%). Other members: Clermont 2541.0 flat, Chornomorets 4654.3->5094.3 (+9.5%), Kyoto 6993.5->6755.0 (-3.4%). Feyenoord still OUT (exited last run). Next tier 1.006: Falkirk/Dundee liq 3209.3->3216.3. Priced 66->70. Detector opportunities: 0. True brackets (min-ask sum<1.00): 0 - no positive gross edge anywhere, no actionable arb. Paper trades 0."
}

with open("results/cron_scan_history.jsonl", "a") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

os.makedirs("runs", exist_ok=True)
for src in [
    "_tmp_cron_20261010T0540Z_scan_verbatim.py",
    "_tmp_cron_20261010T0540Z_supp_minask.py",
    "_tmp_cron_20261010T0540Z_supp_data.json",
]:
    shutil.copy(src, "runs/" + src)
with open("runs/20261010T0540Z_scan_out.txt", "w", encoding="utf-8") as f:
    f.write("🔍 Scan: 500 markets in 49.3s\n")
    f.write("✅ BRACKETS (sum < 1.00): 0\n")
    f.write("📊 Near-misses (≤1.005): 0  [verbatim asks0 — known DESC-sort artifact]\n")
    f.write("\n[supp min-ask pass — authoritative]\n")
    f.write("priced markets: 70\n")
    f.write("TRUE brackets (min-ask sum < 1.0): 0\n")
    f.write("top 5 best sums (min-ask):\n")
    f.write("  1.0010 | Yes@0.041 No@0.960 | liq=86376.72363 | Exact Score: Manchester United FC 0 - 0 Tottenham Hotspur FC\n")
    f.write("  1.0050 | Yes@0.009 No@0.996 | liq=2541.02249 | Clermont Foot 63 vs. Red Star FC: O/U 7.5\n")
    f.write("  1.0050 | Yes@0.010 No@0.995 | liq=5094.26738 | FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5\n")
    f.write("  1.0050 | Yes@0.010 No@0.995 | liq=6754.95159 | Kyōto Sanga FC vs. FC Machida Zelvia: O/U 7.5\n")
    f.write("  1.0050 | Yes@0.012 No@0.993 | liq=7600.41479 | South Melbourne FC vs. Melbourne Victory FC: O/U 7.5\n")
print("persisted:", rec["ts_utc"])

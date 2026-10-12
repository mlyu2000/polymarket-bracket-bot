import json

TS = "2026-10-09T23:51Z"
lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])

band_cur = [
    [1.005, "Clermont Foot 63 vs. Red Star FC: O/U 7.5", 0.009, 0.996, 1985.75776],
    [1.005, "FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5", 0.010, 0.995, 1820.82047],
    [1.005, "Ky\u014dto Sanga FC vs. FC Machida Zelvia: O/U 7.5", 0.010, 0.995, 3871.28618],
]
prev_band = prev['near_1.000_1.005']
cur_set = {(round(t, 3), q) for t, q, _, _, _ in band_cur}
prev_set = {(round(x[0], 3), x[1]) for x in prev_band}
adds = sorted(cur_set - prev_set)
drops = sorted(prev_set - cur_set)
cur_map = {(round(t, 3), q): (yp, np) for t, q, yp, np, _ in band_cur}
prev_map = {(round(x[0], 3), x[1]): (x[2], x[3]) for x in prev_band}
shifts = [(k[1], prev_map[k], cur_map[k]) for k in (cur_set & prev_set) if prev_map[k] != cur_map[k]]

floor = 1.005
prev_floor = prev['best_ask_floor']
trend = "held" if floor == prev_floor else ("fell" if floor < prev_floor else "rose")

rec = {
    "ts_utc": TS,
    "markets": 500,
    "scan_time_s": 43.9,
    "brackets_verbatim": 0,
    "near_misses_verbatim_asks0": 0,
    "priced_minask": 66,
    "best_ask_floor": floor,
    "near_1.000_1.005": band_cur,
    "detector_opps": 0,
    "paper_trades": 0,
    "note": (
        f"verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        f"FLOOR {prev_floor}->{floor} {trend}. Band {len(prev_band)}->{len(band_cur)}: adds {adds}, drops {drops}. "
        f"Intra-band price shifts: {shifts if shifts else 'none'}. "
        "Next tier 1.006 (Falkirk FC vs. Dundee FC: O/U 7.5). "
        f"Priced {prev['priced_minask']}->66. Liquidity drift only in band: Clermont liq 1856.3->1985.8, "
        "Chornomorets 1820.8->1820.8 (flat), Kyoto 3732.5->3871.3. Detector opportunities: 0. "
        "True brackets (min-ask sum<1.00): 0 - no actionable arb. Paper trades 0."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("appended record", len(lines) + 1, "->", TS)
print("prev floor:", prev_floor, "| now:", floor, "| trend:", trend)
print("adds:", adds, "drops:", drops, "shifts:", shifts)

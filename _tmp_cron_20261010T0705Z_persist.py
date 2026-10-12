import json
prev = {}
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T0705Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
entry = {
    'ts_utc': '2026-10-10T07:05Z',
    'markets': supp['markets'],
    'scan_time_s': 49.9,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
        f"min-ask floor authoritative. FLOOR ROSE AGAIN 1.003->1.005 "
        f"({supp['band'][0][1]} Yes@{supp['band'][0][2]} No@{supp['band'][0][3]} "
        f"liq {supp['band'][0][4]}) — second consecutive floor increase "
        "(1.001->1.003->1.005); best gross edge now -0.005 vs parity. "
        "Band n=2->1: South Melbourne (prev sole 1.003 holder, liq 7439.1) EXITED band — "
        "now 1.006 (Yes 0.012->0.015, No 0.991, liq 7439.1->7759.6 +4.3%); "
        "Kyoto sole holder, liq 7101.8->8945.3 (+25.9%), Yes@0.010 No@0.995 held. "
        f"adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
        "Next tier all 1.006: Clermont (liq 2541.0->2503.7), Chornomorets (5094.3->3069.7 -40%), "
        "Falkirk (3216.3->3534.0). priced 57->57. Detector opportunities: 0. Paper trades: 0. "
        "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
        "floor climbing run-over-run — arbitrage band tightening toward/above parity."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:300], '...')

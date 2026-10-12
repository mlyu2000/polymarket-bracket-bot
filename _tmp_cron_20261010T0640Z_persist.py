import json
prev = {}
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T0640Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
entry = {
    'ts_utc': '2026-10-10T06:40Z',
    'markets': supp['markets'],
    'scan_time_s': 48.8,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
        f"min-ask floor authoritative. FLOOR RISEN 1.001->1.003 "
        f"({supp['band'][0][1]} Yes@{supp['band'][0][2]} No@{supp['band'][0][3]} "
        f"liq {supp['band'][0][4]}) — first floor increase since floor was established; "
        "long-standing holder Exact Score Man Utd 0-0 Spurs (1.001, liq 135081.9 last run) "
        f"EXITED band: prev band {[r[1][:30] for r in prev_band]} vs cur {[r[1][:30] for r in cur_band]}. "
        f"Band n=3->2: adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
        "Movers: South Melbourne 1.004->1.003 (Yes 0.012, No 0.992->0.991, liq 7080.2->7439.1 +5.1%) "
        "now sole floor holder; Kyoto 1.005 held (Yes@0.010 No@0.995, liq 7101.8 flat). "
        f"priced 56->{supp['priced']}. Detector opportunities: 0. Paper trades: 0. "
        "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
        "gap to parity widened (best gross edge now -0.003 vs -0.001)."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:300], '...')

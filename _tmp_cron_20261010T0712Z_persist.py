import json
prev = {}
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T0712Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
entry = {
    'ts_utc': '2026-10-10T07:12Z',
    'markets': supp['markets'],
    'scan_time_s': 50.5,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
        "min-ask floor authoritative. FLOOR HELD 1.005 — third consecutive run at 1.005 "
        f"({cur_band[0][1]} Yes@{cur_band[0][2]} No@{cur_band[0][3]} liq {cur_band[0][4]}; "
        "prev run 8945.3 -> 8952.1 +0.1%); climb 1.001->1.003->1.005 has plateaued. "
        "Band n=1->1, members unchanged (Kyoto sole holder). "
        f"adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
        "Next tier all 1.006: Clermont (liq 2503.7->2560.5 +2.3%), Chornomorets (3069.7->3069.7 flat), "
        "Falkirk (3534.0->3539.2 +0.1%), South Melbourne re-appears at 1.006 (7759.6->15397.8 +98.4%), "
        "Kolos Kovalivka/Epitsentr O/U 6.5 ENTERS next tier at 1.006 (liq 2540.4). "
        f"priced 57->59. Detector opportunities: 0. Paper trades: 0. "
        "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
        "floor stable at 1.005, best gross edge -0.005 vs parity."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:300], '...')

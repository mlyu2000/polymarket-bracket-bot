import json
prev = {}
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T0730Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
entry = {
    'ts_utc': '2026-10-10T07:30Z',
    'markets': supp['markets'],
    'scan_time_s': 47.6,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': (
        "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
        "min-ask floor authoritative. FLOOR HELD 1.005 — fourth consecutive run at 1.005 "
        f"({cur_band[0][1]} Yes@{cur_band[0][2]} No@{cur_band[0][3]} liq {cur_band[0][4]}; "
        "prev run 8952.1 -> 7105.6 -20.6%, back to the ~7100 level seen two runs ago). "
        "Band n=1->1, members unchanged (Kyoto sole holder). "
        f"adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
        "Next tier (1.005,1.01]: Clermont (liq 2560.5->2505.9 -2.1%), Chornomorets (3069.7->3152.4 +2.7%), "
        "Kolos/Epitsentr O/U 6.5 (2540.4->2651.8 +4.4%), Falkirk (3539.2->3526.4 -0.4%), "
        "Al Ettifaq/Al Khaleej O/U 7.5 ENTERS at 1.008 (liq 3823.9); South Melbourne DROPPED OUT of next tier "
        "(was 1.006, now >1.01 or re-priced). "
        "priced 59->62. Detector opportunities: 0. Paper trades: 0. "
        "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
        "floor stable at 1.005, best gross edge -0.005 vs parity."
    ),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:300], '...')

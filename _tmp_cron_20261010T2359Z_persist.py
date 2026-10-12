import json
supp = json.load(open('_tmp_cron_20261010T2359Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T23:59Z',
    'markets': supp['markets'],
    'scan_time_s': 47.4,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             f"min-ask floor authoritative. FLOOR held at {supp['floor']} "
             f"(sole holder: {supp['band'][0][1] if supp['band'] else 'n/a'}). "
             "Band 5->3: adds [], drops [Clermont Foot 63 vs. Red Star FC: O/U 7.5, "
             "FK Chornomorets Odesa vs. FK Kharkiv: O/U 7.5]."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

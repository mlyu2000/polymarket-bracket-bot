import json
supp = json.load(open('_tmp_cron_20261010T1250Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T12:50Z',
    'markets': supp['markets'],
    'scan_time_s': 49.3,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. FLOOR HELD 1.005 third consecutive run "
             "(12:07 regression, 12:24 hold, 12:36 hold). Band n=1 unchanged: sole holder "
             "Falkirk FC vs. Dundee FC: O/U 7.5 1.005 Yes@0.012 No@0.993 flat, "
             "liq 3867.3->3867.5 (+0.005%). priced 62->69 (+7). "
             "next tier: Al Ettifaq 1.008 liq 2860.7 (was 1.008 liq 2868.7), "
             "Genoa O/U 4.5 1.008 liq 341.2 (was 1.008 liq 377.4, liq -9.6%), "
             "NE Revolution exact-score 1.009 liq 3481.7 (was 1.009 liq 2644.6, liq +31.7%), "
             "AEK Athens 1.010 liq 30618.6, Atalanta/Venezia 1.010 liq 47345.5, "
             "Crawley/Chesterfield 1.010 liq 7082.0. detector-opps 0, paper 0 executions; "
             "no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
             "floor 1.005, best gross edge -0.005, still 0.025 above 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

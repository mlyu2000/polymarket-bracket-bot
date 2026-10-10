import json
supp = json.load(open('_tmp_cron_20261011T_now_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T2205Z',
    'markets': supp['markets'],
    'scan_time_s': 74.7,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.0050 (3-way tie): Calcio Padova vs. Carrarese O/U 7.5 Yes@0.010 No@0.995 liq 3028.79 "
             "(was 3040.36), Gaziantep FK vs. Çorum FK O/U 7.5 liq 4106.15 (was 4103.44), JEF United Ichihara Chiba "
             "vs. V-Varen Nagasaki O/U 7.5 liq 4270.01 (was 4296.63). Band membership n=3 unchanged vs 21:32Z, only "
             "liquidity churn. Next tier 1.006 (Al Fayha, LNZ Cherkasy, Silkeborg), 1.007 (Dynamo Kyiv/Karpaty). "
             "priced 65->68 (+3, normal variance 45-69); scan 74.7s. detector-opps 0, paper 0 executions; no sum "
             "< 1.00 anywhere = zero positive gross edge; floor 1.005, best gross edge -0.005, still 0.025 above "
             "the 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended:', json.dumps(entry, ensure_ascii=False)[:140], '...')

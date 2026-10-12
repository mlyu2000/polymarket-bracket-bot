import json
supp = json.load(open('_tmp_cron_20261010T1400Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T14:00Z',
    'markets': supp['markets'],
    'scan_time_s': 50.5,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. FLOOR REGRESSED 1.002->1.007; band <=1.005 now "
             "EMPTY (was n=3 at 13:30: TSG Hoffenheim 1.002 liq 3286.6, Genoa 1.004 liq "
             "1008.9, Falkirk 1.005 liq 2629.2 — all three climbed out of the band this "
             "run; tightest ask sums above 1.005). priced 64->56 (-8). next tier: AEK "
             "Athens 1.010 liq 15066.5, Atalanta/Venezia 1.010 liq 46170.0, Troyes/OM "
             "1.010 liq 57426.5, Bohemians exact-score 1.010 liq 12814.1, Ironi Tiberias "
             "1.010 liq 4664.8. detector-opps 0, paper 0 executions; no sum < 1.00 "
             "anywhere = zero positive gross edge, no actionable arb; floor 1.007, best "
             "gross edge -0.007, still 0.027 above 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

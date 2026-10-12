import json
supp = json.load(open('_tmp_cron_20261010T1135Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T11:35Z',
    'markets': supp['markets'],
    'scan_time_s': 49.6,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. FLOOR HELD 1.003 second consecutive run; "
             "band n=2->1: Clermont Foot 63 vs Red Star O/U 7.5 improved 1.004->1.003 "
             "(Yes 0.007->0.006, No 0.997 flat, liq 3149.2->3315.3 +5.3%) now sole holder; "
             "SV Darmstadt 1.003 previous co-holder dropped out of band AND top next-tier "
             "(worsened/unpriced). priced 76->72 (-4). "
             "next tier: Falkirk 1.006 liq 3712.4 flat; Hajduk/Dinamo returned 1.007 liq 3208.5 "
             "(liq +6.0% vs 3027.0); Al Ettifaq 1.008 liq 2892.4; NE Revolution exact-score 1.009 "
             "liq 3474.0 newly in slice; AEK Athens 1.010 liq 10455.6; Atalanta/Venezia 1.010 "
             "liq 47227.6. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = "
             "zero positive gross edge, no actionable arb; floor 1.003, best gross edge -0.003, "
             "still 0.023 above 0.98 actionable threshold"),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

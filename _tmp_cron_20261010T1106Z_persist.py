import json
supp = json.load(open('_tmp_cron_20261010T1106Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T11:06Z',
    'markets': supp['markets'],
    'scan_time_s': 46.7,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. FLOOR HELD 1.005 fourth consecutive run; "
             "band n=1->1 sole holder Clermont Yes@0.008 No@0.997 prices unchanged "
             "liq 2930.47->2930.47 (flat). priced 73->73 flat. "
             "next tier: 1.006 liq 3717.7 Falkirk FC vs. Dun (flat); "
             "1.006 liq 23.01 SV Darmstadt 98 vs. FC Energie (NEW in tier, ultra-low-liq, "
             "detector-filtered); 1.008 liq 2944.0 Al Ettifaq (-0.17%); "
             "1.010 liq 11295.1 AEK Athens (-2.5%); 1.010 liq 46007.2 Atalanta/Venezia; "
             "1.010 liq 27561.7 Cercle Brugge/Anderlecht (newly visible in top slice); "
             "Hajduk 1.007 dropped out of top slice. "
             "detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = "
             "zero positive gross edge, no actionable arb; floor 1.005, "
             "best gross edge -0.005, still 0.025 above 0.98 actionable threshold"),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

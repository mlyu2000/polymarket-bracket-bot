import json

entry = {
    'ts_utc': '2026-10-10T17:06Z',
    'markets': 500,
    'scan_time_s': 54.3,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 49,
    'best_ask_floor': 1.005,
    'near_1.000_1.005': [
        [1.005, 'JEF United Ichihara Chiba vs. V-Varen Nagasaki: O/U 7.5', 0.01, 0.995, 3154.83604],
        [1.005, 'Konyaspor vs. Rams Ba\u015fek\u015fehir FK: O/U 7.5', 0.012, 0.993, 2878.33913],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.005; band refreshed n=1->2: prior sole member CA River Plate vs. AA Estudiantes O/U 7.5 "
             "climbed 1.005->1.006 (0.011/0.995), replaced by two new members from the 1.006 tier: JEF United "
             "Ichihara Chiba vs. V-Varen Nagasaki O/U 7.5 1.005 Yes@0.010 No@0.995 liq 3154.8 and Konyaspor vs. Rams "
             "Basaksehir FK O/U 7.5 1.005 Yes@0.012 No@0.993 liq 2878.3. priced 45->49 (+4). Next tier 1.006 (CA River "
             "Plate), 1.007 (CA Tigre vs. CA Banfield, VfL Bochum vs. DSC Arminia Bielefeld), then 1.010 tier "
             "(Atalanta/Venezia, Club Almagro/Chacarita, Fram Reykjavik spread -1.5). detector-opps 0, paper 0 "
             "executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; floor 1.005, best "
             "gross edge -0.005, still 0.025 above 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

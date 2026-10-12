import json

entry = {
    'ts_utc': '2026-10-11T1215Z',
    'markets': 500,
    'scan_time_s': 70.1,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 58,
    'best_ask_floor': 1.005,
    'near_1.000_1.005': [
        [1.005, 'JEF United Ichihara Chiba vs. V-Varen Nagasaki: O/U 7.5', 0.01, 0.995, 3699.76044],
        [1.005, 'Konyaspor vs. Rams Başakşehir FK: O/U 7.5', 0.012, 0.993, 2887.05926],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR STABLE 1.005 (3rd consecutive observation); band n=2 unchanged from 17:06Z run but membership "
             "rotated slightly on liq: JEF United Ichihara Chiba vs. V-Varen Nagasaki O/U 7.5 1.005 Yes@0.010 "
             "No@0.995 liq 3699.8 (was 3154.8) and Konyaspor vs. Rams Başakşehir FK O/U 7.5 1.005 Yes@0.012 "
             "No@0.993 liq 2887.1 (was 2878.3); next tier 1.006 (CA River Plate, FK LNZ Cherkasy, Silkeborg), then "
             "1.007 (CA Tigre, Dynamo Kyiv, Bochum). priced 49->58 (+9, normal inter-call variance 45-69); scan "
             "70.1s (slowest of recent runs - API latency variance). detector-opps 0, paper 0 executions; no sum "
             "< 1.00 anywhere = zero positive gross edge, no actionable arb; floor 1.005, best gross edge -0.005, "
             "still 0.025 above the 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

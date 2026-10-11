import json

entry = {
    'ts_utc': '2026-10-11T1215Z',
    'markets': 500,
    'scan_time_s': 53.8,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 94,
    'yes_only': 395,
    'no_only': 0,
    'both_empty': 11,
    'median_minask_sum': 1.038,
    'best_ask_floor': 1.001,
    'near_1.000_1.005': [
        [1.001, 'Will the highest temperature in Paris be 16C on October 12?', 0.004, 0.997, 2976.32],
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 3085.90],
        [1.004, 'Gaziantep FK vs. Corum FK: O/U 7.5', 0.01, 0.994, 6052.32],
        [1.004, 'Konyaspor vs. Rams Basaksehir FK: O/U 7.5', 0.011, 0.993, 6103.36],
        [1.004, 'Spread: Cagliari Calcio (-2.5)', 0.01, 0.994, 17290.44],
        [1.005, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.996, 3865.98],
        [1.005, 'Calcio Padova vs. Carrarese Calcio: O/U 7.5', 0.01, 0.995, 5155.40],
        [1.005, 'FK LNZ Cherkasy vs. FK Kudrivka: O/U 7.5', 0.01, 0.995, 4305.25],
        [1.005, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.009, 0.996, 3636.26],
        [1.005, 'Silkeborg IF vs. AC Horsens: O/U 7.5', 0.011, 0.994, 5314.56],
        [1.005, 'Spread: ES Troyes AC (-3.5)', 0.015, 0.99, 6081.42],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "vs 12:10Z: floor HELD 1.0010 (Paris highest temp 16C Yes@0.004 No@0.997 liq 4450.07->2976.32 drift only); "
             "Cagliari -2.5 spread WIDENED 1.0030->1.0040 liq 13395.69->17290.44; Konyaspor O/U 7.5 IMPROVED 1.0050->1.0040 "
             "liq 5553.96->6103.36; CA Talleres and Gaziantep hold 1.0040; band<=1.005 WIDENED n=10->11 "
             "(FK LNZ Cherkasy O/U 7.5 + ES Troyes -3.5 NEW at 1.0050, Konyaspor moved 1.0050->1.0040, Flamengo dropped "
             "to 1.0060); two-sided 88->94 WIDENED, yes-only 401->395, no-only 1->0, both-empty 10->11 = 81.2% not "
             "bracket-able (structural); median TIGHTENED 1.0390->1.0380; verbatim cron scan 54.5s->53.8s: 0 BRACKETS, "
             "0 asks0 near-misses (known DESC artifact); supp min-ask: 94/500 priced, floor 1.0010, actionable(<0.98) 0, "
             "best gross edge -0.001, 0.021 above 0.98 actionable threshold; detector-opps 0, paper 0 executions; no action"),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
with open('results/scan_latest.json', 'w') as f:
    json.dump(entry, f, indent=1)
print('appended:', json.dumps(entry)[:140], '...')

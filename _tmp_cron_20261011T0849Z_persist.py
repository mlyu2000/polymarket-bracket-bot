import json

entry = {
    'ts_utc': '2026-10-11T08:49Z',
    'markets': 500,
    'scan_time_s': 54.1,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 101,
    'yes_only': 388,
    'no_only': 0,
    'both_empty': 11,
    'best_ask_floor': 1.001,
    'near_1.000_1.005': [
        [1.001, 'Will the highest temperature in Paris be 16\u00b0C on October 12?', 0.003, 0.998, 3051.4734],
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 2017.82302],
        [1.004, 'Spread: Cagliari Calcio (-2.5)', 0.008, 0.996, 17017.61994],
        [1.005, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.996, 3876.51159],
        [1.005, 'Calcio Padova vs. Carrarese Calcio: O/U 7.5', 0.01, 0.995, 5184.12758],
        [1.005, 'Gaziantep FK vs. \u00c7orum FK: O/U 7.5', 0.011, 0.994, 5384.00989],
        [1.005, 'Konyaspor vs. Rams Ba\u015fak\u015fehir FK: O/U 7.5', 0.011, 0.994, 5209.66391],
        [1.005, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.009, 0.996, 3630.95926],
        [1.005, 'Silkeborg IF vs. AC Horsens: O/U 7.5', 0.011, 0.994, 5329.13565],
        [1.005, 'Spread: ES Troyes AC (-3.5)', 0.015, 0.99, 6041.73367],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.0010 (Paris highest temp 16C Yes@0.004->0.003 No@0.997->0.998 liq 3011.54->3051.47 drift only); "
             "Cagliari -2.5 spread slipped 1.0030->1.0040 liq 17473.81->17017.62; CA Talleres O/U 8.5 HELD 1.0040 liq 3091.67->2017.82; "
             "Lillestrom SK 4-0 Molde FK exact score DROPPED OUT (was 1.0030); FK LNZ Cherkasy O/U 7.5 slipped 1.0050->1.0060; "
             "ES Troyes -3.5 holds 1.0050; Konyaspor/Gaziantep/Al Fayha/Padova/Modena/Silkeborg all hold 1.0050; "
             "band<=1.005 SHRANK n=12->10. two-sided 102->101 (oscillation), yes-only 388, no-only 0, both-empty 11 "
             "= 79.8% not bracket-able (structural, held). verbatim scan 76.2s->54.1s: 0 BRACKETS, 0 asks0 near-misses (artifact); "
             "supp min-ask: 101/500 priced, floor 1.0010, actionable(<0.98) 0, best gross edge -0.001, 0.021 above the 0.98 "
             "actionable threshold; detector-opps 0, paper 0 executions; no action."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
with open('results/scan_latest.json', 'w') as f:
    json.dump(entry, f, indent=1)
print('appended:', json.dumps(entry)[:140], '...')

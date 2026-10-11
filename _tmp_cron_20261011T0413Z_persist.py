import json

entry = {
    'ts_utc': '2026-10-11T0413Z',
    'markets': 500,
    'scan_time_s': 59.7,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 97,
    'best_ask_floor': 1.004,
    'near_1.000_1.005': [
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 1837.11714],
        [1.004, 'Spread: Cagliari Calcio (-2.5)', 0.01, 0.994, 12179.34652],
        [1.005, 'CA Platense vs. AA Argentinos Juniors: O/U 6.5', 0.009, 0.996, 3558.20191],
        [1.005, 'CR Flamengo vs. Fluminense FC: O/U 7.5', 0.012, 0.993, 4958.63068],
        [1.005, 'Calcio Padova vs. Carrarese Calcio: O/U 7.5', 0.01, 0.995, 4276.0006],
        [1.005, 'Gaziantep FK vs. Çorum FK: O/U 7.5', 0.01, 0.995, 5329.07991],
        [1.005, 'Grêmio FBPA vs. SC Internacional: O/U 7.5', 0.009, 0.996, 4158.21623],
        [1.005, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.009, 0.996, 3249.0765],
        [1.005, 'Silkeborg IF vs. AC Horsens: O/U 7.5', 0.011, 0.994, 5341.78155],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.004->1.004 (unchanged vs 0356Z); band WIDENED n=4->9 (CA Talleres O/U 8.5 joins at "
             "1.0040 Yes@0.005 No@0.999 liq 1837.1; Platense, Flamengo, Padova, Gaziantep, Grêmio, Modena, "
             "Silkeborg join at 1.0050). priced 93->97. 383 one-sided / 20 no-asks = 80.6% of book not "
             "bracket-able via resting asks (structural, unchanged). detector-opps 0, paper 0 executions; no sum "
             "< 1.00 anywhere = zero positive gross edge; best gross edge -0.004, still 0.024 above the 0.98 "
             "actionable threshold. No action required."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
with open('results/scan_latest.json', 'w') as f:
    json.dump(entry, f, indent=1)
print('appended:', json.dumps(entry)[:140], '...')

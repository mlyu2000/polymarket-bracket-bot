import json

entry = {
    'ts_utc': '2026-10-11T1700Z',
    'markets': 500,
    'scan_time_s': 54.6,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 79,
    'best_ask_floor': 1.0030,
    'near_1.000_1.005': [
        [1.0030, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.008, 0.995, 8367.25136],
        [1.0030, 'Will the price of Ethereum be between $3,000 and $3,100...', 0.004, 0.999, 4337.65097],
        [1.0040, 'CR Flamengo vs. Fluminense FC: O/U 7.5', 0.010, 0.994, 21148.42596],
        [1.0040, 'Exact Score: Lillestrom SK 4 - 0 Molde FK?', 0.016, 0.988, 1836.86724],
        [1.0040, 'Lillestrom SK vs. Molde FK: Lillestrom SK O/U 5.5', 0.013, 0.991, 1953.51771],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "Floor unchanged at 1.0030 (Modena FC 2018 vs. Hellas Verona FC O/U 7.5 and Ethereum $3,000-$3,100 both "
             "1.0030); band n=3 with rotation: CR Flamengo vs. Fluminense FC O/U 7.5 and two Lillestrom/Molde markets "
             "at 1.0040. Next tier 1.008. priced 74->79 two-sided (+5, normal variance); yes_only 5, no_only 380, "
             "empty 36. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge; "
             "floor 1.0030, best gross edge -0.0030, still 0.023 above the 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

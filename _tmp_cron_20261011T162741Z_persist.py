import json

entry = {
    'ts_utc': '2026-10-11T1625Z',
    'markets': 500,
    'scan_time_s': 57.6,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 74,
    'best_ask_floor': 1.0030,
    'near_1.000_1.005': [
        [1.0030, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.008, 0.995, 8377.42723],
        [1.0030, 'Will the price of Ethereum be between $3,000 and $3,100 on October...', 0.004, 0.999, 4539.71988],
        [1.0040, 'CR Flamengo vs. Fluminense FC: O/U 7.5', 0.010, 0.994, 8030.26323],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR DROPPED 1.005 -> 1.0030 (new low, was stable at 1.005 for several runs); band n=3 with membership "
             "rotation: Modena FC 2018 vs. Hellas Verona FC O/U 7.5 1.0030 Yes@0.008 No@0.995 liq 8377.4; Ethereum "
             "$3,000-$3,100 1.0030 Yes@0.004 No@0.999 liq 4539.7; CR Flamengo vs. Fluminense FC O/U 7.5 1.0040 "
             "Yes@0.010 No@0.994 liq 8030.3. Next tier 1.008 (Spread: Venezia FC -3.5, Lille OSC -1.5, LA Galaxy -3.5). "
             "priced 58->74 (+16, normal inter-call variance 45-69); scan 57.6s. detector-opps 0, paper 0 executions; "
             "no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; floor 1.0030, best gross edge "
             "-0.0030, still 0.023 above the 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

import json

entry = {
    'ts_utc': '2026-10-12T1349Z',
    'markets': 500,
    'scan_time_s': 56.4,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 73,
    'best_ask_floor': 1.0030,
    'near_1.000_1.005': [
        [1.0030, 'Spread: Venezia FC (-3.5)', 0.004, 0.999, 41412.38],
    ],
    'tiers': {'le1.000': 0, 'le1.005': 1, 'le1.010': 12, 'le1.020': 24, 'le1.030': 30, 'le1.040': 32},
    'detector_opps': 0,
    'paper_trades': 0,
    'structural': {'two_sided': 73, 'yes_only': 417, 'no_only': 0, 'empty': 10},
    'floor_median': 1.0410,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "Floor HELD at 1.0030 (Venezia FC -3.5 SOLO, Y@0.004 N@0.999) from 1335Z->1349Z, now with deep liq "
             "41.4k (was 4.1k at 1319Z when it sat at 1.0080). NH-02 Dem seat no longer in band. Band <=1.005 n=1 "
             "SOLO; <=1.010 n=12 (Dplus KIA + NH-02 Dem seat both 1.0080, Eyupspor 1.0090, Amsterdam temp 1.0090). "
             "Structural: two_sided 73, yes_only 417, no_only 0, empty 10 = 427/500 85.4% NOT bracket-able. "
             "detector-opps 0, paper 0 executions; zero sum < 1.00 anywhere; floor 1.0030 = 0.023 above 0.98 "
             "actionable threshold - NOT actionable."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

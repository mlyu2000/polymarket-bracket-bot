import json

entry = {
    'ts_utc': '2026-10-12T1405Z',
    'markets': 500,
    'scan_time_s': 59.4,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 75,
    'structural': {'two_sided': 75, 'yes_only': 417, 'no_only': 0, 'both_empty': 8},
    'best_ask_floor': 1.008,
    'near_1.000_1.005': [],
    'tiers': {'le_1010': 12, 'le_1020': 20, 'le_1030': 29},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("FLOOR LOOSENED 1.0030->1.0080 (three-way tie): Galatasaray SK (-2.5) Y@0.017 N@0.991 liq 15.9k "
             "[NEW to floor], Venezia FC (-3.5) Y@0.009 N@0.999 liq 2.2k (loosened from 1.0030 Y@0.004, liq "
             "collapsed 41.4k->2.2k), NH-02 Dem House seat Y@0.954 N@0.054 liq 50.8k (HELD at 1.008). Sub-1.005 "
             "band EMPTIED (le1005 1->0). Next tier 1.0090 Amsterdam temp 13C Oct 14 Y@0.010 N@0.999 liq 2.4k. "
             "Tiers le1010 n=12 (hold), le1020 n=20 (was 24), le1030 n=29 (was 30). Structural two_sided 73->75, "
             "yes_only 417, no_only 0, empty 10->8 = 425/500 85.0% NOT bracket-able (structural; YES-ask-only "
             "books cannot be bracketed, NO is a separate token book). Floor 1.008 is 0.028 above 0.98 actionable "
             "threshold - NOT actionable. verbatim scan 59.4s: 0 BRACKETS, 0 asks0 near-misses (artifact). "
             "supp min-ask: 75/500 priced, floor 1.0080, actionable(<=0.98) 0, best gross edge -0.0080, 0.028 "
             "above threshold. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross "
             "edge, no actionable arb. 500 markets, no API errors."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended 1405Z')

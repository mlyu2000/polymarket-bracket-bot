import json

entry = {
    'ts_utc': '2026-10-12T1654Z',
    'markets': 500,
    'scan_time_s': 52.9,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 74,
    'structural': {'two_sided': 74, 'yes_only': 417, 'no_only': 1, 'both_empty': 8},
    'best_ask_floor': 1.004,
    'near_1.000_1.005': [
        [1.004, 'Will Flávio Bolsonaro win the second round of the 2026 Brazilian presidential election by 8–12%?', 0.16, 0.844, 106662.2],
        [1.005, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.99, 27349.39],
    ],
    'tiers': {'le_1000': 0, 'le_1005': 2, 'le_1010': 16, 'le_1020': 25, 'le_1030': 32},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("FLOOR LOOSENED 1.0020 -> 1.0040. NEW floor: Flavio Bolsonaro 2026 BR 2nd-round win-margin 8-12% "
             "Y@0.160 N@0.844 liq 106,662.20 (first appearance in band; huge book). Venezia FC O/U 4.5 1.0020 "
             "(liq 62.28) DROPPED OUT of band. Galatasaray SK (-2.5) HELD 1.0050 liq 27.3k (prices unchanged). "
             "Band <=1.005 now n=2 (first multi-entry band since 1405Z three-way). Eyupspor (-3.5) deepened "
             "15.8k->36.0k at 1.0090; Slovan 1.0060 liq 12.3k->14.0k; NH-02 1.0060 liq 50.9k. "
             "Structural: 74 two-sided (75->74), 417 yes_only, 1 no_only, 8 both_empty = 85.2% not bracket-able "
             "(structural; YES-ask-only books cannot be bracketed, NO is a separate token book). "
             "Verbatim scan 52.9s: 0 BRACKETS, 0 asks[0] near-misses (DESC-sort artifact). supp min-ask: "
             "74/500 priced, floor 1.0040, actionable(<=0.98) 0, best gross edge -0.0040, still 0.024 above the "
             "0.98 actionable threshold. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero "
             "positive gross edge, no actionable arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended 1654Z')

import json

entry = {
    'ts_utc': '2026-10-12T1005Z',
    'markets': 500,
    'scan_time_s': 55.1,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 61,
    'structural': {'two_sided': 61, 'yes_only': 429, 'no_only': 0, 'both_empty': 10},
    'best_ask_floor': 1.004,
    'near_1.000_1.005': [
        [1.004, 'Spread: Viking FK (-1.5)', 0.014, 0.990, 28652.5],
    ],
    'tiers': {'le_1010': 14, 'le_1020': 24, 'le_1030': 31},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.0040: Spread: Viking FK (-1.5) Y@0.014 N@0.990 liq 28642.94->28652.5 (prices unchanged, "
             "slight refill) - SOLO in band n=1, held since 0851Z (~1h14m). Next tier 1.0070 Venezia FC (-3.5) "
             "Y@0.009 N@0.998 liq 6618.73; 1.0080 NH-02 House seat Y@0.954 N@0.054 liq 50782.65. Tiers le_1010 n=14, "
             "le_1020 n=24, le_1030 n=31. Structural: two_sided 62->61, yes_only 429, both_empty 10 = 87.8% not "
             "bracket-able (structural; YES-ask-only books cannot be bracketed, NO is a separate token book). "
             "verbatim scan 55.1s: 0 BRACKETS, 0 asks0 near-misses (artifact). supp min-ask: 61/500 priced, "
             "floor 1.0040, actionable(<=0.98) 0, best gross edge -0.0040, still 0.024 above the 0.98 actionable "
             "threshold. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, "
             "no actionable arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended 1005Z')

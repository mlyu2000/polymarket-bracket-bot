import json

entry = {
    'ts_utc': '2026-10-11T133713Z',
    'markets': 500,
    'scan_time_s': 54.8,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 93,
    'structural': {'two_sided': 93, 'yes_only': 349, 'no_only': 3, 'both_empty': 55},
    'best_ask_floor': 1.003,
    'near_1.000_1.005': [
        [1.003, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.007, 0.996, 23335.01],
        [1.004, 'CR Flamengo vs. Fluminense FC: O/U 7.5', 0.010, 0.994, 8775.86],
        [1.005, 'FC Midtjylland vs. FC K\u00f8benhavn: O/U 8.5', 0.006, 0.999, 6929.44],
        [1.005, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.010, 0.995, 5385.39],
        [1.005, 'NK Slaven Belupo vs. HNK Rijeka: O/U 7.5', 0.011, 0.994, 4229.79],
        [1.005, 'Spread: ES Troyes AC (-3.5)', 0.015, 0.990, 6102.73],
    ],
    'median_floor': 1.039,
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact: asks DESC-sorted, asks[0]=worst ~0.999; "
             "detector correctly uses min()). FLOOR IMPROVED 1.0040->1.0030: Al Fayha O/U 7.5 now sole floor at "
             "1.0030 Yes@0.009->0.007 No@0.996 (unchanged) liq 12375.00->23335.01 (+88% refill) - it DROPPED from the "
             "1.0050 co-floor to become floor leader. Prior 1.0040 floor members CA Talleres O/U 8.5 and Seattle 66-67F "
             "BOTH DROPPED OUT of band; CR Flamengo O/U 7.5 IMPROVED 1.0060->1.0040 Yes@0.010 No@0.994 (new #2). "
             "BAND n=6->6 with full composition turnover: Al Fayha improved to 1.0030; Midtjylland O/U 8.5, Modena O/U 7.5, "
             "Slaven Belupo O/U 7.5, ES Troyes (-3.5) HELD 1.0050; Gaziantep O/U 7.5, NK Lokomotiva, Silkeborg, Padova "
             "DROPPED OUT. Next tier 1.0060 Cagliari (-2.5) liq 20578; 1.0080 Padova/Carrarese. two_sided NARROWED "
             "105->93 (5th consecutive decline; book-refresh jitter + liquidity drain), yes_only 376->349, no_only 0->3, "
             "both_empty 19->55 = 81.4% not bracket-able (structural, held - YES-ask-only books cannot be bracketed; NO is "
             "a separate token book). median priced floor 1.0390 HELD. verbatim scan 54.8s: 0 BRACKETS, 0 asks0 "
             "near-misses (artifact). supp min-ask: 93/500 priced, floor 1.0030, actionable(<0.98) 0, best gross edge "
             "-0.003, still 0.023 above the 0.98 actionable threshold. detector-opps 0, paper 0 executions; no sum < 1.00 "
             "anywhere = zero positive gross edge, no actionable arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended entry:', entry['ts_utc'])

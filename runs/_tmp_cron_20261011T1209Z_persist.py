import json

entry = {
    'ts_utc': '2026-10-11T1209Z',
    'markets': 500,
    'scan_time_s': 53.9,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 103,
    'structural': {'two_sided': 103, 'yes_only': 370, 'no_only': 0, 'both_empty': 27},
    'best_ask_floor': 1.004,
    'median_floor': 1.039,
    'near_1.000_1.005': [
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 3797.34202],
        [1.005, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.996, 4092.13501],
        [1.005, 'FC Midtjylland vs. FC Kobenhavn: O/U 8.5', 0.006, 0.999, 16215.68803],
        [1.005, 'Gaziantep FK vs. Corum FK: O/U 7.5', 0.012, 0.993, 4783.11295],
        [1.005, 'NK Lokomotiva Zagreb vs. NK Varazdin: O/U 7.5', 0.011, 0.994, 3151.57228],
        [1.005, 'Spread: ES Troyes AC (-3.5)', 0.015, 0.99, 6748.6102],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact: asks DESC-sorted, asks[0]=worst "
             "~0.999; detector correctly uses min()). FLOOR HELD 1.0040 (4th+ consecutive obs): CA Talleres O/U 8.5 "
             "Yes@0.005 No@0.999 liq 3087.43->3797.34 (+23% JUMP); prior co-floor Seattle temp 66-67F DROPPED OUT of "
             "band (absent from active priced books); Silkeborg O/U 7.5 DROPPED; FC Midtjylland vs. FC Kobenhavn O/U "
             "8.5 NEW at 1.0050 Yes@0.006 No@0.999 liq 16215.69; ES Troyes -3.5 spread back in band at 1.0050 (was "
             "1.0140 at 1031Z, improved); Al Fayha O/U 7.5 HELD 1.0050 liq 4062.27->4092.14 flat (had drained); "
             "Gaziantep HELD 1.0050; NK Lokomotiva Zagreb HELD 1.0050. BAND n=7->6. Next tier 1.006 (Flamengo, "
             "Modena, Slaven Belupo O/U 7.5, Cagliari spread -2.5). two_sided 105->103 (narrowed), yes_only "
             "368->370, no_only 0, both_empty 27 HELD = 79.4% not bracket-able (structural, held; YES-ask-only books "
             "cannot be bracketed - NO token is a separate book). median floor 1.0390 HELD. verbatim scan 53.9s: 0 "
             "BRACKETS, 0 asks0 near-misses (artifact). supp min-ask: 103/500 priced, floor 1.0040, actionable(<0.98) "
             "0, best gross edge -0.004, floor 0.024 above the 0.98 actionable threshold (held). detector-opps 0, "
             "paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; no action."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended entry ts:', entry['ts_utc'])

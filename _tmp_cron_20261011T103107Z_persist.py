import json

entry = {
    'ts_utc': '2026-10-11T1031Z',
    'markets': 500,
    'scan_time_s': 55.5,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 106,
    'best_ask_floor': 1.004,
    'near_1.000_1.005': [
        [1.004, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.995, 12315.72019],
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 3093.84874],
        [1.004, 'Will the highest temperature in Seattle be between 66-67\u00b0F on October 12?', 0.007, 0.997, 2003.74606],
        [1.005, 'Calcio Padova vs. Carrarese Calcio: O/U 7.5', 0.010, 0.995, 5881.36179],
        [1.005, 'Gaziantep FK vs. \u00c7orum FK: O/U 7.5', 0.012, 0.993, 6292.09228],
        [1.005, 'Modena FC 2018 vs. Hellas Verona FC: O/U 7.5', 0.009, 0.996, 4278.4119],
        [1.005, 'Silkeborg IF vs. AC Horsens: O/U 7.5', 0.011, 0.994, 6925.05214],
    ],
    'structural': {'two_sided': 106, 'yes_only': 376, 'no_only': 0, 'both_empty': 18},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact: asks DESC-sorted, asks[0]=worst; "
             "detector correctly uses min()). FLOOR WORSENED 1.0010->1.0040: prior floor market (Paris highest temp "
             "16C) resolved/closed (absent from active markets, verified). New floor = Al Fayha O/U 7.5 1.0040 "
             "Yes@0.009 No@0.995 liq 12315.72 (HELD flat vs prior run - inherited floor on Paris exit). BAND n=10->7: "
             "Konyaspor O/U 7.5 DROPPED to Yes-only (No book EMPTIED, now Yes@0.014 liq 16563 - same drain pattern as "
             "FK LNZ Cherkasy); ES Troyes -3.5 WORSENED 1.0050->1.0140 (Yes@0.015 No@0.999). CA Talleres O/U 8.5 HELD "
             "1.0040 (liq 3092.16->3093.85 drift only); Seattle temp 66-67F HELD 1.0040 (was NEW last run); "
             "Padova/Gaziantep/Modena/Silkeborg O/U 7.5 all HELD 1.0050. Next tier 1.006 (Flamengo O/U 7.5, Lokomotiva "
             "Zagreb O/U 7.5, Slaven Belupo O/U 7.5, Cagliari spread -2.5). two_sided 110->106 (NARROWED), yes_only "
             "372->376, no_only 0, both_empty 18 = 78.8% not bracket-able (structural, held; YES-ask-only books cannot "
             "be bracketed - NO token is a separate book). Floor 1.0040 = 0.024 above the 0.98 actionable threshold "
             "(was 0.021 - moving further from actionable). detector-opps 0, paper 0 executions; no sum < 1.00 anywhere "
             "= zero positive gross edge, no actionable arb; no action."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

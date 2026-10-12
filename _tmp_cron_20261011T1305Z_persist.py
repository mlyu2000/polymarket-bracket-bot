import json

entry = {
    'ts_utc': '2026-10-11T1305Z',
    'markets': 500,
    'scan_time_s': 56.2,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 105,
    'structural': {'two_sided': 105, 'yes_only': 376, 'no_only': 0, 'both_empty': 19},
    'best_ask_floor': 1.004,
    'near_1.000_1.005': [
        [1.004, 'CA Talleres vs. CA Independiente: O/U 8.5', 0.005, 0.999, 3087.43162],
        [1.004, 'Will the highest temperature in Seattle be between 66-67\u00b0F o', 0.007, 0.997, 1679.95306],
        [1.005, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.996, 12374.99929],
        [1.005, 'Gaziantep FK vs. \u00c7orum FK: O/U 7.5', 0.012, 0.993, 4777.79329],
        [1.005, 'NK Lokomotiva Zagreb vs. NK Vara\u017edin: O/U 7.5', 0.011, 0.994, 3115.05128],
        [1.005, 'Silkeborg IF vs. AC Horsens: O/U 7.5', 0.011, 0.994, 14774.23959],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact: asks DESC-sorted, asks[0]=worst ~0.999; "
             "detector correctly uses min()). FLOOR HELD 1.0040 (3rd consecutive obs since 1031Z): CA Talleres O/U 8.5 "
             "1.0040 Yes@0.005 No@0.999 liq 3093.85->3087.43 (drift only); Seattle 66-67F HELD 1.0040 liq 2003.75->1679.95 "
             "(liq DROPPED ~16%); Al Fayha O/U 7.5 WORSENED 1.0040->1.0050 (Yes@0.009->same, No@0.995->0.996; liq "
             "12315.72->12375.00 flat) - it is no longer co-floor, floor now CA Talleres+Seattle tie. BAND n=7->6: "
             "Padova, Modena, Konyaspor O/U 7.5 DROPPED OUT (all previously-1.005 members; consistent with slow "
             "churn/liquidity drain), REPLACED by NK Lokomotiva Zagreb O/U 7.5 NEW at 1.0050 Yes@0.011 No@0.994 "
             "liq 3115.05. Gaziantep HELD 1.0050 (Yes@0.012 No@0.993 unchanged, liq 6292->4778 DROP); Silkeborg HELD "
             "1.0050 (liq 6925->14774 JUMP). Next tier 1.006 (Flamengo O/U 7.5, Modena O/U 7.5, Slaven Belupo O/U 7.5, "
             "Cagliari spread -2.5 - Modena/Padova reappear at 1.006). two_sided 106->105 (NARROWED 4th consecutive), "
             "yes_only 376 (held), no_only 0 (held), both_empty 18->19 = 79% not bracket-able (structural, held; "
             "YES-ask-only books cannot be bracketed - NO token is a separate book). verbatim scan 55.5s->56.2s: "
             "0 BRACKETS, 0 asks0 near-misses (artifact). supp min-ask: 105/500 priced, floor 1.0040, actionable(<0.98) 0, "
             "best gross edge -0.004, still 0.024 above the 0.98 actionable threshold. detector-opps 0, paper 0 "
             "executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended entry:', entry['ts_utc'])

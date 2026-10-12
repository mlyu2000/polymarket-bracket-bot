import json

entry = {
    'ts_utc': '2026-10-12T1728Z',
    'markets': 500,
    'scan_time_s': 54.4,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 74,
    'structural': {'two_sided': 74, 'yes_only': 417, 'no_only': 1, 'both_empty': 8},
    'best_ask_floor': 1.001,
    'near_1.000_1.005': [
        [1.001, 'Will Flavio Bolsonaro win the second round of the 2026 Brazilian presidential election by 8-12%?', 0.146, 0.855, 94835.87],
        [1.002, 'KFUM-Kameratene Oslo vs. Valerenga Fotball: Valerenga ... (O/U)', 0.006, 0.996, 973.96],
        [1.005, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.99, 23711.16],
    ],
    'tiers': {'le_1000': 0, 'le_1005': 3, 'le_1010': 14, 'le_1020': 25, 'le_1030': 32},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("NEW ALL-TIME-LOW TIE: floor 1.0010 - Flavio Bolsonaro 2026 BR 2nd-round win-margin 8-12% "
             "Y@0.146 N@0.855 liq 94,835.87 (ties 1.0010 low of 2200Z 10-10 ATL; first band appearance since "
             "1654Z 1.0040; Y tightened 0.160->0.146 while N loosened 0.844->0.855, net -0.0030). "
             "Band <=1.005 now n=3: Bolsonaro 1.0010 (big book) + KFUM-Kameratene vs Valerenga O/U 1.0020 "
             "(Y@0.006 N@0.996, liq only 973.96 - THIN, new) + Galatasaray SK (-2.5) HELD 1.0050 "
             "(Y@0.015 N@0.990, liq 23.7k). NH-02 Dem House seat 1.0060 (liq 50.8k), Slovan Bratislava (-2.5) "
             "1.0070 (liq 20.4k). Tiers: <=1.005 n=3, <=1.010 n=14, <=1.020 n=25, <=1.030 n=32. "
             "Structural: 74 two-sided, 417 yes_only, 1 no_only, 8 both_empty = 85.2% not bracket-able "
             "(YES-ask-only books; NO is a separate token book). "
             "Verbatim scan 54.4s: 0 BRACKETS, 0 asks[0] near-misses (DESC-sort artifact, expected). "
             "supp min-ask: 74/500 priced, floor 1.0010, still 0.021 ABOVE the 0.98 actionable threshold - "
             "NOT actionable. 0 positive gross edge anywhere = no arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended 1728Z')

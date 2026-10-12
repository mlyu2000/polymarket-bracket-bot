import json

entry = {
    'ts_utc': '2026-10-12T1920Z',
    'markets': 500,
    'scan_time_s': 55.2,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 69,
    'structural': {'two_sided': 69, 'yes_only': 419, 'no_only': 1, 'both_empty': 11},
    'best_ask_floor': 1.004,
    'best_gross_edge': -0.004,
    'near_1.000_1.005': [
        [1.004, 'Levante UD vs. Sevilla FC: Sevilla FC O/U 4.5', 0.020, 0.984, 2414.36952],
        [1.005, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.990, 21149.59101],
    ],
    'tiers': {'le_1005': 2, 'le_1010': 14, 'le_1020': 28, 'le_1030': 32, 'le_1050': 46},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR LOOSENED 1.0030->1.0040 since 1906Z/1845Z: BOTH prior 1.0030 floor markets dropped out of the band "
             "(Hormuz agreement/oil-below-$80/Dems-win-Senate combo 1.0030 @1845Z liq 119.7k; GKS Katowice vs. Wieczysta "
             "Krakow O/U 1.5 1.0030 @1906Z liq 18.5k). NEW floor: Levante UD vs. Sevilla FC: Sevilla FC O/U 4.5 1.0040 "
             "(Y@0.020 N@0.984 liq 2414.37) - IMPROVED from 1.0050 at 1906Z (Y@0.012 N@0.993 liq 149.78), +2.3k liq refill. "
             "Galatasaray SK (-2.5) HELD 1.0050 (Y@0.015 N@0.990 liq 21149.59; 19.7k@1845Z -> 19.0k -> 21.1k). "
             "Band <=1.005 n=2 (was 3 at 1845Z). NH-02 Dem House seat 1.0060 HELD (liq 50787.92); Slovan Bratislava (-2.5) "
             "1.0070 (liq 12734.83); Amsterdam 13C Oct 14 1.0090 (liq 2424.16). 1.0100 tier crowded: Millwall/Swansea 1H "
             "O/U 0.5, Burnley (-1.5), Man City (-3.5), Real Madrid (-2.5), Georgia 11.5 wins. "
             "Tiers: <=1.005 n=2, <=1.010 n=14, <=1.020 n=28, <=1.030 n=32, <=1.050 n=46 (le1050 widened 43->46 vs 1845Z; "
             "le1020/le1030 held). Structural: 69 two-sided / 419 yes-only / 1 no-only / 11 empty = 86.2% not bracket-able "
             "(was 86.8% at 1845Z; YES-ask-only books cannot be bracketed - NO is a separate token book). "
             "Verbatim scan 55.2s: 0 BRACKETS, 0 asks[0] near-misses (artifact). supp min-ask: 69/500 priced, floor 1.0040, "
             "actionable(<=0.98) 0, best gross edge -0.0040 = floor 0.024 ABOVE the 0.98 actionable threshold - NOT actionable. "
             "All-time low 1.0010 (2200Z 10-10, tied 1728Z 10-12 Bolsonaro - now unbracketable, no asks either side) unchanged. "
             "0 positive gross edge anywhere = no arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended 1920Z')

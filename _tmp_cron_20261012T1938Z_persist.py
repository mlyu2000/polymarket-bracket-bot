import json

entry = {
    'ts_utc': '2026-10-12T1938Z',
    'markets': 500,
    'scan_time_s': 54.9,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 69,
    'structural': {'two_sided': 69, 'yes_only': 419, 'no_only': 2, 'both_empty': 10},
    'best_ask_floor': 1.005,
    'best_gross_edge': -0.005,
    'near_1.000_1.005': [
        [1.005, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.99, 21005.63121],
    ],
    'tiers': {'le_1005': 1, 'le_1010': 11, 'le_1020': 26, 'le_1030': 33, 'le_1050': 45},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR REVERTED 1.0040->1.0050 since 1920Z: the 1920Z floor market Levante UD vs. Sevilla FC: Sevilla FC "
             "O/U 4.5 (1.0040, Y@0.020 N@0.984, liq 2414.37) had its ENTIRE NO book emptied of asks (yes_asks=9, "
             "no_asks=0) while the YES ladder was swept 0.020->0.260 (liq 2414->2277) - now yes-only and unbracketable. "
             "Same failure pattern as Flavio Bolsonaro 8-12% margin @1728Z (cheap asks taken, NO side emptied). "
             "Galatasaray SK (-2.5) HOLDS floor 1.0050 SOLO (Y@0.015 N@0.990, 33 YES asks + 10 NO asks, liq 21005.63; "
             "21.1k@1920Z -> 21.0k). Band <=1.005 n=1 (was 2). NH-02 Dem House seat LOOSENED 1.0060->1.0200 "
             "(Y@0.953 N@0.067; NO side moved 0.052->0.067, liq 50.8k unchanged) - dropped out of the band. NEW #2: "
             "SK Slovan Bratislava (-2.5) TIGHTENED 1.0070->1.0060 (Y@0.008 N@0.998, liq 12734.83->13845.89). "
             "Amsterdam 13C Oct 14 held 1.0090 (liq 2424.16->2784.02). Hormuz agreement combo loosened to 1.0110 "
             "(Y@0.137 N@0.874, liq 119.7k@1845Z -> 37.1k). Tiers: <=1.005 n=1 (was 2), <=1.010 n=11 (was 14), "
             "<=1.020 n=26 (was 28), <=1.030 n=33 (was 32 - tightened), <=1.050 n=45 (was 46). Structural: "
             "69 two-sided / 419 yes-only / 2 no-only (NEW: Map Handicap 6666 (-1.5) vs megoshort (+1.5), liq 5.6) / "
             "10 empty = 86.2% not bracket-able (YES-ask-only books cannot be bracketed - NO is a separate token book). "
             "Verbatim scan 54.9s: 0 BRACKETS, 0 asks[0] near-misses (artifact). supp min-ask: 69/500 priced, floor "
             "1.0050, actionable(<=0.98) 0, best gross edge -0.0050 = floor 0.025 ABOVE the 0.98 actionable threshold "
             "- NOT actionable (worsened from -0.0040 @1920Z). All-time low 1.0010 (2200Z 10-10) unchanged. "
             "0 positive gross edge anywhere = no arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended 1938Z')

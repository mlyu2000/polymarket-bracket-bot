import json

entry = {
    'ts_utc': '2026-10-12T2023Z',
    'markets': 500,
    'scan_time_s': 53.6,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 68,
    'structural': {'two_sided': 68, 'yes_only': 424, 'no_only': 0, 'both_empty': 8},
    'best_ask_floor': 1.005,
    'best_gross_edge': -0.005,
    'near_1.000_1.005': [
        [1.005, 'Spread: Galatasaray SK (-2.5)', 0.015, 0.99, 22954.21211],
    ],
    'tiers': {'le_1005': 1, 'le_1010': 14, 'le_1020': 28, 'le_1030': 32, 'le_1050': 44},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR LOOSENED 1.0030->1.0050 at scan time: the 2010Z floor market (NH-02 Dem House seat 1.0030, Y@0.954 N@0.049 "
             "liq 61.1k) is NO LONGER in the active-500 fetch (market-set rotation; verified absent via follow-up query). "
             "Galatasaray SK (-2.5) HELD 1.0050 as new solo floor (Y@0.015 N@0.990 liq 21149.59->22954.21, +1.8k refill). "
             "Slovan Bratislava (-2.5) HELD 1.0060 (liq 13833.88). Levante UD vs. Sevilla FC: Sevilla FC O/U 4.5 loosened "
             "1.0040->1.0070 at scan time (Y@0.008 N@0.999 liq 2327.91) BUT re-tightened to 1.0030 within minutes "
             "(follow-up fetch: Y@0.008 N@0.995 liq 2327.91) = back at the old floor level; band <=1.005 n=1 at scan time "
             "(n=2 if post-scan re-tighten counts). Hormuz agreement HELD 1.0090 (liq 36500->38807.40). "
             "Band <=1.005 n=2->1; tiers <=1.005 n=1 <=1.010 n=14 <=1.020 n=28 <=1.030 n=32 <=1.050 n=44 "
             "(le1010/le1020 widened 12->14/27->28; le1050 tightened 46->44). Structural: 68 two-sided / 424 yes-only / "
             "0 no-only / 8 empty = 86.4% not bracket-able (was 86.0% at 2010Z; YES-ask-only books cannot be bracketed - "
             "NO is a separate token book). Verbatim scan 53.6s: 0 BRACKETS, 0 asks[0] near-misses (artifact). "
             "supp min-ask: 68/500 priced, floor 1.0050, actionable(<=0.98) 0, best gross edge -0.0050 = floor 0.025 ABOVE "
             "the 0.98 actionable threshold - NOT actionable. All-time low 1.0010 (2200Z 10-10, tied 1728Z 10-12 Bolsonaro "
             "- now unbracketable, no asks either side) unchanged. 0 positive gross edge anywhere = no arb."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
print('appended 2023Z')

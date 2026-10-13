import json

entry = {
    'ts_utc': '2026-10-13T1121Z',
    'markets': 500,
    'scan_time_s': 53.4,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'two_sided': 68,
    'yes_only': 423,
    'no_only': 1,
    'empty': 8,
    'not_bracketable_pct': round(100 * (423 + 1 + 8) / 500, 1),
    'best_ask_floor': 1.0010,
    'tiers': {'le1000': 0, 'le1005': 7, 'le1010': 21, 'le1020': 29, 'le1030': 35},
    'median_two_sided': 1.03,
    'near_1.000_1.010': [
        [1.0010, 'Will Elon Musk post 500+ tweets from October 9 to October 16, 2026?', 0.003, 0.998, 7848.56],
        [1.0020, 'Spread: SK Slovan Bratislava (-3.5)', 0.004, 0.998, 16034.66],
        [1.0030, 'FC Internazionale Milano vs. Club Brugge KV: Club Brugge KV O/U 3.5', 0.012, 0.991, 13055.73],
        [1.0030, 'Will Fernando Mendoza have 3,500+ passing yards in the 2026-27 NFL regular season?', 0.06, 0.943, 232.02],
        [1.0040, 'Exact Score: Venezia FC 4 - 3 SSC Napoli?', 0.006, 0.998, 2177.43],
        [1.0040, 'Spread: Sporting Kansas City (-3.5)', 0.005, 0.999, 3042.89],
        [1.0050, 'Exact Score: Venezia FC 4 - 1 SSC Napoli?', 0.009, 0.996, 2075.53],
        [1.0060, 'Exact Score: Venezia FC 3 - 4 SSC Napoli?', 0.01, 0.996, 2149.75],
        [1.0070, 'Spread: SK Slovan Bratislava (-2.5)', 0.009, 0.998, 18434.50],
        [1.0080, 'Exact Score: Venezia FC 4 - 2 SSC Napoli?', 0.009, 0.999, 2340.42],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'tracked_floor_market': {
        'q': 'Will US unemployment reach at least 6.0% in 2026?',
        'active': True, 'closed': False,
        'min_ask': 0.004, 'max_bid': 0.002,
        'n_asks': 25, 'n_bids': 2,
        'true_floor': 1.0020,
        'in_top500_window': False,
    },
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "NEW window floor 1.0010 (Elon Musk 500+ tweets Oct 9-16, Y@0.003 N@0.998, liq=7848.56) — displaces "
             "Slovan -3.5 to #2 at 1.0020. Floor improved 1.0020->1.0010 (+0.001) driven by a fresh low-priced YES leg. "
             "Structural 68 two-sided/423 yes-only/1 no-only/8 empty-of-500 (86.4% not bracketable); no-only 0->1. "
             "tiers le1.005 n=7, le1.010 n=21, le1.020 n=29, le1.030 n=35 (all up +1~+2 vs 1041Z run); median two-sided "
             "unchanged 1.030. detector-opps 0, paper 0; no sum < 1.00 anywhere = zero positive gross edge; floor 1.0010, "
             "best gross edge -0.0010, still 0.021 above the 0.98 actionable threshold. Tracked unemployment-6.0% mkt "
             "re-verified via gamma public-search (event 'How high will US unemployment go in 2026?' active+held, end "
             "2027-04-01) + direct CLOB /book: Y min-ask 0.004 (25 asks)/max-bid 0.002 (2 bids), N min-ask 0.998 (2 asks)/"
             "max-bid 0.996 (25 bids) = 1.0020 true floor, ties window floor, still out of top-500 window."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:200], '...')

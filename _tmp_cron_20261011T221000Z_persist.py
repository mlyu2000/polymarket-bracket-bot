import json

entry = {
    'ts_utc': '2026-10-11T2210Z',
    'markets': 500,
    'scan_time_s': 57.0,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 58,
    'two_sided': 58,
    'yes_only': 425,
    'no_only': 3,
    'empty': 14,
    'best_ask_floor': 1.0020,
    'near_1.000_1.005': [
        [1.0020, 'Will Elon Musk post 420-439 tweets from October 6 to October 12?', 0.027, 0.975, 12920.17394],
        [1.0030, 'Will the price of Ethereum be between $3,000 and $3,100 on October 12?', 0.004, 0.999, 3587.56323],
        [1.0040, 'Will the price of Bitcoin be above $90,000 on October 14?', 0.016, 0.988, 40161.25742],
        [1.0050, 'Real Valladolid CF vs. Albacete Balompie: O/U 7.5', 0.010, 0.995, 3446.53922],
        [1.0050, 'Spread: Viking FK (-1.5)', 0.015, 0.990, 16133.99144],
    ],
    'tiers': {'le_1010': 15, 'le_1020': 22},
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "Floor HELD at 1.0020 (ties 2142Z/2156Z) but floor market ROTATED off Galatasaray -2.5 (now 1.0080) "
             "onto Elon Musk 420-439 tweets Oct 6-12 (Y@0.027 N@0.975, liq 12.9k); BTC >$90k Oct 14 rose 1.0020->1.0040. "
             "Band<=1.005 n=5 (was 4): added Viking FK -1.5 spread 1.0050. Tiers le_1010 n=15, le_1020 n=22. "
             "Structural: two_sided 58 (was 60), yes_only 425 (flat), no_only 3, empty 14 — ~88% NOT bracket-able; "
             "NO cannot be acquired by hitting YES bids (separate token book), so ask-only bracket check is complete. "
             "detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge; "
             "floor 1.0020, best gross edge -0.0020, still 0.022 above the 0.98 actionable threshold; "
             "all-time low 1.0010 (2200Z 10-10, Chicago 90-91F) unchanged."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

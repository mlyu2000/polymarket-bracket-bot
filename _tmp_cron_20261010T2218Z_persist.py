import json

entry = {
    'ts_utc': '2026-10-10T2218Z',
    'markets': 500,
    'scan_time_s': 53.2,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': 80,
    'best_ask_floor': 1.005,
    'near_1.000_1.005': [
        [1.005, 'Al Fayha Saudi Club vs. Al Riyadh Saudi Club: O/U 7.5', 0.009, 0.996, 2250.23196],
        [1.005, 'Calcio Padova vs. Carrarese Calcio: O/U 7.5', 0.01, 0.995, 3045.91565],
        [1.005, 'Gaziantep FK vs. Çorum FK: O/U 7.5', 0.01, 0.995, 4262.95566],
        [1.005, 'JEF United Ichihara Chiba vs. V-Varen Nagasaki: O/U 7.5', 0.009, 0.996, 4417.04301],
    ],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.0050, band widened n=3->4: Al Fayha Saudi Club vs. Al Riyadh O/U 7.5 re-entered the band "
             "(YES ask 0.010->0.009, sum 1.006->1.005, liq 2249.71->2250.23). Other 3 held with liquidity churn: "
             "Calcio Padova/Carrarese O/U 7.5 1.005 Yes@0.010 No@0.995 liq 3028.79->3045.92 (+0.6%); Gaziantep FK/Çorum FK "
             "O/U 7.5 liq 4106.15->4262.96 (+3.8%); JEF United/V-Varen Nagasaki O/U 7.5 liq 4270.01->4417.04 (+3.5%, YES "
             "ask ticked 0.010->0.009). Next tier 1.006 (FK LNZ Cherkasy liq 2673.87 ~flat, Konyaspor 3430.16, Silkeborg "
             "2861.02), then 1.007 Dynamo Kyiv/Karpaty, 1.008 Lille spread + Bochum. priced 68->80 (+12, normal inter-call "
             "variance 45-80); scan 53.2s (fast). detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero "
             "positive gross edge; floor 1.005, best gross edge -0.005, still 0.025 above the 0.98 actionable threshold."),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:140], '...')

import json
supp = json.load(open('_tmp_cron_20261010T1051Z_supp_data.json'))
entry = {
    'ts_utc': '2026-10-10T10:51Z',
    'markets': supp['markets'],
    'scan_time_s': 50.0,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in supp['band']],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
             "min-ask floor authoritative. FLOOR HELD 1.005 third consecutive run "
             "(after revert 1.002->1.005 at 10:04Z); band n=1->1 sole holder Clermont "
             "prices unchanged Yes@0.008 No@0.997 liq 2938.10->2930.47 (-0.26%). "
             "Kyoto/Kolos still out of band. priced 72->73. "
             "next tier: 1.006 liq 3717.9 Falkirk FC vs. Dun (flat); "
             "1.007 liq 3105.3 HNK Hajduk Split v (sum flat, liq -12.5%); "
             "1.008 liq 2949.1 Al Ettifaq Saudi C (flat); "
             "1.010 liq 11584.8 AEK Athens vs. OFI (new in tier; Dplus KIA Worlds "
             "low-liq dropped out); 1.010 liq 9020.5 Asteras Tripolis v; "
             "1.010 liq 45869.7 Atalanta BC vs. Venezia. "
             "detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = "
             "zero positive gross edge, no actionable arb; floor 1.005, "
             "best gross edge -0.005, still 0.025 above 0.98 actionable threshold"),
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:', json.dumps(entry)[:120], '...')

import json, shutil, os

TS = '20261010T1236Z'
band = [[1.005, "Falkirk FC vs. Dundee FC: O/U 7.5", 0.012, 0.993, 3867.32164]]
floor = 1.005
priced = 62

data = {
    'ts_utc': '2026-10-10T12:36Z',
    'markets': 500,
    'scan_time_s': 49.9,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': priced,
    'best_ask_floor': floor,
    'near_1.000_1.005': band,
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD 1.005 second consecutive run. Band n=1 unchanged: sole holder Falkirk FC vs. Dundee FC: O/U 7.5 "
             "1.005 Yes@0.012 No@0.993 flat, liq 3830.5->3867.3 +1.0%. "
             "priced 66->62 (-4). next tier Al Ettifaq 1.008 liq 2868.7 (was 1.008), Genoa O/U 4.5 1.008 liq 377.4 new, "
             "NE Revolution exact-score 1.009 liq 2644.6, AEK Athens 1.010 liq 30365.8. "
             "detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, "
             "no actionable arb; floor 1.005, best gross edge -0.005, still 0.025 above 0.98 actionable threshold."),
}

for f in [f'_tmp_cron_{TS}_scan_verbatim.py', f'_tmp_cron_{TS}_supp_minask.py',
          f'_tmp_cron_{TS}_scan_out.txt', f'_tmp_cron_{TS}_supp_out.txt',
          f'_tmp_cron_{TS}_supp_data.json']:
    if os.path.exists(f):
        shutil.copy(f, 'runs/' + f.replace('_tmp_', ''))

with open(f'runs/{TS}_scan_data.json', 'w') as fh:
    json.dump(data, fh, indent=2)

with open('results/cron_scan_history.jsonl', 'a') as fh:
    fh.write(json.dumps(data) + '\n')

print('persisted:', f'runs/{TS}_scan_data.json', '+ history entry appended')
print('history lines:', sum(1 for _ in open('results/cron_scan_history.jsonl')))

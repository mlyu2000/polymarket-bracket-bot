import json, shutil, os

TS = '20261010T1207Z'
band = [[1.005, "Falkirk FC vs. Dundee FC: O/U 7.5", 0.012, 0.993, 3830.49132]]
floor = 1.005
priced = 66

data = {
    'ts_utc': '2026-10-10T12:07Z',
    'markets': 500,
    'scan_time_s': 47.7,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': priced,
    'best_ask_floor': floor,
    'near_1.000_1.005': band,
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR REGRESSED 1.002->1.005 (worse by 0.003). Band 2->1: adds ['Falkirk FC vs. Dundee FC: O/U 7.5'], "
             "drops ['Clermont Foot 63 vs. Red Star FC: O/U 7.5' (was 1.002)], "
             "['Notts County FC vs. Oxford United FC: Oxford United FC O/U 4' (was 1.005, ultra-low-liq 30.5)]. "
             "Sole holder Falkirk 1.005 Yes@0.012 No@0.993 liq 3830.5. "
             "priced 70->66 (-4). next tier Hajduk/Dinamo 1.009, Al Ettifaq 1.008, NE Revolution exact-score 1.009, "
             "AEK Athens 1.010. detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, "
             "no actionable arb; floor 1.005, best gross edge -0.005, still 0.025 above 0.98 actionable threshold."),
}

# copy run artifacts into runs/
for f in [f'_tmp_cron_{TS}_scan_verbatim.py', f'_tmp_cron_{TS}_supp_minask.py',
          f'_tmp_cron_{TS}_scan_out.txt', f'_tmp_cron_{TS}_supp_out.txt']:
    shutil.copy(f, 'runs/' + f.replace('_tmp_', ''))

with open(f'runs/{TS}_scan_data.json', 'w') as fh:
    json.dump(data, fh, indent=2)

with open('results/cron_scan_history.jsonl', 'a') as fh:
    fh.write(json.dumps(data) + '\n')

print('persisted:', f'runs/{TS}_scan_data.json', '+ history entry appended')
print('history lines:', sum(1 for _ in open('results/cron_scan_history.jsonl')))

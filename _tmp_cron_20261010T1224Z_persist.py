import json, shutil, os

TS = '20261010T1224Z'
band = [[1.005, "Falkirk FC vs. Dundee FC: O/U 7.5", 0.012, 0.993, 3830.49132]]
floor = 1.005
priced = 65

data = {
    'ts_utc': '2026-10-10T12:24Z',
    'markets': 500,
    'scan_time_s': 50.7,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': priced,
    'best_ask_floor': floor,
    'near_1.000_1.005': band,
    'detector_opps': 0,
    'paper_trades': 0,
    'note': ("verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
             "FLOOR HELD at 1.005 (same as 12:07Z run). Band 1->1: sole holder Falkirk 1.005 Yes@0.012 No@0.993 liq 3830.5 unchanged. "
             "priced 66->65 (-1). next tier Al Ettifaq 1.008, NE Revolution exact-score 1.009; Hajduk/Dinamo 1.009 from prior run dropped out. "
             "detector-opps 0, paper 0 executions; no sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
             "best gross edge -0.005, 0.025 above 0.98 actionable threshold."),
}

os.makedirs('runs', exist_ok=True)
for f in [f'_tmp_cron_{TS}_scan_verbatim.py', f'_tmp_cron_20261010T1210Z_supp_minask.py']:
    if os.path.exists(f):
        shutil.copy(f, 'runs/' + f.replace('_tmp_', ''))

with open(f'runs/{TS}_scan_data.json', 'w') as fh:
    json.dump(data, fh, indent=2)

with open('results/cron_scan_history.jsonl', 'a') as fh:
    fh.write(json.dumps(data) + '\n')

print('persisted:', f'runs/{TS}_scan_data.json', '+ history entry appended')
print('history lines:', sum(1 for _ in open('results/cron_scan_history.jsonl')))

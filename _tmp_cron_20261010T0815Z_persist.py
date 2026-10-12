import json

supp = json.load(open('_tmp_cron_20261010T0815Z_supp_data.json'))
cur_band = supp['band']

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}

entry = {
    'ts_utc': '2026-10-10T08:15Z',
    'markets': supp['markets'],
    'scan_time_s': 50.1,
    'brackets_verbatim': 0,
    'near_misses_verbatim_asks0': 0,
    'priced_minask': supp['priced'],
    'best_ask_floor': supp['floor'],
    'near_1.000_1.005': [list(r) for r in cur_band],
    'detector_opps': 0,
    'paper_trades': 0,
    'note': '',
}

# Build note dynamically from data
def liq_of(rows, name):
    for r in rows:
        if r[1] == name:
            return r[4]
    return None

note = (
    "verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); "
    f"min-ask floor authoritative. FLOOR HELD 1.005 sixth consecutive run "
    f"({supp['band'][0][1]} Yes@{supp['band'][0][2]} No@{supp['band'][0][3]} "
    f"liq {supp['band'][0][4]}). "
    f"band n={len(prev_band)}->{len(cur_band)}; "
    f"adds {sorted(cur_names - prev_names)}, drops {sorted(prev_names - cur_names)}. "
    f"priced {last.get('priced_minask')}->{supp['priced']}; "
    "detector opportunities: 0. Paper trades: 0. "
    "No sum < 1.00 anywhere = zero positive gross edge, no actionable arb; "
    "floor stable 1.005, best gross edge -0.005 vs parity."
)
entry['note'] = note

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended entry:')
print(json.dumps(entry, indent=1, ensure_ascii=False))

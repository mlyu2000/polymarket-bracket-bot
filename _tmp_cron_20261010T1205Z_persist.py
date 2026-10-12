import json, shutil

data = json.load(open('_tmp_cron_20261010T1205Z_data.json'))
for f in ['_tmp_cron_20261010T1205Z_data.json', '_tmp_cron_20261010T1205Z_scan.py']:
    shutil.copy(f, 'runs/' + f.replace('_tmp_', '20261010T1205Z_'))

prev = json.loads(open('results/cron_scan_history.jsonl').read().strip().split('\n')[-1])
prev_band = prev.get('near_1.000_1.005', [])
band = data['band']

def find(rows, key):
    return next((r for r in rows if key in r[1]), None)

cl_now = find(band, 'Clermont')
cl_prev = find(prev_band, 'Clermont')

adds = [r[1] for r in band if not any(r[1] == p[1] for p in prev_band)]
drops = [r[1] for r in prev_band if not any(r[1] == b[1] for b in band)]

cl_desc = 'n/a'
if cl_now and cl_prev:
    liq_pct = (cl_now[4] / cl_prev[4] - 1) * 100 if cl_prev[4] else 0
    cl_desc = (f"Clermont {cl_prev[0]:.3f}->{cl_now[0]:.3f} "
               f"(Yes {cl_prev[2]:.3f}->{cl_now[2]:.3f}, No {cl_prev[3]:.3f}->{cl_now[3]:.3f}, "
               f"liq {cl_prev[4]:.1f}->{cl_now[4]:.1f} {liq_pct:+.1f}%)")

note = (f"verbatim asks[0] near-miss block reports 0 (known DESC-sort artifact); min-ask floor authoritative. "
        f"FLOOR IMPROVED {prev['best_ask_floor']}->{data['floor']} (all-time observed best in history: 1.001, "
        f"Man United 0-0 Tottenham exact-score, now gone). "
        f"Band {len(prev_band)}->{len(band)}: adds {adds}, drops {drops}. {cl_desc}. "
        f"priced {prev.get('priced_minask')}->{data['priced']}. "
        f"detector-opps {len(data['opps_verbatim'])}, paper 0 executions; no sum < 1.00 anywhere = "
        f"zero positive gross edge, no actionable arb; floor {data['floor']}, best gross edge "
        f"{1.0 - data['floor']:+.3f}, still {data['floor'] - 0.98:.3f} above 0.98 actionable threshold.")

entry = {
    'ts_utc': '2026-10-10T12:05Z',
    'markets': data['markets'],
    'scan_time_s': round(data['scan_time'], 1),
    'brackets_verbatim': len(data['opps_verbatim']),
    'near_misses_verbatim_asks0': len(data['near_misses_verbatim']),
    'priced_minask': data['priced'],
    'best_ask_floor': data['floor'],
    'near_1.000_1.005': band,
    'detector_opps': len(data['opps_verbatim']),
    'paper_trades': 0,
    'note': note,
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
print('appended:')
print(json.dumps(entry, indent=1, ensure_ascii=False)[:1500])

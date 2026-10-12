import json
lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
print('prev ts:', prev.get('ts') or prev.get('timestamp'))
print('prev keys:', list(prev))
prev_band = sorted({r[1] for r in prev.get('near_1.000_1.005', [])}) if prev.get('near_1.000_1.005') else []
print('prev floor:', prev.get('best_ask_floor'))
print('prev band size:', len(prev_band))

supp = json.load(open('_tmp_cron_20261010T2359Z_supp_data.json'))
cur_band = sorted({r[1] for r in supp['band']})
adds = [q for q in cur_band if q not in prev_band]
drops = [q for q in prev_band if q not in cur_band]
print('cur floor:', supp['floor'])
print('cur band size:', len(cur_band))
print('adds:', adds)
print('drops:', drops)

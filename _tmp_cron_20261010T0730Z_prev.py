import json

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
supp = json.load(open('_tmp_cron_20261010T0730Z_supp_data.json'))
cur_band = supp['band']
prev_band = last['near_1.000_1.005']
prev_names = {r[1] for r in prev_band}
cur_names = {r[1] for r in cur_band}
print('PREV ts:', last['ts_utc'])
print('PREV floor:', last['best_ask_floor'], '| priced:', last['priced_minask'])
print('PREV band:', prev_band)
print('CUR floor:', supp['floor'], '| priced:', supp['priced'])
print('CUR band:', cur_band)
print('adds:', sorted(cur_names - prev_names), '| drops:', sorted(prev_names - cur_names))
print('prev floor holder liq:', prev_band[0][4] if prev_band else None)

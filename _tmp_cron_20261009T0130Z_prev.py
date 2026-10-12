import json

with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
prev = json.loads(lines[-1])
print('prev ts:', prev['ts_utc'], 'floor:', prev['best_ask_floor'], 'priced:', prev['priced_minask'])
band = sorted({q for _, q, *_ in prev.get('near_1.000_1.005', [])})
print('prev band', len(band))
for q in band:
    print(' -', q)

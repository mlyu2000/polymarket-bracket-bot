import json, time

ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
src = f'runs/_tmp_cron_{ts}_supp_data.json'
data = json.load(open(src))

hist_path = 'results/cron_scan_history.jsonl'
line = {
    'ts': ts,
    'markets': data['markets'],
    'scan_time': data['scan_time'],
    'brackets': 0,
    'floor': data['floor'],
    'tiers': data['tiers'],
}
with open(hist_path, 'a') as f:
    f.write(json.dumps(line) + '\n')

print('appended history line:')
print(json.dumps(line))

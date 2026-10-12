import json

lines = open('results/cron_scan_history.jsonl').read().strip().splitlines()
for l in lines[-2:]:
    d = json.loads(l)
    print(d['ts_utc'], '| markets', d['markets'], '| floor', d.get('best_ask_floor'),
          '| band', len(d.get('near_1.000_1.005', [])), '| brackets', d.get('brackets_verbatim'))
    for row in d.get('near_1.000_1.005', []):
        print('   ', row)

import json
lines = open('results/cron_scan_history.jsonl').read().splitlines()
print('total entries:', len(lines))
for line in lines[-6:]:
    d = json.loads(line)
    print(d['ts_utc'], 'floor', d.get('best_ask_floor'), 'band', len(d.get('near_1.000_1.005', [])),
          'brackets', d.get('brackets_verbatim'), 'priced', d.get('priced_minask'))

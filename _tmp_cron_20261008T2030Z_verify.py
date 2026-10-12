import json
lines = open('results/cron_scan_history.jsonl').read().splitlines()
print('total entries:', len(lines))
for l in lines[-2:]:
    d = json.loads(l)
    print(d['ts_utc'], '| markets', d['markets'], '| priced', d['priced_minask'],
          '| floor', d['best_ask_floor'], '| band', len(d['near_1.000_1.005']),
          '| brackets', d['brackets_verbatim'], '| paper', d['paper_trades'])

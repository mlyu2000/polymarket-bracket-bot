import json
lines = open('results/cron_scan_history.jsonl').read().strip().split('\n')
for l in lines[-3:]:
    d = json.loads(l)
    print(d['ts_utc'], '| markets', d.get('markets'), '| floor', d.get('best_ask_floor'),
          '| near', len(d.get('near_1.000_1.005', [])), '| brackets', d.get('brackets_verbatim'))
    print('   note:', d.get('note', '')[:250])

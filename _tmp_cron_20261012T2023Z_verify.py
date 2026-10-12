import json
lines = open('results/cron_scan_history.jsonl').read().strip().split('\n')
d = json.loads(lines[-1])
print(d['ts_utc'], '| floor:', d['best_ask_floor'], '| edge:', d['best_gross_edge'], '| tiers:', d['tiers'], '| struct:', d['structural'])

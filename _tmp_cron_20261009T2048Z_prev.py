import json
lines = [l for l in open('results/cron_scan_history.jsonl') if l.strip()]
prev = json.loads(lines[-1])
print(json.dumps({k: prev[k] for k in ('ts_utc','best_ask_floor','priced_minask','near_1.000_1.005')}, indent=1))

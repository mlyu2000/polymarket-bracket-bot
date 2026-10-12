import json
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
r = json.loads(lines[-1])
print(json.dumps(r, indent=1)[:1500])

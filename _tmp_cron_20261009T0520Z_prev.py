import json
with open('results/cron_scan_history.jsonl') as f:
    lines = [l for l in f if l.strip()]
r = json.loads(lines[-1])
band = sorted({q for _, q, *_ in r.get('near_1.000_1.005', [])})
print('records:', len(lines))
print('prev:', r['ts_utc'], 'floor=', r['best_ask_floor'], 'priced=', r.get('priced_minask'),
      'band=', len(band), 'brackets=', r['brackets_verbatim'])
print('git status:')
import subprocess
print(subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout or '(clean)')

"""Append this cron run's min-ask diagnostic to results/cron_scan_history.jsonl
(same schema as prior lines). Local + unpushed.
"""
import json

TS = '20261015T1521Z'
SCAN_TIME_VERBATIM = 64.0

d = json.load(open('runs/_tmp_cron_20261015T1521Z_supp_data.json'))

record = {
    'ts': TS,
    'brackets': 0,
    'markets': d['markets'],
    'two_sided': d['two_sided'],
    'pct_not_bracketable': round(100.0 * d['not_bracketable'] / d['markets'], 1),
    'tiers': {
        'le1.005': d['tiers']['<=1.005'],
        'le1.010': d['tiers']['<=1.010'],
        'le1.020': d['tiers']['<=1.020'],
        'le1.050': d['tiers']['<=1.050'],
        'lt1.000': d['tiers']['<1.000'],
    },
    'floor': d['top25'][0]['total'],
    'top12': [
        {'total': r['total'], 'q': r['q'], 'yes': r['yes'], 'no': r['no'], 'liq': r['liq']}
        for r in d['top25'][:12]
    ],
    'scan_time_verbatim': SCAN_TIME_VERBATIM,
    'scan_time_minask': d['scan_time'],
    'asks0_near_miss_artifact': 0,
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(record) + '\n')

print(json.dumps(record, indent=2)[:800])

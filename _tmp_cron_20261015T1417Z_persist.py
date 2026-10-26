"""Persist this cron run's min-ask diagnostic into results/cron_scan_history.jsonl
and refresh runs/_tmp_cron_20261015T1417Z_tiers.json. Local + unpushed.
"""
import json, time

TS = '20261015T1417Z'
PREV_TIERS = {'1.005': 9, '1.01': 17, '1.02': 28, '1.05': 62}
PREV_FLOOR = 1.001
PREV_LEADER_LIQ = 1164.2261
PREV_PRICED = 77

d = json.load(open(f'runs/_tmp_cron_{TS}_supp_data.json'))


def tier(n):
    return d['tiers']['le1.005'] if n == '1.005' else (
        d['tiers']['le1.010'] if n == '1.01' else (
        d['tiers']['le1.020'] if n == '1.02' else (
        d['tiers']['le1.050'] if n == '1.05' else None)))


tiers = {}
for k in ['1.005', '1.01', '1.02', '1.05']:
    tiers[k] = tier(k)

delta = {k: tiers[k] - PREV_TIERS[k] for k in tiers}
delta_str = ', '.join(f"{k} n{tiers[k]} ({'+' if delta[k] > 0 else ''}{delta[k]})" for k in tiers)

leader = d['top12'][0]
floor = d['top12'][0][0]

record = {
    'run_ts_utc': TS,
    'markets': d['markets'],
    'scan_time_s': d['scan_time'],
    'brackets': 0,
    'near_miss_count': d['tiers']['le1.005'],
    'near_misses_top': [
        {'sum': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]}
        for r in d['top12'][:5]
    ],
    'floor': floor,
    'tiers': {**tiers, '1.1': None},
    'bracketable': d['two_sided'],
    'not_bracketable': d['not_bracketable'],
    'asks0_near_miss_artifact': 0,
    'method': 'min(all asks) — detector-equivalent; asks[0] is worst ask (DESC sort)',
}

with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(record) + '\n')

tiers_out = {
    'ts': TS,
    'markets': d['markets'],
    'priced': d['with_both_asks'],
    'scan_time': d['scan_time'],
    'one_sided': d['one_sided'],
    'tiers': tiers,
    'top12': d['top12'],
}
with open(f'runs/_tmp_cron_{TS}_tiers.json', 'w') as f:
    json.dump(tiers_out, f, indent=2)

print(json.dumps({'record': record, 'tiers_delta': delta_str,
                  'leader_liq_delta': round(leader[4] - PREV_LEADER_LIQ, 1),
                  'priced_delta': d['two_sided'] - PREV_PRICED}, indent=2))

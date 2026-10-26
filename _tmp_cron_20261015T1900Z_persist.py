"""Persist cron run 20261015T1900Z min-ask diagnostic + diff vs 18:41Z run.
Local + unpushed (per user rule: runs are git-persisted).
"""
import json

TS = '20261015T1900Z'

out = open(f'_tmp_cron_{TS}_supp_out.txt').read()
rows_json = out.split('ROWS_JSON:', 1)[1].split('\n', 1)[0].strip()
rows = json.loads(rows_json)
brackets_json = out.split('BRACKETS_JSON:', 1)[1].split('\n', 1)[0].strip()
brackets = json.loads(brackets_json)
stats_line = [l for l in out.splitlines() if l.startswith('STATS:')][0]
stats = dict(kv.split('=') for kv in stats_line.replace('STATS: ', '').split())

two_sided = int(stats['two_sided'])
lt1 = int(stats['lt1'])
le1005 = int(stats['le1005'])
le1010 = int(stats['le1010'])
le1020 = int(stats['le1020'])
le1050 = int(stats['le1050'])
floor = float(stats['floor'])
floor_q = rows[0][1]
leader_liq = rows[0][4]

markets = 500
scan_time_verbatim = 57.1

# --- build supp_data.json (same shape as prior runs) ---
top25 = [[round(r[0], 4), r[1], r[2], r[3], r[4], r[5]] for r in rows[:25]]
data = {
    'ts': TS,
    'markets': markets,
    'scan_time': scan_time_verbatim,
    'priced': two_sided,
    'with_both_asks': two_sided,
    'one_sided': markets - two_sided,
    'two_sided': two_sided,
    'not_bracketable': markets - two_sided,
    'brackets': brackets,
    'lt1': lt1,
    'tiers': {
        'lt1.000': lt1,
        'le1.005': le1005,
        'le1.010': le1010,
        'le1.020': le1020,
        'le1.050': le1050,
    },
    'floor': floor,
    'floor_q': floor_q,
    'leader_liq': leader_liq,
    'top25': top25,
}
with open(f'runs/_tmp_cron_{TS}_supp_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# --- append to cron_scan_history.jsonl (same shape as prior runs) ---
record = {
    'ts': TS,
    'markets': markets,
    'scan_time_verbatim': scan_time_verbatim,
    'brackets': 0,
    'near_miss_verbatim': 0,
    'near_miss_artifact_note': 'asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth',
    'floor_min_ask': floor,
    'leader': floor_q[:60],
    'leader_liq': leader_liq,
    'tiers': {'<=1.050': le1050, '<=1.020': le1020, '<=1.010': le1010, '<=1.005': le1005, '<1.000': lt1},
    'two_sided': two_sided,
    'not_bracketable': markets - two_sided,
    'top12': [{'total': r[0], 'q': r[1], 'liq': r[4]} for r in rows[:12]],
}
with open('results/cron_scan_history.jsonl', 'a') as f:
    f.write(json.dumps(record) + '\n')

# --- tiers.json snapshot ---
tiers_out = {
    'ts': TS,
    'markets': markets,
    'priced': two_sided,
    'scan_time': scan_time_verbatim,
    'one_sided': markets - two_sided,
    'tiers': {'1.005': le1005, '1.01': le1010, '1.02': le1020, '1.05': le1050},
    'top25': [{'total': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]} for r in rows[:25]],
}
with open(f'runs/_tmp_cron_{TS}_tiers.json', 'w') as f:
    json.dump(tiers_out, f, indent=2)

# --- diff vs previous run (18:41Z) ---
hist = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
prev_jsonl = hist[-2]
prev_top12 = {t['q']: (t['total'], t['liq']) for t in prev_jsonl['top12']}

print('=== tier deltas (18:41Z -> 19:00Z) ===')
pt = prev_jsonl['tiers']
print(f"le1.005 {pt['<=1.005']}->{le1005} ({le1005 - pt['<=1.005']:+d})")
print(f"le1.010 {pt['<=1.010']}->{le1010} ({le1010 - pt['<=1.010']:+d})")
print(f"le1.020 {pt['<=1.020']}->{le1020} ({le1020 - pt['<=1.020']:+d})")
print(f"le1.050 {pt['<=1.050']}->{le1050} ({le1050 - pt['<=1.050']:+d})")
print(f"two_sided {prev_jsonl['two_sided']}->{two_sided} ({two_sided - prev_jsonl['two_sided']:+d})")
print(f"floor {prev_jsonl['floor_min_ask']}->{floor} | leader liq {prev_jsonl['leader_liq']}->{leader_liq} ({leader_liq - prev_jsonl['leader_liq']:+.1f}, {(leader_liq/prev_jsonl['leader_liq']-1)*100:+.1f}%)")

print('=== top-25 movers vs 18:41Z (names present in both) ===')
cur_map = {r[1]: (r[0], r[4]) for r in rows[:25]}
for q, (tot, liq) in cur_map.items():
    if q in prev_top12:
        ptot, pliq = prev_top12[q]
        if abs(liq - pliq) > 50 or abs(tot - ptot) > 1e-9:
            pct = ((liq/pliq-1)*100) if pliq else 0
            print(f"  {q[:45]}: {ptot:.3f}->{tot:.3f} | liq {pliq:.1f}->{liq:.1f} ({liq-pliq:+.1f}, {pct:+.1f}%)")

print('=== NEW in top-25 (absent from prev top-12) ===')
for r in rows[:25]:
    if r[1] not in prev_top12:
        print(f"  NEW {r[0]:.3f} | liq {r[4]:.1f} | {r[1][:55]}")

print('=== dropped from prev top-12 ===')
for q, (tot, liq) in prev_top12.items():
    if q not in cur_map:
        print(f"  DROP {tot:.3f} | liq {liq:.1f} | {q[:55]}")

print('=== persists done ===')
print(f"runs/_tmp_cron_{TS}_supp_data.json + runs/_tmp_cron_{TS}_tiers.json + results/cron_scan_history.jsonl")

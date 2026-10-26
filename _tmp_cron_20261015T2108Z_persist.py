"""Persist this cron run (20261015T2108Z) min-ask diagnostic + diff vs 20:55Z.
Local + unpushed (per user rule: runs are git-persisted).
BoJ 50+ bps market dropped out of active-500 universe this scan.
"""
import json

TS = '20261015T2108Z'

supp = json.load(open(f'runs/_tmp_cron_{TS}_supp_data.json'))
rows = supp['top25']
two_sided = supp['two_sided']
not_bracketable = supp['not_bracketable']
tiers = supp['tiers']
floor = supp['floor']
leader = supp['floor_q']
leader_liq = supp['leader_liq']

markets = 500
scan_time_verbatim = 62.3

le1005 = tiers['le1.005']
le1010 = tiers['le1.010']
le1020 = tiers['le1.020']
le1050 = tiers['le1.050']
lt1 = tiers['lt1.000']

# --- build supp_data.json (same shape as prior runs) ---
top25 = [[round(r[0], 4), r[1], r[2], r[3], r[4]] for r in rows[:25]]
data = {
    'ts': TS,
    'markets': markets,
    'scan_time': scan_time_verbatim,
    'priced': two_sided,
    'with_both_asks': two_sided,
    'one_sided': markets - two_sided,
    'two_sided': two_sided,
    'not_bracketable': not_bracketable,
    'brackets': [],
    'lt1': lt1,
    'tiers': {
        'lt1.000': lt1,
        'le1.005': le1005,
        'le1.010': le1010,
        'le1.020': le1020,
        'le1.050': le1050,
    },
    'floor': floor,
    'floor_q': leader,
    'leader_liq': leader_liq,
    'top25': top25,
    'note': 'BoJ 50+ bps cuts market no longer in active-500 universe (0 japan/bps hits); Lagarde 2027 now sole floor holder',
}
with open(f'runs/_tmp_cron_{TS}_supp_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# --- append to cron_scan_history.jsonl (idempotent; same shape as prior runs) ---
lines = open('results/cron_scan_history.jsonl').read().splitlines()
lines = [l for l in lines if f'"ts": "{TS}"' not in l]
with open('results/cron_scan_history.jsonl', 'w') as f:
    f.write('\n'.join(lines) + '\n')
record = {
    'ts': TS,
    'markets': markets,
    'scan_time_verbatim': scan_time_verbatim,
    'brackets': 0,
    'near_miss_verbatim': 0,
    'near_miss_artifact_note': 'asks[0] is worst ask (DESC-sorted /book); verbatim near-miss block always 0; min-ask diag is source of truth',
    'floor_min_ask': floor,
    'leader': leader[:60],
    'leader_liq': leader_liq,
    'tiers': {'<=1.050': le1050, '<=1.020': le1020, '<=1.010': le1010, '<=1.005': le1005, '<1.000': lt1},
    'two_sided': two_sided,
    'not_bracketable': not_bracketable,
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

# --- diff vs previous run (20:55Z; handles both history-line shapes) ---
prev_jsonl = [json.loads(l) for l in open('results/cron_scan_history.jsonl')][-2]
prev_top12 = {t['q']: (t['total'], t['liq']) for t in prev_jsonl.get('top12', [])}
pt = prev_jsonl['tiers']
p_le1005 = pt.get('<=1.005', pt.get('le_1_005'))
p_le1010 = pt.get('<=1.010', pt.get('le_1_010'))
p_le1020 = pt.get('<=1.020', pt.get('le_1_020'))
p_le1050 = pt.get('<=1.050', pt.get('le_1_050'))
if 'floor_min_ask' in prev_jsonl:
    p_floor, p_leader_liq = prev_jsonl['floor_min_ask'], prev_jsonl['leader_liq']
else:
    p_floor = prev_jsonl['floor'][0]
    p_leader_liq = prev_jsonl['floor'][4]
p_two_sided = prev_jsonl.get('two_sided', 'n/a')

print('=== tier deltas (20:55Z -> 21:08Z) ===')
print(f"le1.005 {p_le1005}->{le1005} ({le1005 - p_le1005:+d})")
print(f"le1.010 {p_le1010}->{le1010} ({le1010 - p_le1010:+d})")
print(f"le1.020 {p_le1020}->{le1020} ({le1020 - p_le1020:+d})")
print(f"le1.050 {p_le1050}->{le1050} ({le1050 - p_le1050:+d})")
if isinstance(p_two_sided, int):
    print(f"two_sided {p_two_sided}->{two_sided} ({two_sided - p_two_sided:+d})")
else:
    print(f"two_sided n/a->{two_sided} (prev 20:55Z line lacked field)")
print(f"floor {p_floor}->{floor} | leader liq {p_leader_liq}->{leader_liq} ({leader_liq - p_leader_liq:+.1f}, {(leader_liq/p_leader_liq-1)*100:+.1f}%)")

print('=== top-10 leaders vs 20:55Z (names present in both) ===')
cur_map = {r[1]: (r[0], r[4]) for r in rows}
for q, (tot, liq) in cur_map.items():
    if q in prev_top12:
        ptot, pliq = prev_top12[q]
        if abs(liq - pliq) > 50 or abs(tot - ptot) > 1e-9:
            pct = ((liq/pliq-1)*100) if pliq else 0
            print(f"  {q[:45]}: {ptot:.3f}->{tot:.3f} | liq {pliq:.1f}->{liq:.1f} ({liq-pliq:+.1f}, {pct:+.1f}%)")

print('=== NEW in top-10 (absent from prev top-12) ===')
for r in rows:
    if r[1] not in prev_top12:
        print(f"  NEW {r[0]:.3f} | liq {r[4]:.1f} | {r[1][:55]}")

print('=== dropped from prev top-12 ===')
for q, (tot, liq) in prev_top12.items():
    if q not in cur_map:
        print(f"  DROP {tot:.3f} | liq {liq:.1f} | {q[:55]}")

print('=== persists done ===')
print(f"runs/_tmp_cron_{TS}_supp_data.json + runs/_tmp_cron_{TS}_tiers.json + results/cron_scan_history.jsonl")

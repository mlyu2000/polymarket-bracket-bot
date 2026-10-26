"""Persist this cron run (20261015T212712Z) min-ask diagnostic + diff vs 21:08Z.
Local + unpushed (per user rule: runs are git-persisted).
Key event: spread-cluster re-exit (Thun -4.5/-5.5, Kobenhavn -4.5, PA House Dems
left the active-500 universe; Jablonec -4.5 + Man City 0-2 Ipswich went YES-only).
Floor 1.001 HELD (Lagarde 2027 sole holder, sum unchanged).
"""
import json, os

TS = '20261015T212712Z'
PREV_TS = '20261015T2108Z'

supp = json.load(open(f'runs/_tmp_cron_{TS}_supp_rows.json'))
rows = supp['top25']  # list of [total, q, yp, np_, liq]
two_sided = supp['two_sided']
yes_only = supp['yes_only']
na_only = supp['na_only']
not_bracketable = supp['not_bracketable']
tiers = supp['tiers']
floor = supp['floor_min_ask']
leader = rows[0]
leader_q = leader[1]
leader_liq = leader[4]

markets = 500
scan_time_verbatim = 55.3

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
    'yes_only': yes_only,
    'na_only': na_only,
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
    'floor_q': leader_q,
    'leader_liq': leader_liq,
    'top25': top25,
    'note': 'spread-cluster re-exit: Thun(-4.5/-5.5), Kobenhavn(-4.5), PA House Dems 12+ left active-500 universe; Jablonec(-4.5) + Man City 0-2 Ipswich went YES-only; Jablonec(-5.5) worsened 1.005->1.008; NEW exact-score Bayern 1-3 Leipzig two-sided; floor 1.001 HELD (Lagarde sole holder)',
}
with open(f'runs/_tmp_cron_{TS}_supp_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# --- append to cron_scan_history.jsonl (idempotent) ---
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
    'leader': leader_q[:60],
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

# --- diff vs previous run (21:08Z) ---
hist = [json.loads(l) for l in open('results/cron_scan_history.jsonl')]
prev = [h for h in hist if h.get('ts') == PREV_TS]
prev = prev[-1] if prev else hist[-2]
prev_top12 = {t['q']: (t['total'], t['liq']) for t in prev.get('top12', [])}
pt = prev['tiers']
p_le1005 = pt.get('<=1.005')
p_le1010 = pt.get('<=1.010')
p_le1020 = pt.get('<=1.020')
p_le1050 = pt.get('<=1.050')
p_floor = prev.get('floor_min_ask')
p_leader_liq = prev.get('leader_liq')
p_two_sided = prev.get('two_sided', 'n/a')

print('=== tier deltas (21:08Z -> 21:27Z) ===')
print(f"le1.005 {p_le1005}->{le1005} ({le1005 - p_le1005:+d})")
print(f"le1.010 {p_le1010}->{le1010} ({le1010 - p_le1010:+d})")
print(f"le1.020 {p_le1020}->{le1020} ({le1020 - p_le1020:+d})")
print(f"le1.050 {p_le1050}->{le1050} ({le1050 - p_le1050:+d})")
if isinstance(p_two_sided, int):
    print(f"two_sided {p_two_sided}->{two_sided} ({two_sided - p_two_sided:+d})")
    print(f"not_bracketable {prev.get('not_bracketable')}->{not_bracketable} ({not_bracketable - prev.get('not_bracketable', 0):+d}, {not_bracketable/markets*100:.1f}%)")
print(f"floor {p_floor}->{floor} | leader liq {p_leader_liq}->{leader_liq} ({leader_liq - p_leader_liq:+.1f}, {(leader_liq/p_leader_liq-1)*100:+.1f}%)")

print('=== top-10 leaders vs 21:08Z (present in both) ===')
cur_map = {r[1]: (r[0], r[4]) for r in rows}
for q, (tot, liq) in cur_map.items():
    if q in prev_top12:
        ptot, pliq = prev_top12[q]
        if abs(liq - pliq) > 50 or abs(tot - ptot) > 1e-9:
            pct = ((liq/pliq-1)*100) if pliq else 0
            print(f"  {q[:45]}: {ptot:.3f}->{tot:.3f} | liq {pliq:.1f}->{liq:.1f} ({liq-pliq:+.1f}, {pct:+.1f}%)")

print('=== NEW in top-12 (absent from 21:08Z top-12) ===')
for r in rows[:12]:
    if r[1] not in prev_top12:
        print(f"  NEW {r[0]:.3f} | liq {r[4]:.1f} | {r[1][:55]}")

print('=== dropped from 21:08Z top-12 (verified: left-universe / YES-only) ===')
VERIFIED = {
    'Spread: FC Thun (-4.5)': 'left active-500 universe',
    'Spread: FC Thun (-5.5)': 'left active-500 universe',
    'Spread: FK Jablonec (-4.5)': 'YES-only (NO-leg bid-only, still active)',
    'Spread: FC K\u00f8benhavn (-4.5)': 'left active-500 universe',
    'Exact Score: Manchester City FC 0 - 2 Ipswich Town FC?': 'YES-only (NO-leg bid-only, still active)',
    'Will Democrats win 12 or more House seats in Pennsylvania in the 2026 midterm election?': 'left active-500 universe',
}
for q, (tot, liq) in prev_top12.items():
    if q not in cur_map:
        tag = VERIFIED.get(q, '(lower-tier or unresolved; fell below top-25)')
        print(f"  DROP {tot:.3f} | liq {liq:.1f} | {q[:48]} -- {tag}")

print('=== frozen-book check (Bitcoin) ===')
btc = [r for r in rows if 'Bitcoin more valuable' in r[1]]
if btc:
    print(f"  Bitcoin liq={btc[0][4]} (21:08Z was 3934.17625 -> {'BYTE-IDENTICAL' if abs(btc[0][4]-3934.17625)<1e-6 else 'CHANGED'})")

print('=== persists done ===')
print(f"runs/_tmp_cron_{TS}_supp_data.json + runs/_tmp_cron_{TS}_tiers.json + results/cron_scan_history.jsonl")
print(f"prev_ts_used={prev.get('ts')}")

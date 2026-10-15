"""Diff 17:23Z scan vs 17:08Z run for the commit message / report. Read-only."""
import json

TS = '20261015T172346Z'

records = [json.loads(l) for l in open('results/cron_scan_history.jsonl') if l.strip()]
def ts_of(r):
    return r.get('ts') or r.get('run_ts_utc')

cur = [r for r in records if ts_of(r) == TS][0]
prev = [r for r in records if ts_of(r) == '2026-10-15T17:08Z'][0]

d = json.load(open(f'runs/_tmp_cron_{TS}_supp_data.json'))
rows = [r for r in d['top25']]

print('=== tier deltas (17:08Z -> 17:23Z) ===')
pt = prev['tiers']; ct = cur['tiers']
for k, label in [('<=1.005','le1.005'), ('<=1.010','le1.010'), ('<=1.020','le1.020'), ('<=1.050','le1.050')]:
    print(f"{label} {pt[k]}->{ct[k]} ({ct[k]-pt[k]:+d})")
print(f"two_sided {prev['two_sided']}->{cur['two_sided']} ({cur['two_sided']-prev['two_sided']:+d})")
print(f"floor {prev['floor_min_ask']}->{cur['floor_min_ask']} | leader liq {prev['leader_liq']}->{cur['leader_liq']} ({cur['leader_liq']-prev['leader_liq']:+.1f}, {(cur['leader_liq']/prev['leader_liq']-1)*100:+.1f}%)")

prev_top12 = {t['q']: (t['total'], t['liq']) for t in prev['top12']}
cur_map = {r[1]: (r[0], r[4]) for r in rows}

print('=== names in both scans (changes) ===')
for q, (tot, liq) in cur_map.items():
    if q in prev_top12:
        ptot, pliq = prev_top12[q]
        if abs(liq - pliq) > 50 or abs(tot - ptot) > 1e-9:
            print(f"  {q[:45]}: {ptot:.3f}->{tot:.3f} | liq {pliq:.1f}->{liq:.1f} ({liq-pliq:+.1f}, {((liq/pliq)-1)*100 if pliq else 0:+.1f}%)")

print('=== NEW in top-25 (absent from 17:08Z top-12) ===')
for r in rows:
    if r[1] not in prev_top12:
        print(f"  NEW {r[0]:.3f} | Yes@{r[2]} No@{r[3]} | liq {r[4]:.1f} | {r[1][:55]}")

print('=== dropped from 17:08Z top-12 ===')
for q, (tot, liq) in prev_top12.items():
    if q not in cur_map:
        print(f"  DROP {tot:.3f} | liq {liq:.1f} | {q[:55]}")

print('=== clusters at identical price/liq this scan (structural) ===')
import collections
groups = collections.defaultdict(list)
for r in rows:
    groups[(r[0], r[2], r[3])].append((r[1], r[4]))
for k, v in groups.items():
    if len(v) >= 3:
        print(f"  sum={k[0]:.3f} Yes@{k[1]} No@{k[2]} x{len(v)}: {', '.join(n[:40] for n,_ in v)}")

print('=== byte-identical liq check (frozen books) ===')
for r in rows:
    if r[1] in prev_top12 and r[4] == prev_top12[r[1]][1]:
        print(f"  FLAT {r[1][:55]} liq {r[4]:.1f}")

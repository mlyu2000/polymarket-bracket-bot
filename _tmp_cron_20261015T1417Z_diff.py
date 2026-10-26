"""Diff top12 between previous (1356Z) and current (1417Z) run."""
import json

old = json.load(open('runs/_tmp_cron_20261015T1356Z_tiers.json'))['top12']
new = json.load(open('runs/_tmp_cron_20261015T1417Z_tiers.json'))['top12']

o = {r[1]: (round(r[0], 4), round(r[4])) for r in old}
n = {r[1]: (round(r[0], 4), round(r[4])) for r in new}

print('=== 1356Z (prev) ===')
for q, (s, liq) in sorted(o.items(), key=lambda kv: kv[1][0]):
    print(f'  {s:.3f} liq {liq:>7} | {q[:55]}')
print('=== 1417Z (now) ===')
for q, (s, liq) in sorted(n.items(), key=lambda kv: kv[1][0]):
    print(f'  {s:.3f} liq {liq:>7} | {q[:55]}')
print('=== DROPPED ===')
for q in sorted(o.keys() - n.keys()):
    s, liq = o[q]
    print(f'  {s:.3f} liq {liq:>7} | {q[:55]}')
print('=== NEW ===')
for q in sorted(n.keys() - o.keys()):
    s, liq = n[q]
    print(f'  {s:.3f} liq {liq:>7} | {q[:55]}')
print('=== MOVES ===')
for q in sorted(o.keys() & n.keys()):
    os_, ol = o[q]
    ns_, nl = n[q]
    if os_ != ns_ or abs(nl - ol) > max(50, 0.02 * ol):
        print(f'  {os_:.3f}->{ns_:.3f} liq {ol:>7}->{nl:>7} ({nl-ol:+.0f}) | {q[:55]}')

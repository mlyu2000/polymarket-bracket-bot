"""Final diff: match on q[:50] prefix vs prior run's full top-25. Read-only."""
import json

TS = '20261015T172346Z'
PREV = '20261015T1707Z'

cur = json.load(open(f'runs/_tmp_cron_{TS}_tiers.json'))['top25']       # dicts
prev = json.load(open(f'runs/_tmp_cron_{PREV_TS if False else "20261015T1707Z"}_supp_data.json'))['top25']  # dicts

def key(t):
    return t['q'][:50]

cur_map = {key(t): t for t in cur}
prev_map = {key(t): t for t in prev}

print('=== movers (both top-25s, >50 liq or sum change) ===')
for k, t in cur_map.items():
    if k in prev_map:
        p = prev_map[k]
        if abs(t['liq'] - p['liq']) > 50 or abs(t['total'] - p['total']) > 1e-9:
            print(f"  {key(t)[:45]}: {p['total']:.3f}->{t['total']:.3f} | liq {p['liq']:.1f}->{t['liq']:.1f} ({t['liq']-p['liq']:+.1f}, {((t['liq']/p['liq'])-1)*100 if p['liq'] else 0:+.1f}%)")

print('=== NEW in top-25 ===')
for k, t in cur_map.items():
    if k not in prev_map:
        print(f"  NEW {t['total']:.3f} | liq {t['liq']:.1f} | {t['q'][:58]}")

print('=== dropped from top-25 ===')
for k, t in prev_map.items():
    if k not in cur_map:
        print(f"  DROP {t['total']:.3f} | liq {t['liq']:.1f} | {t['q'][:58]}")

print('=== byte-identical liq vs prior scan ===')
for k, t in cur_map.items():
    if k in prev_map and t['liq'] == prev_map[k]['liq']:
        print(f"  FLAT {t['q'][:55]} liq {t['liq']:.1f} (total {t['total']:.3f}->{prev_map[k]['total']:.3f} unchanged)")

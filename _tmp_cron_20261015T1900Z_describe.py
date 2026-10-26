import json

TS = '20261015T1900Z'
data = json.load(open(f'runs/_tmp_cron_{TS}_supp_data.json'))

rows = data['top25']
print('=== full top-25 ===')
for r in rows:
    print(f"  {r[0]:.4f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq {r[4]:.1f} | {r[1][:60]}")

# NFL futures cluster: rows are [total, q, yes, no, liq, opp]
nfl = [r for r in rows if 'finish the 2026-27 NFL regular' in r[1]]
print(f'=== NFL futures in top25: {len(nfl)} ===')
for r in nfl:
    print(f"  {r[0]:.4f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq {r[4]:.1f} | {r[1][:55]}")
es = [r for r in rows if ' - ' in r[1] and any(c.isdigit() for c in r[1])]
print(f'=== exact-score in top25: {len(es)} ===')
for r in es:
    print(f"  {r[0]:.4f} | liq {r[4]:.1f} | {r[1][:55]}")

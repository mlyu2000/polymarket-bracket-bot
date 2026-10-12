import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TS = "2026-10-12T1005Z"

async def supp():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    rows = []
    priced = 0
    one_sided = 0
    both_empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_has = bool(yb and yb.asks)
        n_has = bool(nb and nb.asks)
        if y_has and n_has:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((round(yp + np_, 4), m.question[:60], round(yp, 3), round(np_, 3), round(m.liquidity, 2)))
        elif y_has or n_has:
            one_sided += 1
        else:
            both_empty += 1
    rows.sort()
    return len(markets), priced, one_sided, both_empty, rows, scan_time

markets_n, priced_n, one_sided, both_empty, rows, scan_time = asyncio.run(supp())
print(f"priced markets: {priced_n}/{markets_n} | one-sided: {one_sided} | both-empty: {both_empty} | scan {scan_time:.1f}s")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
    best_gross_edge = round(1.0 - rows[0][0], 4)
    print(f"best gross edge: {best_gross_edge}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f}")
print(f"band <=1.005: {len(band)}")
for r in band[:8]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
next_tier = [r for r in rows if r[0] <= 1.008 and r[0] > 1.005]
print(f"tier 1.006-1.008: {len(next_tier)}")
for r in next_tier[:6]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
tiers = {
    'le_1010': len([r for r in rows if r[0] <= 1.010]),
    'le_1020': len([r for r in rows if r[0] <= 1.020]),
    'le_1030': len([r for r in rows if r[0] <= 1.030]),
}
print(f"tiers: {tiers}")
actionable = [r for r in rows if r[0] <= 0.98]
print(f"actionable (sum<=0.98): {len(actionable)}")

with open('runs/_tmp_cron_20261012T1005Z_supp_data.json', 'w') as f:
    json.dump({'ts': TS, 'markets': markets_n, 'priced': priced_n,
               'one_sided': one_sided, 'both_empty': both_empty,
               'scan_time': round(scan_time, 1),
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'best_gross_edge': best_gross_edge if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band],
               'next_tier': [list(r) for r in next_tier[:6]],
               'tiers': tiers,
               'actionable': len(actionable)}, f, indent=1)
print("supp data written")

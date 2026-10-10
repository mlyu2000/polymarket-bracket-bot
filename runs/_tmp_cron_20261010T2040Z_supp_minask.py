import asyncio, logging, json, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TS = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT = f'runs/_tmp_cron_{TS}_supp_data.json'

async def supp():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    rows = []
    priced = 0
    both_sided = 0
    one_sided = 0
    both_empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya = bool(yb and yb.asks)
        na = bool(nb and nb.asks)
        if ya and na:
            both_sided += 1
        elif ya or na:
            one_sided += 1
        else:
            both_empty += 1
        if not (ya and na):
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((round(yp + np_, 4), m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), priced, rows, scan_time, both_sided, one_sided, both_empty

markets_n, priced_n, rows, scan_time, both_sided, one_sided, both_empty = asyncio.run(supp())
print(f"markets: {markets_n} | priced (both-sided): {priced_n} | scan {scan_time:.1f}s")
print(f"book health: {both_sided} both-sided / {one_sided} one-sided / {both_empty} both-empty")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]:.2f}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print(f"band <=1.005: {len(band)}")
for r in band[:10]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print(f"next tier (1.005-1.010):")
for r in [x for x in rows if 1.005 < x[0] <= 1.010][:5]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
with open(OUT, 'w') as f:
    json.dump({'ts': TS, 'markets': markets_n, 'priced': priced_n, 'scan_time': scan_time,
               'both_sided': both_sided, 'one_sided': one_sided, 'both_empty': both_empty,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band[:15]]}, f, indent=1)
print(f"saved -> {OUT}")

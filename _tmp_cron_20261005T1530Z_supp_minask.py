import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def sup():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        tot = yp + np
        priced += 1
        rows.append((tot, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"priced_markets={priced}")
    lm = [r for r in rows if r[0] < 1.0]
    print(f"true_brackets_sum_lt_1={len(lm)}")
    for r in lm[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"near_misses_1.00_to_1.005={len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    floor = rows[0] if rows else None
    print(f"floor={floor[0]:.4f} ({floor[1]})" if floor else "floor=None")

asyncio.run(sup())

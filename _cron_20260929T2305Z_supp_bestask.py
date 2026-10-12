import asyncio, logging, time
from polymarket_api import PolymarketAPI
from config import Config

logging.basicConfig(level=logging.ERROR)

async def main():
    t0 = time.time()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    el = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a["price"]) for a in yb.asks)
        na = min(float(a["price"]) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"corrected best-ask scan: {len(markets)} markets in {el:.1f}s; priced pairs: {len(rows)}")
    if rows:
        print(f"floor sum: {rows[0][0]:.4f} | {rows[0][1]}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"brackets (best-ask sum < 1.00): {len(brackets)}")
    for r in brackets[:10]:
        print(f"  {r[0]:.4f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq {r[4]:.0f} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"near-misses (1.000-1.005): {len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.4f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq {r[4]:.0f} | {r[1]}")

asyncio.run(main())

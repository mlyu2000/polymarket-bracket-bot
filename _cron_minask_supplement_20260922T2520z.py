import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"markets with books: {len(rows)}")
    lm = [r for r in rows if r[0] < 1.00]
    nm = [r for r in rows if 1.00 <= r[0] <= 1.005]
    print(f"true brackets (<1.00): {len(lm)}")
    for s, q, ya, na, liq in lm[:10]:
        print(f"  {s:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")
    print(f"near-misses (<=1.005): {len(nm)}")
    for s, q, ya, na, liq in nm[:10]:
        print(f"  {s:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")
    print("global floor:")
    for s, q, ya, na, liq in rows[:5]:
        print(f"  {s:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())

import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"markets={len(markets)} priced={len(rows)} elapsed={time.time()-t0:.1f}s")
    for s, q, ya, na, liq in rows[:10]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())

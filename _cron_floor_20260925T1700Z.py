import asyncio, logging, time
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
            rows.append((ya+na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"markets with both books: {len(rows)}")
    print("floor (true min-ask sums):")
    for t,q,ya,na,liq in rows[:8]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0]<1.0)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0]<=1.005)}")

asyncio.run(main())

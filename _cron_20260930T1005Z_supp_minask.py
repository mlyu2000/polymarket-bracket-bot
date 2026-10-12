import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            tot = ya + na
            priced += 1
            rows.append((tot, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print(f"TRUE floor (best asks, sum<=1.005): {sum(1 for r in rows if r[0]<=1.005)}")
    print(f"sum<1.000: {sum(1 for r in rows if r[0]<1.000)}")
    for tot, q, ya, na, liq in rows[:10]:
        print(f"  {tot:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())

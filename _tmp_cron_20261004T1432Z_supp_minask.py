import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    floors = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        total = yp + np
        priced += 1
        if total <= 1.005:
            floors.append((total, m.question[:60], yp, np, m.liquidity))
    floors.sort()
    print(f"priced markets (min-ask): {priced}")
    print(f"min-ask near-misses (<=1.005): {len(floors)}")
    for t, q, yp, np, liq in floors[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(main())

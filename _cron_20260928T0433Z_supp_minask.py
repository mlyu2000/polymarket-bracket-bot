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
    floors = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            floors.append((ya + na, m.question[:55], ya, na, m.liquidity))
    floors.sort()
    brk = [f for f in floors if f[0] < 1.0]
    print(f"Markets with both books: {len(floors)}")
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brk)}")
    for t, q, ya, na, liq in brk[:10]:
        print(f"  🔴 {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("Lowest 5 true sums (min-ask):")
    for t, q, ya, na, liq in floors[:5]:
        print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())

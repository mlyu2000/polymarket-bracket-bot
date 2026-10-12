import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((y + n, y, n, m.question[:60], m.liquidity))
    rows.sort()
    print(f"min-ask floor across {len(rows)} priced markets: {rows[0][0]:.4f}")
    print("Top 5 best min-ask sums:")
    for s, y, n, q, liq in rows[:5]:
        print(f"  {s:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(main())

import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    below1 = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        t = y + n
        if t < 1.0 and m.liquidity > 0:
            below1 += 1
        rows.append((t, m.question[:55], y, n, m.liquidity))

    rows.sort()
    print(f"markets_with_books={len(rows)} sum_below_1.00={below1}")
    print("--- true floor (min-ask best) ---")
    for t, q, y, n, liq in rows[:8]:
        print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq={liq:,.0f} | {q}")
    print(f"count<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"count<=1.01: {sum(1 for r in rows if r[0] <= 1.01)}")

asyncio.run(main())

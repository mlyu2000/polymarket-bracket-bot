import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        y, n = best_ask(yb), best_ask(nb)
        t = y + n
        if t < 1.0:
            brackets.append((t, m.question[:60], y, n, m.liquidity))
        rows.append((t, m.question[:50], y, n))
    rows.sort()
    brackets.sort()
    print(f"markets with priced books: {len(rows)}")
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for t, q, y, n, liq in brackets[:10]:
        print(f"  {t:.3f} | Y@{y:.3f} N@{n:.3f} | liq={liq} | {q}")
    print("floor (best 8 min-ask sums):")
    for t, q, y, n in rows[:8]:
        print(f"  {t:.3f} | Y@{y:.3f} N@{n:.3f} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"min-ask near-misses (<=1.005): {len(nm)}")

asyncio.run(main())

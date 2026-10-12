import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    print(f"markets with both books: {len(rows)}")
    print("TOP 10 MIN-ASK TOTALS:")
    for t, q, y, n, liq in rows[:10]:
        print(f"  {t:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"TRUE BRACKETS (min-ask sum<1.00): {len(brackets)}")
    print(f"TRUE NEAR-MISSES (1.00-1.005): {len(nm)}")
    for t, q, y, n, liq in brackets + nm:
        print(f"  SUM={t:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(supp())

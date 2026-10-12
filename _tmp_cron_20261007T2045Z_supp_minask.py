import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        tot = yp + np
        priced += 1
        rows.append((tot, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"best-ask totals: {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print("top 8 lowest best-ask sums:")
    for tot, q, yp, np, liq in rows[:8]:
        print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"true brackets (sum<1.000): {len(under)} | near-misses (1.000..1.005): {len(nm)}")
    for tot, q, yp, np, liq in under:
        print(f"  BRACKET {tot:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())

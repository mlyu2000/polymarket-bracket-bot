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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            npr = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + npr, m.question[:55], yp, npr, m.liquidity))
    rows.sort()
    print(f"min-ask floor scan: {len(rows)} priced markets in {dt:.1f}s")
    print("top 8 lowest YES+NO min-ask sums:")
    for total, q, yp, npr, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (<=1.005): {len(nm)}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"min-ask brackets (<1.0): {len(brackets)}")

asyncio.run(scan())

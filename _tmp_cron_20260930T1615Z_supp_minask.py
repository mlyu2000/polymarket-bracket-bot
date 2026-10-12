import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity, m.active, m.closed))
    rows.sort()
    print(f"min-ask scan: {len(markets)} markets, {priced} with two-sided asks, {scan_time:.1f}s")
    below_1 = [r for r in rows if r[0] < 1.00]
    print(f"min-ask sum < 1.00: {len(below_1)}")
    for s, q, yp, np, liq, act, cl in below_1:
        print(f"  SUM {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} active={act} closed={cl} | {q}")
    print("best 10 min-ask sums:")
    for s, q, yp, np, liq, act, cl in rows[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())

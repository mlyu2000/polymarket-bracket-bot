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
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {len(rows)} priced, {dt:.1f}s")
    print("Top-10 lowest sums:")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")

asyncio.run(scan())

import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor_scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        if total <= 1.01:
            rows.append((total, ya, na, m.question[:60], m.liquidity))
    rows.sort()
    print(f"floor scan: {priced}/{len(markets)} priced in {time.time()-t0:.1f}s")
    print(f"markets with best-ask sum <= 1.01: {len(rows)}")
    for total, ya, na, q, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    if rows:
        print(f"TRUE FLOOR = {min(r[0] for r in rows):.4f}")

asyncio.run(floor_scan())

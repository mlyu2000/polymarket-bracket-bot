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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            s = ya + na
            priced += 1
            rows.append((s, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"MIN-ASK SCAN: {len(markets)} markets, {priced} priced, in {dt:.1f}s")
    print(f"BRACKETS sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"Worst-of-top (closest to bracket, sum<=1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
    for s, q, ya, na, liq in rows[:8]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())

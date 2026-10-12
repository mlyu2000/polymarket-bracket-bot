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
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return rows, len(markets), dt

rows, n, dt = asyncio.run(scan())
print(f"min-ask floor scan: {n} markets in {dt:.1f}s")
print(f"count with best-ask sum <= 1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"count with best-ask sum <  1.00 : {sum(1 for r in rows if r[0] <  1.00)}")
print("top-10 lowest best-ask sums:")
for total, q, ya, na, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        rows.append((total, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"Min-ask supplement: {priced} priced markets of {len(markets)} in {dt:.1f}s")
    print("Floor sums (best-ask Yes+No), 10 closest to <=1.00:")
    for total, q, ya, na, liq in rows[:10]:
        flag = " <-- BRACKET" if total < 1.0 else ""
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}{flag}")
    n_under_1005 = sum(1 for r in rows if r[0] <= 1.005)
    n_under_100 = sum(1 for r in rows if r[0] < 1.0)
    print(f"Count sum<1.000: {n_under_100} | sum<=1.005: {n_under_1005}")

asyncio.run(scan())

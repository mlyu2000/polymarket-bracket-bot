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
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        rows.append((total, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"bestask scan: {len(markets)} markets in {dt:.1f}s; priced={len(rows)}")
    print(f"sum<1.000: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"min sum: {rows[0][0]:.4f}" if rows else "no priced rows")
    for total, q, ya, na, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())

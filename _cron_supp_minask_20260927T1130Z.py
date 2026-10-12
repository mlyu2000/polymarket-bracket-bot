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
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        floors.append((ya + na, m.question[:55], ya, na, m.liquidity))
    floors.sort()
    print(f"min-ask floor scan: {len(floors)} priced markets in {dt:.1f}s")
    n_lt1 = sum(1 for f in floors if f[0] < 1.0)
    n_le1001 = sum(1 for f in floors if f[0] <= 1.001)
    print(f"min-ask sum<1.00: {n_lt1} | sum<=1.001: {n_le1001}")
    for total, q, ya, na, liq in floors[:8]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())

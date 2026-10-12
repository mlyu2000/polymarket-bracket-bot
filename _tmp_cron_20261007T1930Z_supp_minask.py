import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        priced += 1
        rows.append((total, m.question[:60], yes_min, no_min, m.liquidity))

    rows.sort()
    print(f"min-ask floor scan: {priced}/{len(markets)} markets priced")
    print(f"sum < 1.00 (true brackets): {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"sum <= 1.005 (near-misses): {sum(1 for r in rows if r[0] <= 1.005)}")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())

import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total = yes_min + no_min
            if total <= 1.005:
                rows.append((total, m.question[:55], yes_min, no_min, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print(f"MIN-ASK near-misses (sum<=1.005): {len(rows)}")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if not rows:
        # report overall floor anyway
        all_totals = []
        for m, (yes_book, no_book) in zip(markets, all_books):
            if yes_book and no_book and yes_book.asks and no_book.asks:
                t = min(float(a['price']) for a in yes_book.asks) + min(float(a['price']) for a in no_book.asks)
                all_totals.append((t, m.question[:55]))
        all_totals.sort()
        print("FLOOR (lowest 5 min-ask sums):")
        for t, q in all_totals[:5]:
            print(f"  {t:.3f} | {q}")

asyncio.run(supp())

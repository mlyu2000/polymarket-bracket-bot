import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    below_1 = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            best.append((total, m.question[:50], ya, na, m.liquidity))
            if total < 1.0:
                below_1.append((total, m.question[:50], ya, na, m.liquidity))
    best.sort()
    print(f"Total priced markets (min-ask): {len(best)}")
    print(f"MIN-ASK sums < 1.00: {len(below_1)}")
    for t, q, ya, na, liq in below_1:
        print(f"  sum={t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("Top 10 closest (min-ask best total):")
    for t, q, ya, na, liq in best[:10]:
        print(f"  sum={t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())

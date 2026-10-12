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

    # True floor: min() of asks (asks are DESC-sorted in /book API)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    print(f"markets with both books: {len(rows)} / {len(markets)}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (min-ask, <=1.005): {len(nm)}")
    brackets = [r for r in rows if r[0] < 1.000]
    print(f"sum<1.000 by min-ask: {len(brackets)}")
    for total, q, ya, na, liq in nm[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("top-5 lowest overall:")
    for total, q, ya, na, liq in rows[:5]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())

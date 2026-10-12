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
    below_1 = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        if total < 1.0:
            below_1 += 1
        rows.append((total, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    return len(markets), priced, below_1, rows

n, priced, below_1, rows = asyncio.run(scan())
print(f"Floor scan (min-ask): {n} markets, {priced} priced both-sides, {below_1} with sum<1.00")
print("Lowest 8 Yes+No best-ask sums:")
for total, q, ya, na, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")

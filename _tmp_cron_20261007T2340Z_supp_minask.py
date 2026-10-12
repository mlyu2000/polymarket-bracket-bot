import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp >= 1.0 or np >= 1.0 or yp <= 0 or np <= 0:
            continue
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"priced markets (min-ask): {priced}")
print("--- 10 lowest best-ask sums ---")
for total, q, yp, np, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"--- near-miss count (min-ask <= 1.005): {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"--- sub-1.00 count (min-ask): {sum(1 for r in rows if r[0] < 1.0)}")

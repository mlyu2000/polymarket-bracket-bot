import asyncio, logging
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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    if rows:
        print(f"true floor (min sum): {rows[0][0]:.4f}")
    print("best 8 by min-ask sum:")
    for total, q, yp, np, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.00)}")

asyncio.run(scan())

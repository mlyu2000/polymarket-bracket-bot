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
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("--- best min-ask sums (YES+NO) ---")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())

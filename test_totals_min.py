import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test_totals_min():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print(f"markets {len(markets)}")
    totals = []
    for m in markets[:50]:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            totals.append(total)
            print(f"{total:.3f} yes {yp:.3f} no {np:.3f} | {m.question[:60]}")
    if totals:
        print(f"min total {min(totals):.3f}, max {max(totals):.3f}, avg {sum(totals)/len(totals):.3f}")

asyncio.run(test_totals_min())

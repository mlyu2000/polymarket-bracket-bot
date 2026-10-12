import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    best_total = 2.0
    best_m = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_best = float(yes_book.asks[0]['price'])
            no_best = float(no_book.asks[0]['price'])
            total = yes_best + no_best
            if total < best_total:
                best_total = total
                best_m = m.question[:80]
    print(f"Best total using asks[0]: {best_total:.4f} for {best_m}")

asyncio.run(test())

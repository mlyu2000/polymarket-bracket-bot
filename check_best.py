import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=50)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_prices = [float(a['price']) for a in yes_book.asks]
            no_prices = [float(a['price']) for a in no_book.asks]
            yes_best = min(yes_prices)
            no_best = min(no_prices)
            total = yes_best + no_best
            if total < 1.0:
                print("BRACKET!", m.question[:60], total, yes_best, no_best)
            if total <= 1.005:
                print(f"Near {total:.3f} {m.question[:60]} yes_best={yes_best} no_best={no_best}")

asyncio.run(test())

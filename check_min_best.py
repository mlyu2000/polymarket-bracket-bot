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
    best_yes = None
    best_no = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_prices = [float(a['price']) for a in yes_book.asks]
            no_prices = [float(a['price']) for a in no_book.asks]
            yes_best = min(yes_prices)
            no_best = min(no_prices)
            total = yes_best + no_best
            if total < best_total:
                best_total = total
                best_m = m.question[:80]
                best_yes = yes_best
                best_no = no_best
    print(f"Best total min ask: {best_total:.4f} for {best_m}")
    print(f"Yes best: {best_yes}, No best: {best_no}")

asyncio.run(test())

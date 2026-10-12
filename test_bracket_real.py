import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    detector = BracketDetector()
    total = 0
    brackets = 0
    near = 0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            total_cost = float(yes_ask["price"]) + float(no_ask["price"])
            total += 1
            if total_cost < 1.0:
                brackets += 1
                print('BRACKET', m.question[:60], total_cost, yes_ask, no_ask)
            elif total_cost <= 1.005:
                near += 1
                #print('NEAR', m.question[:60], total_cost)
    print('checked', total, 'brackets', brackets, 'near', near)

asyncio.run(test())

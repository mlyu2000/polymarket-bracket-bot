import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=50)
    count=0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
            no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
            total = yes_price + no_price
            if total < 1.005:
                count+=1
                print(total, m.question[:60], yes_price, no_price, m.liquidity)
    print('total near', count)

asyncio.run(test())

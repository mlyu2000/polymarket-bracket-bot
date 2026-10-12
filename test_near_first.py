import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print('markets', len(markets))
    count=0
    for m in markets[:20]:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(yes_book.asks[0]['price'])
            no_price = float(no_book.asks[0]['price'])
            total = yes_price + no_price
            if total <= 1.005:
                print('near', m.question[:60], total, yes_price, no_price)
                count+=1
    print('found near', count)

asyncio.run(test())

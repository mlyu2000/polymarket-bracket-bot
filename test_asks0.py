import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, all_books):
        print(m.question[:60])
        if yes_book and no_book and yes_book.asks and no_book.asks:
            print(" yes asks[0]:", yes_book.asks[0])
            print(" no asks[0]:", no_book.asks[0])
            yes_price = float(yes_book.asks[0]['price'])
            no_price = float(no_book.asks[0]['price'])
            print(" total:", yes_price+no_price)

asyncio.run(test())

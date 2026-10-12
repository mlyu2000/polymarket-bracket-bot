import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print('markets', len(markets))
    for i,m in enumerate(markets[:5]):
        print(i, m.question[:60], m.liquidity, m.clob_token_ids)
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book:
            print('yes asks first 5', yes_book.asks[:5])
            print('yes asks last 5', yes_book.asks[-5:])
        if no_book:
            print('no asks first 5', no_book.asks[:5])
            print('no asks last 5', no_book.asks[-5:])
        print()

asyncio.run(test())

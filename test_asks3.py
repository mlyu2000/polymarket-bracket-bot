import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test_asks():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(m.question[:60])
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book:
            print(' yes asks len', len(yes_book.asks))
            if yes_book.asks:
                print(' yes asks[0]', yes_book.asks[0])
                print(' yes asks[-1]', yes_book.asks[-1])
        if no_book:
            print(' no asks len', len(no_book.asks))
            if no_book.asks:
                print(' no asks[0]', no_book.asks[0])
                print(' no asks[-1]', no_book.asks[-1])
        print('---')

asyncio.run(test_asks())

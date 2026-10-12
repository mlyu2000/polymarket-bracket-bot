import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test_asks():
    api = PolymarketAPI()
    # Get first market
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print(m.question)
    books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
    yes_book, no_book = books[0]
    print('yes asks len', len(yes_book.asks) if yes_book else 0)
    if yes_book:
        print('yes asks[0]', yes_book.asks[0])
        print('yes asks[-1]', yes_book.asks[-1])
    if no_book:
        print('no asks[0]', no_book.asks[0])
        print('no asks[-1]', no_book.asks[-1])

asyncio.run(test_asks())

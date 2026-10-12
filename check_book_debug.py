import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=1)
    token_pairs = [(m[0].clob_token_ids[0], m[0].clob_token_ids[1])]
    books = await api.fetch_order_books_batch(token_pairs)
    yes_book, no_book = books[0]
    print('Market:', m[0].question[:80])
    print('Yes asks:', yes_book.asks[:5] if yes_book else None)
    print('No asks:', no_book.asks[:5] if no_book else None)

asyncio.run(f())

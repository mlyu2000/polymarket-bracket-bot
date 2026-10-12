import asyncio
from polymarket_api import PolymarketAPI
import time

async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=5)
    print(len(m))
    print(m[0].question[:80])
    print(m[0].clob_token_ids)
    t = time.time()
    books = await api.fetch_order_books_batch([(m[0].clob_token_ids[0], m[0].clob_token_ids[1])])
    print('books', books)
    print('time', time.time()-t)

asyncio.run(f())

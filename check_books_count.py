import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print('markets', len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print('books', len(all_books))
    ok = 0
    for y,n in all_books:
        if y and n and y.asks and n.asks:
            ok += 1
    print('ok books', ok)

asyncio.run(f())

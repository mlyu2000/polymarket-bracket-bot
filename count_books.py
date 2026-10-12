import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count_no_no = 0
    count_both = 0
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if yes_book and yes_book.asks and no_book and no_book.asks:
            count_both += 1
        elif yes_book and yes_book.asks and (not no_book or not no_book.asks):
            count_no_no += 1
    print('both', count_both, 'no_no', count_no_no, 'total', len(markets))

asyncio.run(f())

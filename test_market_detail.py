import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print(m.question)
    print(m.liquidity)
    yes_id, no_id = m.clob_token_ids
    yes_book = await api.fetch_order_book(yes_id)
    no_book = await api.fetch_order_book(no_id)
    print('yes asks first 3', yes_book.asks[:3])
    print('yes best ask', min(yes_book.asks, key=lambda a: float(a['price'])))
    print('no asks first 3', no_book.asks[:3])
    print('no best ask', min(no_book.asks, key=lambda a: float(a['price'])))

asyncio.run(f())

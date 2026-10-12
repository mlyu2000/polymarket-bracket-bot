import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(1)
    print(m[0].clob_token_ids)
    ob = await api.fetch_order_book(m[0].clob_token_ids[0])
    print(ob.asks[:3])

asyncio.run(f())

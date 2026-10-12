import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api=PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    yes=await api.fetch_order_book(markets[0].clob_token_ids[0])
    for a in yes.asks[:10]:
        print(a)

asyncio.run(f())

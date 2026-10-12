import asyncio
from polymarket_api import PolymarketAPI
async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=2)
    for mk in m:
        print(mk.id, mk.question[:80], mk.liquidity)
asyncio.run(f())

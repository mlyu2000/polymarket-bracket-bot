import asyncio
from polymarket_api import PolymarketAPI
async def f():
    api=PolymarketAPI()
    m=await api.fetch_active_markets(limit=1)
    print(m[0].liquidity, m[0].question[:80])
asyncio.run(f())

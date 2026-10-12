import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api=PolymarketAPI()
    m=await api.fetch_active_markets(limit=500)
    print(len(m))

asyncio.run(f())

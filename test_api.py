import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=2)
    print(len(m))
    print(m[0].question[:100])
    print(m[0].clob_token_ids)

asyncio.run(f())

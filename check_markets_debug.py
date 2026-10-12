import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=5)
    for i in range(len(m)):
        print(m[i].question[:80], m[i].liquidity, m[i].clob_token_ids)

asyncio.run(f())

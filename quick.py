import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    print(len(markets))
    print(markets[0].liquidity, markets[0].clob_token_ids)

asyncio.run(f())

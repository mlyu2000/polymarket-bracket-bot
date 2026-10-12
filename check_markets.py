import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=10)
    for market in m:
        print(market.question[:80], market.liquidity, market.clob_token_ids)

asyncio.run(t())

import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def t():
    Config.validate()
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=1)
    print(m[0].question, m[0].clob_token_ids)

asyncio.run(t())

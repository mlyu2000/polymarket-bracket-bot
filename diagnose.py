import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Fetched {len(markets)} markets")
    for m in markets[:5]:
        print(m.question[:80], m.liquidity, m.clob_token_ids)

asyncio.run(check())

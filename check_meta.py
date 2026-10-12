import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(m.liquidity, m.active, m.closed)

asyncio.run(main())

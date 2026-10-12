import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Markets: {len(markets)}")
    for m in markets[:10]:
        print(m.question[:80], m.liquidity)

asyncio.run(main())

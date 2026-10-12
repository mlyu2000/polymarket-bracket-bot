import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print(f"fetched {len(markets)} markets")
    for m in markets[:10]:
        print(m.question[:60], m.liquidity)
    # check min liquidity
    print("min liquidity", min(m.liquidity for m in markets))
    print("max liquidity", max(m.liquidity for m in markets))

asyncio.run(test())

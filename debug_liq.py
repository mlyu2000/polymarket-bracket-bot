import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def inspect():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=50)
    for m in markets[:10]:
        print(m.question[:80], "liq", m.liquidity, "active", m.active, "closed", m.closed)
    # check liquidity filter
    print("MIN_LIQUIDITY_USDC", Config.MIN_LIQUIDITY_USDC)

asyncio.run(inspect())

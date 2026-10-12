import asyncio
from config import Config
from polymarket_api import PolymarketAPI

Config.SCAN_SORT_BY = 'volume'
Config.MAX_MARKETS_PER_SCAN = 500
Config.MIN_LIQUIDITY_USDC = 100

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets")
    cnt=0
    for m in markets[:50]:
        if m.liquidity < 100:
            continue
        cnt+=1
        print(f"{m.question[:50]} liq {m.liquidity:.0f}")
    print(f"With liq>=100: {cnt}")

asyncio.run(test())

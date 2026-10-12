import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    api = PolymarketAPI()
    # fetch markets sorted by liquidity
    Config.SCAN_SORT_BY = 'liquidity'
    markets = await api.fetch_active_markets(limit=500)
    print('total', len(markets))
    # print first 20 liquidity
    for m in markets[:20]:
        print(m.liquidity, m.question[:60])

asyncio.run(main())

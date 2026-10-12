import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    # use liquidity sort
    from config import Config as C
    orig = C.SCAN_SORT_BY
    C.SCAN_SORT_BY = 'liquidity'
    markets = await api.fetch_active_markets(limit=500)
    print('liquidity sort first 5')
    for m in markets[:5]:
        print(m.question[:60], m.liquidity)
    C.SCAN_SORT_BY = orig

asyncio.run(check())

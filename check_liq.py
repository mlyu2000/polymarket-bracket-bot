import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print('total markets', len(markets))
    low_liq = [m for m in markets if m.liquidity < 1000]
    print('liquidity < 1000', len(low_liq))
    for m in low_liq[:10]:
        print(m.question[:60], m.liquidity)

asyncio.run(f())

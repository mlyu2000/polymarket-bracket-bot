import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"total active markets: {len(markets)}")
    spreads = [m for m in markets if m.question.startswith('Spread:')]
    print(f"'Spread:' markets: {len(spreads)}")
    vik = [m for m in markets if 'Viking' in m.question]
    print(f"'Viking' matches: {len(vik)}")
    for m in spreads[:5]:
        print(f"  {m.question[:60]} | liq={m.liquidity:.0f}")

asyncio.run(check())

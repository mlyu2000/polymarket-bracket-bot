import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Total markets: {len(markets)}")
    # Find first market with liquidity >= 100
    for m in markets:
        if m.liquidity >= Config.MIN_LIQUIDITY_USDC:
            print(f"First market with liquidity >= {Config.MIN_LIQUIDITY_USDC}: {m.liquidity} - {m.question[:60]}")
            break
    # Count how many meet liquidity threshold
    count = sum(1 for m in markets if m.liquidity >= Config.MIN_LIQUIDITY_USDC)
    print(f"Markets with liquidity >= {Config.MIN_LIQUIDITY_USDC}: {count}/{len(markets)}")

asyncio.run(test())

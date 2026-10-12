import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    for m in markets[:10]:
        print(f"{m.liquidity} | {m.question[:60]} | tokens={m.clob_token_ids}")

asyncio.run(test())

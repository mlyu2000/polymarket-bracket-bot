import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=50)
    print(f"markets: {len(markets)}")
    for m in markets:
        print(f"token ids len: {len(m.clob_token_ids)} {m.clob_token_ids}")

asyncio.run(test())

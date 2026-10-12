import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id = m.clob_token_ids[0]
    no_id = m.clob_token_ids[1]
    # raw request
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"https://clob.polymarket.com/book?token_id={yes_id}")
        data = r.json()
    print(data.keys())
    print(data.get('asks')[:5])

asyncio.run(check())

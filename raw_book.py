import asyncio, httpx
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    token = '60006288971625048769132682622303102703569328188109475381665435908288048663307'
    url = f"https://clob.polymarket.com/book?token_id={token}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
        print("keys", data.keys())
        print("asks first 10:", data['asks'][:10])

asyncio.run(check())

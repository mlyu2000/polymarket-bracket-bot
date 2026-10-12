import asyncio
from config import Config
from polymarket_api import PolymarketAPI
import httpx

async def f():
    api = PolymarketAPI()
    url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
    m = data[0]
    print('question', m.get('question'))
    print('outcomes', m.get('outcomes'))
    print('outcomePrices', m.get('outcomePrices'))
    print('clobTokenIds', m.get('clobTokenIds'))
    print('conditionId', m.get('conditionId'))

asyncio.run(f())

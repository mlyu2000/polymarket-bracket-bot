import asyncio, httpx
from config import Config

async def test():
    url = "https://clob.polymarket.com/book?token_id=19039930756738455783103072435880506034204446741177886400889371901235212597751"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
        print("asks first 5:", data['asks'][:5])
        print("bids first 5:", data['bids'][:5])

asyncio.run(test())

import asyncio
import httpx

async def test():
    url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
        m = data[0]
        print(m['id'])
        print(m['clobTokenIds'])
        print(m['conditionId'])

asyncio.run(test())
